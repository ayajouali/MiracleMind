# recommender_enhanced.py
from neo4j_client import run_query
from student_manager_enhanced import student_average_score, get_student
from domain_config import get_domain_info
from typing import List, Dict, Optional
import random
from datetime import datetime, timedelta

def get_student_preferred_domains(student_id: str) -> List[str]:
    """Récupère les domaines préférés de l'étudiant"""
    student = get_student(student_id)
    if student and "preferred_domains" in student:
        return student["preferred_domains"]
    return ["mathematics"]

def get_recently_recommended_concepts(student_id: str, hours: int = 24) -> List[str]:
    """Récupère les concepts récemment recommandés pour éviter les répétitions"""
    res = run_query("""
    MATCH (s:Student {id: $id})
    WHERE s.last_recommended_at IS NOT NULL
    AND duration.between(s.last_recommended_at, datetime()).hours < $hours
    RETURN s.recently_recommended AS concepts
    """, {"id": student_id, "hours": hours}, fetch=True)
    
    if res and res[0].get("concepts"):
        return res[0]["concepts"]
    return []

def update_recommendation_history(student_id: str, concept_name: str):
    """Met à jour l'historique des recommandations"""
    run_query("""
    MATCH (s:Student {id: $id})
    SET s.last_recommended_at = datetime(),
        s.recently_recommended = COALESCE(s.recently_recommended, []) + $concept,
        s.recently_recommended = 
            CASE WHEN size(s.recently_recommended) > 10 
            THEN tail(s.recently_recommended) 
            ELSE s.recently_recommended END
    """, {"id": student_id, "concept": [concept_name]})

def available_concepts_for_student(student_id: str, domain: Optional[str] = None, limit: int = 50) -> List[tuple]:
    """Renvoie les concepts non complétés dont les prérequis sont satisfaits"""
    domain_filter = "AND c.domain = $domain" if domain else ""
    
    # Exclure les concepts récemment recommandés
    recently_recommended = get_recently_recommended_concepts(student_id, hours=2)
    exclude_filter = ""
    if recently_recommended:
        exclude_filter = "AND NOT c.name IN $exclude"
    
    res = run_query(f"""
    MATCH (c:Concept)
    WHERE NOT EXISTS {{
        MATCH (c)-[:REQUIRES]->(p)
        WHERE NOT EXISTS {{
            MATCH (:Student {{id:$id}})-[:COMPLETED]->(p)
        }}
    }}
    AND NOT EXISTS {{ MATCH (:Student {{id:$id}})-[:COMPLETED]->(c) }}
    {domain_filter}
    {exclude_filter}
    RETURN c.name AS name, 
           c.difficulty AS difficulty, 
           c.description AS description,
           c.domain AS domain,
           c.subcategory AS subcategory
    ORDER BY toInteger(c.difficulty) ASC
    LIMIT $limit
    """, {"id": student_id, "limit": limit, "domain": domain, "exclude": recently_recommended}, fetch=True)
    
    result = []
    for r in res:
        name = r["name"]
        try:
            difficulty = int(r.get("difficulty", 1))
        except (ValueError, TypeError):
            difficulty = 1
        description = r.get("description", "")
        domain = r.get("domain", "mathematics")
        subcategory = r.get("subcategory", "")
        result.append((name, difficulty, description, domain, subcategory))
    
    return result

def get_learning_path(student_id: str, domain: str, max_depth: int = 5) -> List[Dict]:
    """Génère un parcours d'apprentissage complet pour un domaine"""
    res = run_query("""
    MATCH path = (start:Concept {domain: $domain})-[:REQUIRES*0..]->(end:Concept)
    WHERE NOT EXISTS {
        MATCH (:Student {id: $id})-[:COMPLETED]->(start)
    }
    AND NOT EXISTS {
        MATCH (start)-[:REQUIRES]->(prereq)
        WHERE NOT EXISTS {
            MATCH (:Student {id: $id})-[:COMPLETED]->(prereq)
        }
    }
    WITH start, length(path) as depth
    WHERE depth <= $max_depth
    RETURN DISTINCT start.name AS name, 
           start.difficulty AS difficulty,
           start.description AS description,
           start.subcategory AS subcategory,
           depth
    ORDER BY depth ASC, start.difficulty ASC
    LIMIT 10
    """, {"id": student_id, "domain": domain, "max_depth": max_depth}, fetch=True)
    
    path = []
    for r in res:
        path.append({
            "concept": r["name"],
            "difficulty": int(r.get("difficulty", 1)),
            "description": r.get("description", ""),
            "subcategory": r.get("subcategory", ""),
            "depth": r.get("depth", 0)
        })
    
    return path

def calculate_concept_score(
    concept: tuple, 
    student_perf: float,
    overload_score: float,
    emotion_label: str,
    preferred_domains: List[str],
    last_domain: Optional[str] = None
) -> float:
    """Calcule un score de recommandation pour un concept avec plus de variété"""
    name, difficulty, description, domain, subcategory = concept
    
    # 1. Score de base basé sur la difficulté adaptée
    target_difficulty = max(1, student_perf * 5)
    
    # Ajuster selon l'émotion
    if emotion_label in ["sadness", "fear", "anger"]:
        target_difficulty = max(1, target_difficulty - 1)  # Plus facile si négatif
    elif emotion_label in ["joy", "surprise"] and student_perf >= 0.7:
        target_difficulty = min(5, target_difficulty + 0.5)  # Plus difficile si positif
    
    diff_score = 1.0 - abs(difficulty - target_difficulty) / 5.0
    diff_score = max(0.0, min(1.0, diff_score))
    
    # 2. Pénalité de surcharge cognitive
    if overload_score > 0.5:
        overload_penalty = overload_score * (difficulty / 5.0) * 0.6
    else:
        overload_penalty = 0.0
    
    # 3. Bonus émotionnel amélioré
    emotion_bonus = 0.0
    if emotion_label in ["joy", "surprise"]:
        if student_perf >= 0.7 and difficulty >= target_difficulty:
            emotion_bonus = 0.15  # Encourager le défi
        else:
            emotion_bonus = 0.05
    elif emotion_label in ["sadness", "fear", "anger"]:
        if difficulty < target_difficulty:
            emotion_bonus = 0.2  # Fortement privilégier le facile
    elif emotion_label == "neutral":
        emotion_bonus = 0.05  # Petit bonus neutre
    
    # 4. Bonus domaine préféré
    domain_bonus = 0.25 if domain in preferred_domains else 0.0
    
    # 5. Bonus de diversité (éviter le même domaine que le dernier)
    diversity_bonus = 0.15 if (last_domain and domain != last_domain) else 0.0
    
    # 6. Facteur aléatoire pour éviter les mêmes recommandations
    random_factor = random.uniform(-0.05, 0.05)
    
    # Score final
    final_score = (
        diff_score 
        - overload_penalty 
        + emotion_bonus 
        + domain_bonus 
        + diversity_bonus 
        + random_factor
    )
    
    return max(0.0, min(1.0, final_score))

def recommend_next(
    student_id: str, 
    emotion_label: Optional[str] = None,
    overloaded_score: float = 0.0,
    preferred_domain: Optional[str] = None,
    diversity: bool = True
) -> Optional[Dict]:
    """Recommande le prochain concept à étudier avec plus de diversité"""
    preferred_domains = get_student_preferred_domains(student_id)
    last_domain = get_last_completed_domain(student_id)
    
    # Récupérer les concepts disponibles
    if preferred_domain:
        avail = available_concepts_for_student(student_id, domain=preferred_domain, limit=100)
    else:
        avail = available_concepts_for_student(student_id, limit=100)
    
    if not avail:
        return None
    
    # Obtenir les performances
    perf_data = student_average_score(student_id)
    perf = perf_data.get("avg_score") if perf_data.get("avg_score") is not None else 0.6
    
    # Appliquer la diversité
    if diversity and last_domain and len(avail) > 5:
        # 70% de chance de recommander un domaine différent
        if random.random() < 0.7:
            different_domain_concepts = [c for c in avail if c[3] != last_domain]
            if different_domain_concepts:
                avail = different_domain_concepts
    
    # Calculer les scores
    scored = []
    for concept in avail:
        score = calculate_concept_score(
            concept,
            perf,
            overloaded_score,
            emotion_label or "neutral",
            preferred_domains,
            last_domain
        )
        scored.append((*concept, score))
    
    # Trier par score
    scored.sort(key=lambda x: (-x[5], random.random()))
    
    if not scored:
        return None
    
    # Sélectionner parmi les 3 meilleurs avec probabilités pondérées
    top_3 = scored[:3]
    weights = [c[5] for c in top_3]
    total_weight = sum(weights)
    
    if total_weight > 0:
        weights = [w/total_weight for w in weights]
        selected = random.choices(top_3, weights=weights, k=1)[0]
    else:
        selected = top_3[0]
    
    # Mettre à jour l'historique
    update_recommendation_history(student_id, selected[0])
    
    domain_info = get_domain_info(selected[3])
    
    return {
        "concept": selected[0],
        "difficulty": selected[1],
        "description": selected[2],
        "domain": selected[3],
        "domain_name": domain_info["name"],
        "domain_icon": domain_info["icon"],
        "subcategory": selected[4],
        "score": selected[5],
        "alternatives": [
            {
                "concept": alt[0],
                "difficulty": alt[1],
                "domain": alt[3],
                "score": alt[5]
            }
            for alt in scored[1:5]
        ],
        "emotion_considered": emotion_label,
        "overload_considered": overloaded_score > 0.5
    }

def get_last_completed_domain(student_id: str) -> Optional[str]:
    """Retourne le domaine du dernier concept complété"""
    res = run_query("""
    MATCH (s:Student {id: $id})-[r:COMPLETED]->(c:Concept)
    RETURN c.domain AS domain
    ORDER BY r.completed_at DESC
    LIMIT 1
    """, {"id": student_id}, fetch=True)
    
    return res[0]["domain"] if res else None

def get_domain_progress(student_id: str, domain: str) -> Dict:
    """Calcule la progression dans un domaine"""
    res = run_query("""
    MATCH (c:Concept {domain: $domain})
    WITH count(c) AS total
    MATCH (s:Student {id: $id})-[r:COMPLETED]->(c2:Concept {domain: $domain})
    RETURN total, count(c2) AS completed, avg(r.score) AS avg_score
    """, {"id": student_id, "domain": domain}, fetch=True)
    
    if not res:
        return {"total": 0, "completed": 0, "progress": 0.0, "avg_score": None}
    
    row = res[0]
    total = row.get("total", 0)
    completed = row.get("completed", 0)
    progress = (completed / total * 100) if total > 0 else 0.0
    
    return {
        "total": total,
        "completed": completed,
        "progress": round(progress, 1),
        "avg_score": row.get("avg_score")
    }

def get_all_domains_progress(student_id: str) -> List[Dict]:
    """Retourne la progression dans tous les domaines"""
    from domain_config import get_all_domains
    
    domains = get_all_domains()
    progress_list = []
    
    for domain_key, domain_info in domains.items():
        progress = get_domain_progress(student_id, domain_key)
        if progress["total"] > 0:
            progress_list.append({
                "domain": domain_key,
                "name": domain_info["name"],
                "icon": domain_info["icon"],
                "color": domain_info["color"],
                **progress
            })
    
    progress_list.sort(key=lambda x: x["progress"], reverse=True)
    
    return progress_list