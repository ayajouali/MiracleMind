# student_manager_enhanced.py
from neo4j_client import run_query
from typing import Dict, List, Optional

def get_student(student_id: str) -> Optional[Dict]:
    """Récupère les informations complètes d'un étudiant"""
    res = run_query("""
    MATCH (s:Student {id:$id})
    OPTIONAL MATCH (s)-[r:COMPLETED]->(c:Concept)
    RETURN s {.*} AS student,
           collect({concept: c.name, score: r.score, time_spent: r.time_spent_minutes}) AS completions
    """, {"id": student_id}, fetch=True)
    if not res:
        return None
    row = res[0]
    student = row.get("student", {})
    student["completions"] = row.get("completions", [])
    return student

def create_or_update_student(student_id: str, name: str, preferred_domains: List[str] = None):
    if preferred_domains is None:
        preferred_domains = ["mathematics"]
    run_query("""
    MERGE (s:Student {id:$id})
    SET s.name = $name, 
        s.preferred_domains = $domains,
        s.updated_at = datetime()
    """, {"id": student_id, "name": name, "domains": preferred_domains})

def update_emotional_state(student_id: str, emotion_label: str, emotion_score: float, sentiment_label: Optional[str] = None):
    run_query("""
    MATCH (s:Student {id:$id})
    SET s.last_emotion = $emotion_label,
        s.last_emotion_score = $emotion_score,
        s.last_sentiment = $sentiment_label,
        s.last_update = datetime()
    """, {
        "id": student_id,
        "emotion_label": emotion_label,
        "emotion_score": float(emotion_score),
        "sentiment_label": sentiment_label
    })

def record_completion(student_id: str, concept_name: str, score: float, time_spent_minutes: Optional[int] = None):
    """Enregistre la complétion d'un concept"""
    run_query("""
    MATCH (s:Student {id:$id}), (c:Concept {name:$name})
    MERGE (s)-[r:COMPLETED]->(c)
    SET r.score = $score,
        r.completed_at = datetime(),
        r.time_spent_minutes = $time_spent,
        r.attempts = COALESCE(r.attempts, 0) + 1
    """, {
        "id": student_id,
        "name": concept_name,
        "score": float(score),
        "time_spent": time_spent_minutes
    })

def student_average_score(student_id: str) -> Dict:
    res = run_query("""
    MATCH (:Student {id:$id})-[r:COMPLETED]->(c:Concept)
    RETURN avg(r.score) AS avg_score,
           count(r) AS completed_count,
           sum(r.time_spent_minutes) AS total_time
    """, {"id": student_id}, fetch=True)
    if not res:
        return {"avg_score": None, "completed_count": 0, "total_time": 0}
    row = res[0]
    return {
        "avg_score": row.get("avg_score"),
        "completed_count": row.get("completed_count", 0),
        "total_time": row.get("total_time", 0)
    }
