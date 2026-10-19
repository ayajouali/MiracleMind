
Adaptive Learning System avec LangChain + GPT-2 (100% Gratuit)
✨ Nouvelles Fonctionnalités v2.1
🤖 Plans d'étude générés par IA (GPT-2 + LangChain)
📊 Visualisations interactives du parcours d'apprentissage
💡 Conseils de révision personnalisés selon l'état émotionnel
🎯 Génération automatique de quiz
📈 Timeline visuelle des étapes d'apprentissage
🎨 Graphiques radar de progression par sujet
📋 Prérequis
Neo4j installé et en cours d'exécution
Python 3.8+
Environnement virtuel recommandé
⚙️ Installation
1. Installer les dépendances
pip install -r requirements.txt
Note: Le premier chargement téléchargera GPT-2 (~500MB) automatiquement.

2. Configurer Neo4j
Modifier .env si nécessaire :

NEO4J_URI=neo4j://127.0.0.1:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=miraclemind123
HF_DEVICE=cpu  # ou "cuda" si vous avez un GPU
3. Initialiser la base de données
python populate_graph_enhanced.py
Cela créera :

8 domaines d'apprentissage
~80 concepts interconnectés
2 étudiants de démonstration
🚀 Lancement
Option 1 : API + Interface Web (Recommandé)
Terminal 1 - Lancer l'API :

python api_enhanced.py
L'API sera disponible sur http://localhost:8000

Terminal 2 - Lancer Streamlit :

streamlit run streamlit_app_enhanced.py
L'interface sera disponible sur http://localhost:8501

Option 2 : API uniquement
python api_enhanced.py
Documentation interactive : http://localhost:8000/docs

🎯 Utilisation
1. Via l'interface Streamlit
Sélectionner un étudiant (ou en créer un nouveau)
Onglet "Recommandations" :
Décrire votre état émotionnel
Cocher "Générer plan IA"
Cliquer sur "Obtenir ma Recommandation"
Visualiser le plan généré :
Timeline interactive des étapes
Graphique radar des sujets
Exercices pratiques
Ressources recommandées
Quiz de révision
2. Via l'API
Obtenir une recommandation avec plan :

curl -X POST "http://localhost:8000/recommend_next" \
  -H "Content-Type: application/json" \
  -d '{
    "student_id": "student_1",
    "text": "Je me sens motivé et prêt à apprendre !",
    "diversity": true,
    "generate_plan": true
  }'
Réponse :

{
  "recommendation": {
    "concept": "Linear Equations",
    "difficulty": 2,
    "description": "Solving ax + b = c",
    "domain": "mathematics"
  },
  "learning_content": {
    "study_plan": {
      "overview": "...",
      "key_topics": [...],
      "learning_steps": [...],
      "practice_exercises": [...],
      "resources": [...],
      "time_allocation": "5-10 hours"
    },
    "revision_tips": {...},
    "quiz": [...]
  }
}
📊 Visualisations Disponibles
1. Timeline d'Apprentissage
Diagramme de Gantt interactif montrant les étapes progressives.

2. Graphique Radar
Visualisation de la couverture des sujets clés.

3. Répartition du Temps
Graphique circulaire de l'allocation du temps par étape.

4. Graphe de Concepts
Réseau interactif montrant les dépendances entre concepts.

🤖 Fonctionnement de l'IA
LangChain + GPT-2
Le système utilise GPT-2 (modèle open-source de 124M paramètres) via LangChain pour :

Analyser le concept à apprendre
Prendre en compte :
Difficulté du concept
État émotionnel de l'étudiant
Performances passées
Domaine d'étude
Générer automatiquement :
Plan d'étude structuré
Conseils de révision personnalisés
Questions de quiz
100% Gratuit : Aucune API payante, tout s'exécute en local !

🎨 Personnalisation
Modifier les prompts GPT-2
Éditer langchain_gpt2.py :

STUDY_PLAN_TEMPLATE = """
Créez un plan pour: {concept_name}
...
Votre prompt personnalisé ici
"""
Ajouter de nouveaux domaines
Éditer domain_config.py :

DOMAINS = {
    "votre_domaine": {
        "name": "Votre Domaine",
        "color": "#HEXCOLOR",
        "icon": "🎯",
        "subcategories": [...]
    }
}
📝 Endpoints API Principaux
Endpoint	Méthode	Description
/recommend_next	POST	Recommandation + Plan IA
/generate_study_plan	POST	Plan d'étude uniquement
/complete_concept	POST	Marquer un concept complété
/progress/{student_id}	GET	Progression globale
/graph_data	GET	Données du graphe
/health	GET	État du système
🐛 Dépannage
GPT-2 trop lent ?
Réduire max_new_tokens dans langchain_gpt2.py
Utiliser un GPU si disponible (modifier HF_DEVICE=cuda dans .env)
Plans générés de mauvaise qualité ?
Ajuster temperature et top_p dans langchain_gpt2.py
Améliorer les prompts dans les templates
Erreur Neo4j ?
# Vérifier que Neo4j est démarré
neo4j status

# Redémarrer si nécessaire
neo4j restart
🔧 Architecture
┌─────────────────┐
│   Streamlit UI  │  ← Interface utilisateur
└────────┬────────┘
         │
         v
┌─────────────────┐
│   FastAPI API   │  ← Logique métier
└────────┬────────┘
         │
    ┌────┴────┐
    │         │
    v         v
┌──────┐  ┌──────────┐
│Neo4j │  │GPT-2 + LC│  ← Stockage + IA
└──────┘  └──────────┘
📚 Documentation Complète
API Docs : http://localhost:8000/docs
Streamlit : http://localhost:8501
Neo4j Browser : http://localhost:7474
🎓 Exemples d'Usage
Étudiant motivé
"Je me sens super motivé aujourd'hui ! 
Je veux apprendre quelque chose de challengeant !"
→ Recommande un concept difficile + plan intensif

Étudiant fatigué
"Je suis un peu fatigué, j'ai du mal à me concentrer..."
→ Recommande un concept facile + sessions courtes

Diversité
Cocher "Varier les domaines"
→ Alterne entre différents domaines pour éviter la monotonie

🚀 Prochaines Étapes
Compléter vos premiers concepts
Explorer les différents domaines
Générer des plans d'étude personnalisés
Suivre votre progression dans le graphe
Bon apprentissage ! 🎓
