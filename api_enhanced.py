# api_enhanced.py
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List
from hf_models import detect_emotion, detect_sentiment, detect_cognitive_overload
from student_manager_enhanced import update_emotional_state, student_average_score, record_completion, get_student
from recommender_enhanced import (
    recommend_next, 
    get_learning_path, 
    get_domain_progress,
    get_all_domains_progress,
    available_concepts_for_student
)
from domain_config import get_all_domains
from neo4j_client import run_query
from langchain_gpt2 import generate_complete_learning_content, generate_study_plan
import uvicorn
import traceback

app = FastAPI(
    title="Adaptive Learning System API",
    description="Multi-domain intelligent learning recommendation system with AI-powered study plans",
    version="2.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# FONCTION HELPER POUR PRÉREQUIS
def get_concept_prerequisites(concept_name: str) -> list:
    """Récupère les prérequis d'un concept depuis Neo4j"""
    try:
        res = run_query("""
        MATCH (c:Concept {name: $name})-[:REQUIRES]->(p:Concept)
        RETURN p.name AS prereq
        """, {"name": concept_name}, fetch=True)
        
        return [r["prereq"] for r in res] if res else []
    except Exception as e:
        print(f"Erreur récupération prérequis: {e}")
        return []

# MODÈLES PYDANTIC
class TextPayload(BaseModel):
    student_id: str
    text: str

class RecommendPayload(BaseModel):
    student_id: str
    text: str
    preferred_domain: Optional[str] = None
    diversity: bool = False
    generate_plan: bool = True

class CompletePayload(BaseModel):
    student_id: str
    concept_name: str
    score: float = Field(ge=0.0, le=1.0)
    time_spent_minutes: Optional[int] = None

class StudentCreate(BaseModel):
    student_id: str
    name: str
    preferred_domains: List[str] = ["mathematics"]

class StudyPlanRequest(BaseModel):
    concept_name: str
    description: str
    difficulty: int
    domain: str
    student_id: Optional[str] = None

# ENDPOINTS
@app.post("/detect_state", tags=["Analysis"])
def detect_state(payload: TextPayload):
    """Analyse l'état émotionnel et cognitif"""
    try:
        emo = detect_emotion(payload.text)
        sent = detect_sentiment(payload.text)
        perf = student_average_score(payload.student_id)
        overload = detect_cognitive_overload(payload.text, recent_activity=perf)
        
        update_emotional_state(
            payload.student_id, 
            emo["label"], 
            emo.get("score", 0.0), 
            sentiment_label=sent.get("label")
        )
        
        return {
            "emotion": emo,
            "sentiment": sent,
            "overload": overload,
            "performance": perf
        }
    except Exception as e:
        print(f"Error in detect_state: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/recommend_next", tags=["Recommendations"])
def api_recommend(payload: RecommendPayload):
    """Recommande le prochain concept avec plan d'étude"""
    try:
        emo = detect_emotion(payload.text)
        perf = student_average_score(payload.student_id)
        overload = detect_cognitive_overload(payload.text, recent_activity=perf)
        
        rec = recommend_next(
            payload.student_id,
            emotion_label=emo["label"],
            overloaded_score=overload["score"],
            preferred_domain=payload.preferred_domain,
            diversity=payload.diversity
        )
        
        if not rec:
            raise HTTPException(
                status_code=404, 
                detail="No concept found. All concepts may be completed or prerequisites not met."
            )
        
        from strategy import generate_study_strategy
        strat = generate_study_strategy(
            emo["label"],
            emo.get("score", 0.0),
            overload["score"],
            perf.get("avg_score"),
            rec["difficulty"]
        )
        
        # Génération du contenu avec prérequis
        learning_content = None
        if payload.generate_plan:
            try:
                performance = perf.get("avg_score") if perf.get("avg_score") else 0.75
                
                # NOUVEAU: Récupérer les prérequis
                prereqs = get_concept_prerequisites(rec["concept"])
                
                learning_content = generate_complete_learning_content(
                    concept_name=rec["concept"],
                    description=rec["description"],
                    difficulty=rec["difficulty"],
                    domain=rec["domain"],
                    emotion=emo["label"],
                    performance=performance,
                    prerequisites=prereqs
                )
            except Exception as e:
                print(f"Warning: Could not generate learning content: {e}")
                traceback.print_exc()
                learning_content = None
        
        return {
            "recommendation": rec,
            "strategy": strat,
            "emotion": emo,
            "overload": overload,
            "performance": perf,
            "learning_content": learning_content
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in api_recommend: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")

@app.post("/generate_study_plan", tags=["Learning Content"])
def api_generate_study_plan(payload: StudyPlanRequest):
    """Génère un plan d'étude détaillé pour un concept"""
    try:
        performance = 0.75
        if payload.student_id:
            perf = student_average_score(payload.student_id)
            performance = perf.get("avg_score") if perf.get("avg_score") else 0.75
        
        plan = generate_study_plan(
            concept_name=payload.concept_name,
            description=payload.description,
            difficulty=payload.difficulty,
            domain=payload.domain,
            student_performance=performance
        )
        
        return {
            "concept": payload.concept_name,
            "plan": plan
        }
    except Exception as e:
        print(f"Error in api_generate_study_plan: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/learning_path/{student_id}/{domain}", tags=["Recommendations"])
def get_path(student_id: str, domain: str, max_depth: int = Query(5, ge=1, le=10)):
    """Génère un parcours d'apprentissage"""
    try:
        path = get_learning_path(student_id, domain, max_depth)
        return {"student_id": student_id, "domain": domain, "path": path}
    except Exception as e:
        print(f"Error in get_path: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/available_concepts/{student_id}", tags=["Recommendations"])
def get_available_concepts(
    student_id: str, 
    domain: Optional[str] = None,
    limit: int = Query(20, ge=1, le=100)
):
    """Retourne tous les concepts disponibles"""
    try:
        concepts = available_concepts_for_student(student_id, domain, limit)
        return {
            "student_id": student_id,
            "domain": domain,
            "count": len(concepts),
            "concepts": [
                {
                    "name": c[0],
                    "difficulty": c[1],
                    "description": c[2],
                    "domain": c[3],
                    "subcategory": c[4]
                }
                for c in concepts
            ]
        }
    except Exception as e:
        print(f"Error in get_available_concepts: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/complete_concept", tags=["Progress"])
def complete_concept(payload: CompletePayload):
    """Marque un concept comme complété"""
    try:
        record_completion(
            payload.student_id,
            payload.concept_name,
            payload.score,
            payload.time_spent_minutes
        )
        return {
            "status": "success",
            "message": f"Concept '{payload.concept_name}' marked as completed"
        }
    except Exception as e:
        print(f"Error in complete_concept: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/progress/{student_id}", tags=["Progress"])
def get_progress(student_id: str):
    """Retourne la progression globale"""
    try:
        progress = get_all_domains_progress(student_id)
        perf = student_average_score(student_id)
        
        return {
            "student_id": student_id,
            "overall_performance": perf,
            "domains": progress
        }
    except Exception as e:
        print(f"Error in get_progress: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/progress/{student_id}/{domain}", tags=["Progress"])
def get_domain_progress_endpoint(student_id: str, domain: str):
    """Retourne la progression dans un domaine"""
    try:
        progress = get_domain_progress(student_id, domain)
        return {
            "student_id": student_id,
            "domain": domain,
            **progress
        }
    except Exception as e:
        print(f"Error in get_domain_progress_endpoint: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/students", tags=["Students"])
def create_student(student: StudentCreate):
    """Crée un nouveau profil étudiant"""
    try:
        from populate_graph_enhanced import create_student
        create_student(student.student_id, student.name, student.preferred_domains)
        return {
            "status": "success",
            "message": f"Student '{student.name}' created successfully",
            "student_id": student.student_id
        }
    except Exception as e:
        print(f"Error in create_student: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/students/{student_id}", tags=["Students"])
def get_student_info(student_id: str):
    """Récupère les informations d'un étudiant"""
    try:
        student = get_student(student_id)
        if not student:
            raise HTTPException(status_code=404, detail="Student not found")
        
        perf = student_average_score(student_id)
        progress = get_all_domains_progress(student_id)
        
        return {
            "student": student,
            "performance": perf,
            "domains_progress": progress
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in get_student_info: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/domains", tags=["Domains"])
def list_domains():
    """Liste tous les domaines disponibles"""
    try:
        domains = get_all_domains()
        return {"domains": domains}
    except Exception as e:
        print(f"Error in list_domains: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/graph_data", tags=["Visualization"])
def get_graph_data():
    """Retourne les données du graphe en JSON pour visualisation"""
    try:
        nodes = run_query("""
            MATCH (c:Concept)
            RETURN c.name AS id, 
                   c.name AS label,
                   c.description AS description, 
                   c.difficulty AS difficulty,
                   c.domain AS domain,
                   c.subcategory AS subcategory
        """, fetch=True)
        
        edges = run_query("""
            MATCH (a:Concept)-[:REQUIRES]->(b:Concept) 
            RETURN a.name AS source, b.name AS target
        """, fetch=True)
        
        return {
            "nodes": nodes,
            "edges": edges
        }
    except Exception as e:
        print(f"Error in get_graph_data: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/", tags=["Info"])
def root():
    """Point d'entrée de l'API"""
    return {
        "message": "Adaptive Learning System API with AI Study Plans",
        "version": "2.1.0",
        "status": "running",
        "docs": "/docs",
        "features": [
            "Multi-domain learning",
            "Emotional state detection",
            "Cognitive overload analysis",
            "Intelligent recommendations",
            "AI-powered study plans (GPT-2 + LangChain)",
            "Interactive roadmaps",
            "QCM quiz generation",
            "Learning path generation",
            "Progress tracking"
        ]
    }

@app.get("/health", tags=["Info"])
def health_check():
    """Vérifie l'état de santé de l'API"""
    try:
        run_query("RETURN 1", fetch=True)
        neo4j_status = "healthy"
    except:
        neo4j_status = "unhealthy"
    
    return {
        "status": "healthy" if neo4j_status == "healthy" else "degraded",
        "neo4j": neo4j_status,
        "langchain": "enabled",
        "gpt2": "loaded",
        "version": "2.1.0"
    }

if __name__ == "__main__":
    uvicorn.run(
        "api_enhanced:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )