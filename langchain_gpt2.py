# langchain_gpt2.py – VERSION CORRIGÉE (Cache par concept + émotion)

"""
Module de génération de contenu éducatif avec LangChain et GPT-2
VERSION CORRIGÉE: Cache intelligent par concept ET contexte émotionnel
"""

try:
    from langchain_huggingface import HuggingFacePipeline
    print("✓ Utilisation de langchain_huggingface")
except ImportError:
    try:
        from langchain_community.llms import HuggingFacePipeline
        print("✓ Utilisation de langchain.llms")
    except ImportError:
        print("✗ ERREUR: Installez langchain-huggingface")
        raise

from langchain_core.prompts import PromptTemplate
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
import torch
import os
from dotenv import load_dotenv
from functools import lru_cache
import hashlib
import json

load_dotenv()

DEVICE = 0 if os.getenv("HF_DEVICE") == "cuda" else -1
MODEL_NAME = "gpt2"

print(f"🔧 Chargement de GPT-2 sur {'GPU' if DEVICE == 0 else 'CPU'}...")

tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForCausalLM.from_pretrained(MODEL_NAME)

pipe = pipeline(
    "text-generation",
    model=model,
    tokenizer=tokenizer,
    max_new_tokens=200,
    temperature=0.7,
    top_p=0.9,
    repetition_penalty=1.2,
    device=DEVICE,
    do_sample=True,
    pad_token_id=tokenizer.eos_token_id
)

llm = HuggingFacePipeline(pipeline=pipe)

print("✅ GPT-2 chargé avec succès!")

# ======================================
# CACHE AMÉLIORÉ
# ======================================

_generation_cache = {}

def get_cache_key(concept_name: str, content_type: str, **kwargs) -> str:
    """Génère une clé de cache unique incluant le contexte"""
    # Inclure les paramètres contextuels dans la clé
    context_parts = [concept_name, content_type]
    
    # Ajouter l'émotion si présente
    if 'emotion' in kwargs:
        context_parts.append(f"emo_{kwargs['emotion']}")
    
    # Ajouter la performance si présente
    if 'performance' in kwargs:
        perf_bucket = int(kwargs['performance'] * 10) / 10  # Arrondir à 0.1
        context_parts.append(f"perf_{perf_bucket}")
    
    key_str = "_".join(str(p) for p in context_parts)
    return hashlib.md5(key_str.encode()).hexdigest()

def get_from_cache(cache_key: str):
    """Récupère du cache"""
    return _generation_cache.get(cache_key)

def save_to_cache(cache_key: str, data):
    """Sauvegarde dans le cache (limite à 100 entrées)"""
    if len(_generation_cache) > 100:
        # Supprimer les 20 entrées les plus anciennes
        oldest_keys = list(_generation_cache.keys())[:20]
        for key in oldest_keys:
            del _generation_cache[key]
    
    _generation_cache[cache_key] = data

# ======================================
# TEMPLATES AMÉLIORÉS
# ======================================

STUDY_PLAN_TEMPLATE = """Create a study plan for: {concept_name}

Description: {description}
Difficulty: {difficulty}/5
Domain: {domain}
Student performance level: {performance}

Provide:
1. Overview (2-3 sentences)
2. Key topics (3-5 specific items)
3. Learning steps (5-6 progressive steps)
4. Time estimation

Plan:"""

QUIZ_TEMPLATE_IMPROVED = """Generate 3 unique MCQ questions about: {concept_name}

Description: {description}
Difficulty level: {difficulty}/5
Domain: {domain}

Requirements:
- Questions must be specific to {concept_name}
- Include 4 options (A, B, C, D)
- Mark the correct answer
- Vary question types (definition, application, analysis)

Format:
Q1: [Specific question about {concept_name}]
A) [Option] B) [Option] C) [Option] D) [Option]
Correct: [A/B/C/D]
Explanation: [Why this is correct]

Questions:"""

REVISION_TIPS_TEMPLATE = """Provide study tips for: {concept_name}

Difficulty: {difficulty}/5
Student emotion: {emotion}
Performance level: {performance}

Give personalized advice considering:
- Current emotional state: {emotion}
- Difficulty level: {difficulty}/5
- Recommended study approach
- Time management tips
- Motivation strategies

Tips:"""

# ======================================
# GENERATE STUDY PLAN (Amélioré)
# ======================================

def generate_study_plan(
    concept_name: str,
    description: str,
    difficulty: int,
    domain: str,
    student_performance: float = 0.75
) -> dict:
    
    # Vérifier le cache avec performance incluse
    cache_key = get_cache_key(concept_name, "study_plan", performance=student_performance)
    cached = get_from_cache(cache_key)
    if cached:
        print(f"⚡ Cache hit pour study_plan: {concept_name}")
        return cached
    
    try:
        # Ajuster la performance pour le prompt
        if student_performance >= 0.8:
            perf_text = "high (80%+)"
        elif student_performance >= 0.6:
            perf_text = "medium (60-80%)"
        else:
            perf_text = "developing (below 60%)"
        
        prompt = PromptTemplate(
            input_variables=["concept_name", "description", "difficulty", "domain", "performance"],
            template=STUDY_PLAN_TEMPLATE
        )

        chain = prompt | llm

        result = chain.invoke({
            "concept_name": concept_name,
            "description": description,
            "difficulty": difficulty,
            "domain": domain,
            "performance": perf_text
        })

        plan = parse_study_plan(result)
        plan["raw_output"] = result

        # Sauvegarder dans le cache
        save_to_cache(cache_key, plan)

        return plan

    except Exception as e:
        print(f"⚠️ Erreur génération plan: {e}")
        return get_fallback_study_plan(concept_name, difficulty)


def parse_study_plan(text: str) -> dict:
    lines = [l.strip() for l in text.split('\n') if l.strip()]

    plan = {
        "overview": "",
        "key_topics": [],
        "learning_steps": [],
        "practice_exercises": [],
        "resources": [],
        "time_allocation": "4-8 hours"
    }

    current_section = None

    for line in lines:
        lower_line = line.lower()

        if "overview" in lower_line or "introduction" in lower_line:
            current_section = "overview"
        elif "key topic" in lower_line or "main topic" in lower_line or "topics" in lower_line:
            current_section = "key_topics"
        elif "learning step" in lower_line or "steps" in lower_line:
            current_section = "learning_steps"
        elif "practice" in lower_line or "exercise" in lower_line:
            current_section = "practice_exercises"
        elif "resource" in lower_line:
            current_section = "resources"
        elif "time" in lower_line or "hours" in lower_line:
            current_section = "time_allocation"
        elif current_section and line:
            if current_section == "overview":
                plan["overview"] += line + " "
            elif current_section == "time_allocation":
                plan["time_allocation"] = line
            elif isinstance(plan[current_section], list):
                cleaned = line.lstrip('•-*0123456789.). ')
                if cleaned and len(cleaned) > 3:
                    plan[current_section].append(cleaned)

    plan["overview"] = plan["overview"].strip()

    if not plan["overview"] or len(plan["key_topics"]) == 0:
        return get_fallback_study_plan("Concept", 3)

    return plan


def get_fallback_study_plan(concept_name: str, difficulty: int) -> dict:
    return {
        "overview": f"Ce plan vous guidera dans l'apprentissage de {concept_name}. "
                   f"Le niveau de difficulté est de {difficulty}/5.",
        "key_topics": [
            f"Introduction à {concept_name}",
            "Concepts fondamentaux",
            "Applications pratiques",
            "Exercices et révision"
        ],
        "learning_steps": [
            "Lire la théorie de base",
            "Voir des exemples concrets",
            "Pratiquer avec des exercices",
            "Réviser et consolider",
            "Auto-évaluation"
        ],
        "practice_exercises": [
            "QCM de compréhension",
            "Exercices d'application",
            "Projet pratique"
        ],
        "resources": [
            "Documentation officielle",
            "Tutoriels en ligne",
            "Exercices interactifs"
        ],
        "time_allocation": f"{3 + difficulty} à {5 + difficulty * 2} heures"
    }

# ======================================
# REVISION TIPS (Amélioré)
# ======================================

def generate_revision_tips(
    concept_name: str,
    emotion: str,
    difficulty: int,
    performance: float = 0.75
) -> dict:
    
    # Cache avec émotion ET performance
    cache_key = get_cache_key(concept_name, "tips", emotion=emotion, performance=performance)
    cached = get_from_cache(cache_key)
    if cached:
        print(f"⚡ Cache hit pour tips: {concept_name} ({emotion})")
        return cached
    
    # Utiliser le fallback amélioré
    tips_data = get_fallback_tips(emotion, difficulty, concept_name, performance)
    
    # Sauvegarder dans le cache
    save_to_cache(cache_key, tips_data)
    
    return tips_data


def get_fallback_tips(emotion: str, difficulty: int, concept_name: str = "ce concept", performance: float = 0.75) -> dict:
    # Conseils adaptés à l'émotion
    tips_by_emotion = {
        "joy": f"✨ Ton énergie positive est un atout ! Profite de cet état pour explorer {concept_name} en profondeur. Challenge-toi avec des exercices avancés.",
        "sadness": f"💙 Prends le temps qu'il faut. Commence par de petites étapes avec {concept_name}. Chaque progrès compte, même minime.",
        "anger": f"🔥 Canalise cette énergie ! Fixe-toi des objectifs clairs pour maîtriser {concept_name}. Les pauses sont importantes.",
        "fear": f"🤗 C'est normal d'être anxieux. Décompose {concept_name} en petites parties. Tu es capable !",
        "surprise": f"🎯 Excellente curiosité ! Explore {concept_name} avec cette ouverture d'esprit. Pose-toi des questions.",
        "neutral": f"📚 Concentre-toi sur les fondamentaux de {concept_name}. Travaille de façon méthodique et régulière."
    }
    
    # Conseils selon difficulté
    difficulty_tips = {
        1: "Ce concept est accessible. 20-30 minutes par session suffisent.",
        2: "Niveau intermédiaire. Prévois 30-45 minutes par session.",
        3: "Concept modéré. Sessions de 45-60 minutes recommandées.",
        4: "Concept avancé. Prévois 60-90 minutes avec des pauses.",
        5: "Niveau expert. Sessions courtes mais fréquentes (30-45 min)."
    }
    
    # Conseils selon performance
    if performance >= 0.8:
        perf_advice = "• Tu as d'excellentes performances ! N'hésite pas à aller plus loin et explorer des aspects avancés."
    elif performance >= 0.6:
        perf_advice = "• Tes performances sont bonnes. Continue ce rythme et renforce tes bases."
    else:
        perf_advice = "• Prends le temps de bien consolider chaque étape avant d'avancer. La patience est clé."
    
    base_tip = tips_by_emotion.get(emotion, tips_by_emotion["neutral"])
    diff_tip = difficulty_tips.get(difficulty, difficulty_tips[3])
    
    strategies = [
        "• Méthode Pomodoro : 25 min de travail, 5 min de pause",
        "• Révision espacée : revoir après 1h, 1 jour, 1 semaine",
        "• Technique Feynman : expliquer le concept à voix haute",
        perf_advice
    ]
    
    mistakes = [
        "• Ne pas bachoter la veille (inefficace à long terme)",
        "• Éviter de relire passivement, pratiquer activement",
        "• Ne pas sauter les exercices pratiques"
    ]
    
    tips = f"""
**💡 Conseils Personnalisés**

{base_tip}

**📊 Selon la difficulté ({difficulty}/5) :**
{diff_tip}

**✅ Stratégies Efficaces :**
{chr(10).join(strategies)}

**❌ Erreurs à Éviter :**
{chr(10).join(mistakes)}

**🧠 Technique Mnémotechnique :**
• Créez des acronymes avec les concepts clés
• Utilisez des associations visuelles
• Enseignez à quelqu'un d'autre
    """
    
    return {
        "tips": tips,
        "emotion_adapted": emotion
    }

# ======================================
# QUIZ GENERATION (Amélioré - Sans Cache)
# ======================================

def generate_quiz_questions(
    concept_name: str,
    description: str,
    difficulty: int,
    domain: str = "general"
) -> list:
    
    # PAS DE CACHE pour les quiz - générer à chaque fois
    print(f"🎯 Génération de quiz unique pour: {concept_name}")
    
    try:
        prompt = PromptTemplate(
            input_variables=["concept_name", "description", "difficulty", "domain"],
            template=QUIZ_TEMPLATE_IMPROVED
        )

        chain = prompt | llm

        result = chain.invoke({
            "concept_name": concept_name,
            "description": description,
            "difficulty": difficulty,
            "domain": domain
        })

        questions = parse_quiz_improved(result)

        if len(questions) < 2:
            questions = generate_intelligent_fallback_quiz(
                concept_name, description, difficulty, domain)
        
        # Limiter à 5 questions
        questions = questions[:5]
        
        # NE PAS SAUVEGARDER dans le cache

        return questions

    except Exception as e:
        print(f"⚠️ Erreur quiz: {e}")
        return generate_intelligent_fallback_quiz(
            concept_name, description, difficulty, domain)


def parse_quiz_improved(text: str) -> list:
    questions = []
    lines = text.split('\n')

    current_q = None
    current_options = []
    current_correct = None
    current_explanation = None

    for line in lines:
        line = line.strip()

        if any(marker in line.upper() for marker in ["Q1:", "Q2:", "Q3:", "Q4:", "Q5:"]):
            if current_q and len(current_options) >= 2:
                questions.append({
                    "question": current_q,
                    "options": current_options[:4],
                    "correct": current_correct or "A",
                    "explanation": current_explanation or "Concept clé"
                })

            current_q = line.split(":", 1)[-1].strip()
            current_options = []
            current_correct = None
            current_explanation = None

        elif line.startswith(("A)", "B)", "C)", "D)")):
            current_options.append(line[2:].strip())

        elif "CORRECT" in line.upper():
            for letter in ["A", "B", "C", "D"]:
                if letter in line.upper():
                    current_correct = letter

        elif "EXPLANATION" in line.upper():
            current_explanation = line.split(":", 1)[-1].strip()

    if current_q and len(current_options) >= 2:
        questions.append({
            "question": current_q,
            "options": current_options[:4],
            "correct": current_correct or "A",
            "explanation": current_explanation or "Explication du concept"
        })

    return questions


def generate_intelligent_fallback_quiz(concept_name, description, difficulty, domain):
    """Génère un quiz de secours SPÉCIFIQUE au concept"""
    
    quiz = [
        {
            "question": f"Quel est le principe fondamental de {concept_name} ?",
            "options": [
                description[:100] if len(description) > 100 else description,
                "Une théorie non prouvée",
                "Un concept obsolète",
                "Aucune des réponses"
            ],
            "correct": "A",
            "explanation": f"{concept_name} se base sur: {description}"
        },
        {
            "question": f"Dans quel contexte {concept_name} est-il le plus utilisé ?",
            "options": [
                f"Dans le domaine de {domain.replace('_', ' ')}",
                "Uniquement en théorie pure",
                "Dans tous les domaines de manière égale",
                "Ce n'est plus utilisé aujourd'hui"
            ],
            "correct": "A",
            "explanation": f"{concept_name} est principalement appliqué en {domain}"
        },
        {
            "question": f"Quelle est la meilleure approche pour maîtriser {concept_name} ?",
            "options": [
                "Pratiquer régulièrement avec des exercices progressifs",
                "Mémoriser la définition uniquement",
                "Attendre de tout comprendre avant de pratiquer",
                "Étudier seulement la théorie"
            ],
            "correct": "A",
            "explanation": "La pratique régulière est essentielle pour tout apprentissage"
        }
    ]
    
    # Ajouter des questions selon la difficulté
    if difficulty >= 3:
        quiz.append({
            "question": f"Quelle erreur commune faut-il éviter avec {concept_name} ?",
            "options": [
                "Vouloir aller trop vite sans consolider les bases",
                "Prendre son temps pour bien comprendre",
                "Faire des exercices variés",
                "Demander de l'aide quand nécessaire"
            ],
            "correct": "A",
            "explanation": "Il faut toujours consolider les bases avant d'avancer"
        })
    
    return quiz

# ======================================
# ROADMAP (Version rapide)
# ======================================

def generate_concept_roadmap(
    concept_name: str,
    description: str,
    difficulty: int,
    prerequisites: list = None
) -> dict:

    if prerequisites is None:
        prerequisites = []

    roadmap = {
        "concept": concept_name,
        "difficulty": difficulty,
        "steps": [],
        "total_estimated_hours": 3 + difficulty * 2
    }

    if prerequisites:
        roadmap["steps"].append({
            "phase": "Prérequis",
            "duration": "30-60 min",
            "tasks": [f"Réviser: {p}" for p in prerequisites[:3]],
            "status": "prerequisite"
        })

    roadmap["steps"].append({
        "phase": "Introduction",
        "duration": "30 min",
        "tasks": [
            f"Comprendre la définition de {concept_name}",
            "Voir des exemples simples",
            "Identifier les cas d'usage"
        ],
        "status": "introduction"
    })

    roadmap["steps"].append({
        "phase": "Théorie",
        "duration": "1h",
        "tasks": [
            "Étudier les concepts de base",
            "Apprendre le vocabulaire clé",
            "Comprendre les principes fondamentaux"
        ],
        "status": "theory"
    })

    roadmap["steps"].append({
        "phase": "Pratique de Base",
        "duration": "1h",
        "tasks": [
            "Exercices guidés niveau débutant",
            "Exemples corrigés pas à pas",
            "Quiz d'auto-évaluation"
        ],
        "status": "practice_basic"
    })

    if difficulty >= 3:
        roadmap["steps"].append({
            "phase": "Pratique Avancée",
            "duration": "1h30",
            "tasks": [
                "Exercices complexes",
                "Problèmes ouverts",
                "Optimisation et variantes"
            ],
            "status": "practice_advanced"
        })

    roadmap["steps"].append({
        "phase": "Projet d'Application",
        "duration": "2h",
        "tasks": [
            f"Créer un mini-projet utilisant {concept_name}",
            "Tester différentes approches",
            "Documenter votre travail"
        ],
        "status": "project"
    })

    roadmap["steps"].append({
        "phase": "Évaluation",
        "duration": "30 min",
        "tasks": [
            "Quiz final",
            "Auto-évaluation des compétences",
            "Identification des points à améliorer"
        ],
        "status": "assessment"
    })

    return roadmap

# ======================================
# FULL CONTENT GENERATION (Amélioré)
# ======================================

def generate_complete_learning_content(
    concept_name: str,
    description: str,
    difficulty: int,
    domain: str,
    emotion: str = "neutral",
    performance: float = 0.75,
    prerequisites: list = None
) -> dict:

    print(f"🤖 Génération contenu pour: {concept_name} (émotion: {emotion}, perf: {performance:.2f})")

    return {
        "study_plan": generate_study_plan(
            concept_name, description, difficulty, domain, performance
        ),
        "revision_tips": generate_revision_tips(
            concept_name, emotion, difficulty, performance
        ),
        "quiz": generate_quiz_questions(
            concept_name, description, difficulty, domain
        ),
        "roadmap": generate_concept_roadmap(
            concept_name, description, difficulty, prerequisites
        )
    }