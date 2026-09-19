# streamlit_app_enhanced.py
import streamlit as st
import requests
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import networkx as nx
from roadmap_visualizer import visualize_concept_roadmap, visualize_quiz_interactive

API_BASE = "http://127.0.0.1:8000"

st.set_page_config(
    layout="wide",
    page_title="Miracle Mind",
    page_icon="🎓",
    initial_sidebar_state="expanded"
)

# Initialiser session_state pour persister les recommandations
if 'current_recommendation' not in st.session_state:
    st.session_state.current_recommendation = None
if 'recommendation_timestamp' not in st.session_state:
    st.session_state.recommendation_timestamp = None

# CSS personnalisé
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        padding: 1rem 0;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 10px;
        text-align: center;
    }
    .emotion-badge {
        display: inline-block;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-weight: bold;
        margin: 0.5rem;
    }
    .study-step {
        background: #f8f9fa;
        padding: 1rem;
        margin: 0.5rem 0;
        border-left: 4px solid #667eea;
        border-radius: 5px;
    }
    .resource-card {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        color: white;
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

def call_api(endpoint, method="GET", data=None, timeout=60):
    """Appelle l'API avec timeout augmenté"""
    try:
        url = f"{API_BASE}{endpoint}"
        if method == "GET":
            response = requests.get(url, timeout=timeout)
        elif method == "POST":
            response = requests.post(url, json=data, timeout=timeout)
        
        response.raise_for_status()
        return response.json()
    except requests.exceptions.ConnectionError:
        st.error("✗ L'API n'est pas démarrée. Lance: `python api_enhanced.py`")
        return None
    except requests.exceptions.Timeout:
        st.error(f"✗ L'API met trop de temps à répondre (timeout: {timeout}s). Réessaye avec 'Génération simplifiée'")
        return None
    except Exception as e:
        st.error(f"✗ Erreur: {str(e)}")
        return None

def get_emotion_emoji(emotion):
    """Retourne un emoji pour chaque émotion"""
    emojis = {
        "joy": "😊", "sadness": "😢", "anger": "😠",
        "fear": "😰", "surprise": "😲", "neutral": "😐",
        "disgust": "🤢"
    }
    return emojis.get(emotion, "😐")

def get_emotion_color(emotion):
    """Retourne une couleur pour chaque émotion"""
    colors = {
        "joy": "#10B981", "sadness": "#3B82F6", "anger": "#EF4444",
        "fear": "#F59E0B", "surprise": "#8B5CF6", "neutral": "#6B7280",
        "disgust": "#059669"
    }
    return colors.get(emotion, "#6B7280")

def visualize_study_plan(plan_data):
    """Visualise le plan d'étude avec des graphiques interactifs"""
    if not plan_data or "study_plan" not in plan_data:
        st.warning("Aucun plan d'étude disponible")
        return
    
    plan = plan_data["study_plan"]
    
    # 1. Vue d'ensemble
    st.markdown("### 📋 Vue d'ensemble")
    st.info(plan.get("overview", "Plan d'étude généré automatiquement"))
    
    # 2. Timeline des étapes d'apprentissage
    if plan.get("learning_steps"):
        st.markdown("### 📊 Parcours d'Apprentissage")
        
        steps = plan["learning_steps"]
        fig = go.Figure()
        
        for idx, step in enumerate(steps):
            fig.add_trace(go.Bar(
                name=f"Étape {idx+1}",
                x=[1],
                y=[step[:50] + "..." if len(step) > 50 else step],
                orientation='h',
                marker=dict(
                    color=f'rgba(102, 126, 234, {0.3 + (idx / len(steps)) * 0.7})',
                    line=dict(color='rgb(102, 126, 234)', width=2)
                ),
                hoverinfo='text',
                hovertext=step
            ))
        
        fig.update_layout(
            title="Étapes progressives d'apprentissage",
            xaxis_title="Progression",
            showlegend=False,
            height=400,
            barmode='stack'
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        with st.expander("📝 Détail des étapes"):
            for idx, step in enumerate(steps):
                st.markdown(f"""
                <div class="study-step">
                    <strong>Étape {idx + 1}:</strong> {step}
                </div>
                """, unsafe_allow_html=True)
    
    # 3. Sujets clés avec graphique radar
    if plan.get("key_topics"):
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.markdown("### 🎯 Sujets Clés")
            for idx, topic in enumerate(plan["key_topics"]):
                st.markdown(f"**{idx + 1}.** {topic}")
        
        with col2:
            topics = plan["key_topics"][:6]
            
            fig = go.Figure()
            
            fig.add_trace(go.Scatterpolar(
                r=[100] * len(topics),
                theta=[f"Sujet {i+1}" for i in range(len(topics))],
                fill='toself',
                name='Objectif',
                line_color='rgba(102, 126, 234, 0.3)'
            ))
            
            fig.add_trace(go.Scatterpolar(
                r=[0] * len(topics),
                theta=[f"Sujet {i+1}" for i in range(len(topics))],
                fill='toself',
                name='Progression actuelle',
                line_color='rgb(102, 126, 234)'
            ))
            
            fig.update_layout(
                polar=dict(
                    radialaxis=dict(visible=True, range=[0, 100])
                ),
                showlegend=True,
                title="Couverture des sujets",
                height=350
            )
            
            st.plotly_chart(fig, use_container_width=True)
    
    # 4. Exercices pratiques
    if plan.get("practice_exercises"):
        st.markdown("### 💪 Exercices Pratiques")
        
        exercises = plan["practice_exercises"]
        cols = st.columns(min(3, len(exercises)))
        
        for idx, exercise in enumerate(exercises):
            with cols[idx % 3]:
                st.markdown(f"""
                <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                     color: white; padding: 1rem; border-radius: 8px; margin: 0.5rem 0;">
                    <strong>📝 Exercice {idx + 1}</strong><br>
                    {exercise}
                </div>
                """, unsafe_allow_html=True)
    
    # 5. Ressources recommandées
    if plan.get("resources"):
        st.markdown("### 📚 Ressources Recommandées")
        
        for idx, resource in enumerate(plan["resources"]):
            st.markdown(f"""
            <div class="resource-card">
                <strong>🔗 Ressource {idx + 1}:</strong> {resource}
            </div>
            """, unsafe_allow_html=True)
    
    # 6. Allocation du temps
    if plan.get("time_allocation"):
        st.markdown("### ⏱️ Temps Estimé")
        
        time_str = plan["time_allocation"]
        st.success(f"**Durée totale recommandée:** {time_str}")
        
        if plan.get("learning_steps"):
            fig = go.Figure(data=[go.Pie(
                labels=[f"Étape {i+1}" for i in range(len(plan["learning_steps"]))],
                values=[1] * len(plan["learning_steps"]),
                hole=.3
            )])
            
            fig.update_layout(
                title="Répartition du temps par étape",
                height=300
            )
            
            st.plotly_chart(fig, use_container_width=True)

def visualize_revision_tips(tips_data):
    """Affiche les conseils de révision"""
    if not tips_data or "revision_tips" not in tips_data:
        return
    
    tips = tips_data["revision_tips"]
    
    st.markdown("### 💡 Conseils de Révision Personnalisés")
    
    emotion = tips.get("emotion_adapted", "neutral")
    emotion_color = get_emotion_color(emotion)
    
    st.markdown(f"""
    <div style="background: {emotion_color}; color: white; padding: 1rem; 
         border-radius: 10px; margin: 1rem 0;">
        {get_emotion_emoji(emotion)} <strong>Adapté à votre état émotionnel: {emotion.title()}</strong>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown(tips.get("tips", ""))

def visualize_graph(graph_data):
    """Crée une visualisation interactive du graphe de concepts"""
    if not graph_data:
        st.error("Impossible de charger le graphe")
        return
    
    nodes = graph_data.get("nodes", [])
    edges = graph_data.get("edges", [])
    
    if not nodes:
        st.warning("Aucun concept trouvé dans le graphe")
        return
    
    G = nx.DiGraph()
    
    domain_colors = {
        "mathematics": "#3B82F6",
        "physics": "#10B981",
        "computer_science": "#8B5CF6",
        "chemistry": "#F59E0B",
        "biology": "#059669",
        "languages": "#EC4899",
        "history": "#EF4444",
        "engineering": "#6366F1"
    }
    
    for node in nodes:
        G.add_node(
            node['id'],
            label=node['label'],
            domain=node.get('domain', 'unknown'),
            difficulty=node.get('difficulty', 1),
            description=node.get('description', '')
        )
    
    for edge in edges:
        G.add_edge(edge['source'], edge['target'])
    
    pos = nx.spring_layout(G, k=1, iterations=50)
    
    edge_trace = go.Scatter(
        x=[], y=[],
        line=dict(width=1, color='#888'),
        hoverinfo='none',
        mode='lines'
    )
    
    for edge in G.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_trace['x'] += tuple([x0, x1, None])
        edge_trace['y'] += tuple([y0, y1, None])
    
    node_trace = go.Scatter(
        x=[], y=[], text=[], mode='markers+text',
        hoverinfo='text',
        marker=dict(showscale=False, colorscale='YlGnBu', size=[], color=[], line_width=2),
        textposition="top center"
    )
    
    for node in G.nodes():
        x, y = pos[node]
        node_trace['x'] += tuple([x])
        node_trace['y'] += tuple([y])
        
        node_data = G.nodes[node]
        domain = node_data.get('domain', 'unknown')
        difficulty = node_data.get('difficulty', 1)
        
        label = node_data.get('label', node)
        short_label = label[:15] + '...' if len(label) > 15 else label
        node_trace['text'] += tuple([short_label])
        
        color = domain_colors.get(domain, '#999')
        node_trace['marker']['color'] += tuple([color])
        
        size = 20 + (difficulty * 5)
        node_trace['marker']['size'] += tuple([size])
    
    fig = go.Figure(
        data=[edge_trace, node_trace],
        layout=go.Layout(
            title=dict(
                text="Graphe des Concepts d'Apprentissage",
                font=dict(size=20)
            ),
            showlegend=False,
            hovermode="closest",
            margin=dict(b=0, l=0, r=0, t=40),
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            height=700,
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)"
        )
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("### 🎨 Légende des Domaines")
    cols = st.columns(4)
    domains_resp = call_api("/domains")
    if domains_resp:
        for idx, (key, info) in enumerate(domains_resp["domains"].items()):
            with cols[idx % 4]:
                st.markdown(
                    f'<div style="background-color: {info["color"]}; '
                    f'padding: 10px; border-radius: 5px; text-align: center; '
                    f'color: white; margin: 5px;">{info["icon"]} {info["name"]}</div>',
                    unsafe_allow_html=True
                )

# SIDEBAR
with st.sidebar:
    st.markdown("### 👤 Profil Étudiant")
    student_mode = st.radio("Mode", ["Étudiant existant", "Nouvel étudiant"])
    
    if student_mode == "Étudiant existant":
        student_id = st.text_input("Student ID", "student_1")
    else:
        with st.form("create_student"):
            new_id = st.text_input("ID")
            new_name = st.text_input("Nom")
            
            domains_resp = call_api("/domains")
            if domains_resp:
                domain_names = [v["name"] for v in domains_resp["domains"].values()]
                selected_domains = st.multiselect("Domaines préférés", domain_names)
                
                if st.form_submit_button("Créer"):
                    domain_keys = [k for k, v in domains_resp["domains"].items() 
                                 if v["name"] in selected_domains]
                    
                    result = call_api("/students", "POST", {
                        "student_id": new_id,
                        "name": new_name,
                        "preferred_domains": domain_keys
                    })
                    if result:
                        st.success(f"✅ Étudiant créé: {new_name}")
                        student_id = new_id
    
    st.divider()
    
    if 'student_id' in locals():
        student_info = call_api(f"/students/{student_id}")
        if student_info:
            st.markdown(f"**Nom:** {student_info['student'].get('name', 'N/A')}")
            perf = student_info['performance']
            if perf.get('avg_score') is not None:
                score_pct = perf['avg_score'] * 100
                st.metric("Score Moyen", f"{score_pct:.1f}%")
                st.metric("Concepts Complétés", perf.get('completed_count', 0))

# HEADER
st.markdown('<h1 class="main-header">🎓 Miracle Mind</h1>', unsafe_allow_html=True)
st.markdown("_Powered by GPT-2 + LangChain 🤖_")
st.markdown("---")

# ONGLETS
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Dashboard",
    "🎯 Recommandations",
    "✅ Compléter un Concept",
    "📈 Progression",
    "🌐 Graphe de Concepts"
])

# TAB 1: DASHBOARD
with tab1:
    if 'student_id' in locals():
        col1, col2, col3 = st.columns(3)
        
        progress_data = call_api(f"/progress/{student_id}")
        if progress_data:
            perf = progress_data['overall_performance']
            
            with col1:
                st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                st.metric("Score Global", f"{perf.get('avg_score', 0)*100:.1f}%" if perf.get('avg_score') else "N/A")
                st.markdown('</div>', unsafe_allow_html=True)
            
            with col2:
                st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                st.metric("Concepts Complétés", perf.get('completed_count', 0))
                st.markdown('</div>', unsafe_allow_html=True)
            
            with col3:
                domains_count = len([d for d in progress_data['domains'] if d['completed'] > 0])
                st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                st.metric("Domaines Actifs", domains_count)
                st.markdown('</div>', unsafe_allow_html=True)
            
            st.markdown("### 📚 Progression par Domaine")
            
            if progress_data['domains']:
                fig = go.Figure()
                
                domains = progress_data['domains']
                names = [f"{d['icon']} {d['name']}" for d in domains if d['total'] > 0]
                values = [d['completed'] for d in domains if d['total'] > 0]
                colors = [d['color'] for d in domains if d['total'] > 0]
                
                fig.add_trace(go.Pie(
                    labels=names,
                    values=values,
                    marker=dict(colors=colors),
                    textinfo='label+percent'
                ))
                
                fig.update_layout(title="Distribution des Concepts Complétés", height=400)
                st.plotly_chart(fig, use_container_width=True)

# TAB 2: RECOMMANDATIONS AVEC PLAN (VERSION CORRIGÉE)
with tab2:
    if 'student_id' in locals():
        st.markdown("### 💭 Comment te sens-tu aujourd'hui?")
        
        # Si une recommandation existe déjà, afficher un bouton pour la voir
        if st.session_state.current_recommendation:
            col1, col2 = st.columns([3, 1])
            with col1:
                st.info("📌 Une recommandation est déjà chargée")
            with col2:
                if st.button("🔄 Nouvelle Recommandation"):
                    st.session_state.current_recommendation = None
                    st.session_state.recommendation_timestamp = None
                    st.rerun()
        
        # Formulaire de demande de recommandation
        if not st.session_state.current_recommendation:
            text = st.text_area(
                "Décris ton état d'esprit",
                height=150,
                placeholder="Ex: Je me sens motivé et prêt à relever un défi ! / Je suis un peu fatigué aujourd'hui..."
            )
            
            col1, col2 = st.columns([3, 1])
            with col1:
                diversity = st.checkbox("Varier les domaines", value=True)
            
            with col2:
                generate_plan = st.checkbox("Générer plan IA", value=True, 
                                           help="Utilise GPT-2 pour créer un plan détaillé")
            
            if st.button("🎯 Obtenir ma Recommandation", type="primary"):
                if not text.strip():
                    st.warning("⚠️ Écris quelque chose d'abord!")
                else:
                    with st.spinner("🤖 Analyse en cours... Cela peut prendre 30-60 secondes..."):
                        result = call_api("/recommend_next", "POST", {
                            "student_id": student_id,
                            "text": text,
                            "diversity": diversity,
                            "generate_plan": generate_plan
                        }, timeout=90)  # Timeout augmenté à 90s
                    
                    if result:
                        # Sauvegarder la recommandation dans session_state
                        st.session_state.current_recommendation = result
                        st.session_state.recommendation_timestamp = datetime.now()
                        st.rerun()
        
        # Afficher la recommandation si elle existe
        if st.session_state.current_recommendation:
            result = st.session_state.current_recommendation
            
            emo = result['emotion']
            emotion_color = get_emotion_color(emo['label'])
            
            st.markdown(f"""
            <div class="emotion-badge" style="background-color: {emotion_color};">
                {get_emotion_emoji(emo['label'])} {emo['label'].title()} 
                ({emo.get('score', 0)*100:.0f}%)
            </div>
            """, unsafe_allow_html=True)
            
            rec = result['recommendation']
            st.markdown(f"### {rec['domain_icon']} Concept Recommandé: **{rec['concept']}**")
            st.markdown(f"**Domaine:** {rec['domain_name']}")
            st.markdown(f"**Difficulté:** {'⭐' * rec['difficulty']}")
            st.info(f"📖 {rec['description']}")
            
            strat = result['strategy']
            st.success(f"⏱️ Session recommandée: {strat['session_duration_min']} min | ☕ Pause toutes les {strat['break_every_min']} min")
            st.markdown(f"**Conseil:** {strat['advice']}")
            
            # Tabs pour le contenu
            if result.get('learning_content'):
                st.markdown("---")
                st.markdown("## 🤖 Plan d'Étude Généré par IA")
                
                tabs = st.tabs([
                    "🗺️ Roadmap", 
                    "📋 Plan Détaillé", 
                    "💡 Conseils", 
                    "🎯 Quiz Interactif"
                ])
                
                # TAB 0: ROADMAP
                with tabs[0]:
                    visualize_concept_roadmap(
                        result['learning_content'].get('roadmap'),
                        concept_info={
                            'name': rec['concept'],
                            'difficulty': rec['difficulty'],
                            'domain': rec['domain']
                        }
                    )
                
                # TAB 1: Plan détaillé
                with tabs[1]:
                    visualize_study_plan(result['learning_content'])
                
                # TAB 2: Conseils
                with tabs[2]:
                    visualize_revision_tips(result['learning_content'])
                
                # TAB 3: QUIZ INTERACTIF
                with tabs[3]:
                    visualize_quiz_interactive(result['learning_content'])
            
            # Alternatives
            if rec.get('alternatives'):
                with st.expander("🔄 Voir les alternatives"):
                    for alt in rec['alternatives']:
                        st.markdown(f"- **{alt['concept']}** ({'⭐' * alt['difficulty']}) - {alt['domain']}")

# TAB 3: COMPLÉTER
with tab3:
    if 'student_id' in locals():
        st.markdown("### ✅ Marquer un Concept comme Complété")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            domains_resp = call_api("/domains")
            if domains_resp:
                domain_options = {
                    f"{v['icon']} {v['name']}": k 
                    for k, v in domains_resp["domains"].items()
                }
                domain_options["Tous les domaines"] = None
                
                selected_label = st.selectbox("Filtrer par domaine", list(domain_options.keys()))
                selected_domain = domain_options[selected_label]
        
        if selected_domain:
            concepts_data = call_api(f"/available_concepts/{student_id}?domain={selected_domain}&limit=50")
        else:
            concepts_data = call_api(f"/available_concepts/{student_id}?limit=50")
        
        if concepts_data and concepts_data.get('concepts'):
            concepts = concepts_data['concepts']
            
            concept_options = {
                f"{c['name']} ({'⭐' * c['difficulty']}) - {c['domain']}": c['name']
                for c in concepts
            }
            
            st.markdown(f"**{len(concepts)} concepts disponibles**")
            
            with st.form("complete_concept_form"):
                selected_concept_label = st.selectbox(
                    "Sélectionne le concept que tu as complété",
                    list(concept_options.keys())
                )
                
                selected_concept = concept_options[selected_concept_label]
                concept_info = next(c for c in concepts if c['name'] == selected_concept)
                st.info(f"📖 {concept_info['description']}")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    score = st.slider("Score (0-100%)", 0, 100, 75, 5)
                
                with col2:
                    time_spent = st.number_input("Temps passé (minutes)", 1, 300, 30, 5)
                
                submitted = st.form_submit_button("✅ Marquer comme Complété", type="primary")
                
                if submitted:
                    result = call_api("/complete_concept", "POST", {
                        "student_id": student_id,
                        "concept_name": selected_concept,
                        "score": score / 100.0,
                        "time_spent_minutes": time_spent
                    })
                    
                    if result:
                        st.success(f"🎉 Bravo! Concept '{selected_concept}' complété avec {score}%!")
                        st.balloons()
                        # Invalider la recommandation actuelle
                        st.session_state.current_recommendation = None
                        st.rerun()
        else:
            st.info("🎓 Félicitations! Tu as complété tous les concepts disponibles pour le moment.")

# TAB 4: PROGRESSION
with tab4:
    if 'student_id' in locals():
        progress_data = call_api(f"/progress/{student_id}")
        
        if progress_data:
            st.markdown("### 📈 Progression Détaillée")
            
            for domain in progress_data['domains']:
                if domain['total'] > 0:
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.markdown(f"**{domain['icon']} {domain['name']}**")
                        st.progress(domain['progress'] / 100)
                    with col2:
                        st.metric("Progression", f"{domain['progress']:.1f}%")
                    
                    st.markdown(f"_{domain['completed']} / {domain['total']} concepts complétés_")
                    st.divider()

# TAB 5: GRAPHE
with tab5:
    st.markdown("### 🌐 Graphe de Concepts")
    st.markdown("Visualisation interactive des concepts et de leurs dépendances")
    
    if st.button("🔄 Charger le Graphe", type="primary"):
        with st.spinner("Chargement du graphe..."):
            graph_data = call_api("/graph_data")
            if graph_data:
                visualize_graph(graph_data)

st.markdown("---")
st.markdown("Made with ❤️ | Adaptive Learning System v2.1 | Powered by GPT-2 + LangChain 🤖")
