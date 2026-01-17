# roadmap_visualizer.py - VERSION CORRIGÉE (Quiz toujours unique)
"""
Module de visualisation de roadmap et quiz interactifs
CORRECTION: Chaque quiz a maintenant un ID unique basé sur le timestamp
"""

import plotly.graph_objects as go
import streamlit as st
import networkx as nx
import time
import hashlib

def visualize_concept_roadmap(roadmap_data, concept_info=None):
    """Visualise la roadmap d'apprentissage d'un concept sous forme de graphe"""
    if not roadmap_data or "steps" not in roadmap_data:
        st.warning("Aucune roadmap disponible")
        return
    
    st.markdown(f"### 🗺️ Roadmap d'Apprentissage")
    
    if concept_info:
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Concept", concept_info.get("name", "N/A"))
        with col2:
            st.metric("Difficulté", "⭐" * roadmap_data.get("difficulty", 1))
        with col3:
            st.metric("Durée Estimée", f"{roadmap_data.get('total_estimated_hours', 0)}h")
    
    st.markdown("#### 📊 Parcours d'Apprentissage")
    
    steps = roadmap_data["steps"]
    G = nx.DiGraph()
    
    phase_colors = {
        "prerequisite": "#F59E0B",
        "introduction": "#3B82F6",
        "theory": "#8B5CF6",
        "practice_basic": "#10B981",
        "practice_advanced": "#059669",
        "project": "#EC4899",
        "assessment": "#EF4444"
    }
    
    for i, step in enumerate(steps):
        G.add_node(
            i,
            label=step["phase"],
            duration=step["duration"],
            tasks=step.get("tasks", []),
            status=step.get("status", "unknown"),
            color=phase_colors.get(step.get("status", "unknown"), "#6B7280")
        )
    
    for i in range(len(steps) - 1):
        G.add_edge(i, i + 1)
    
    pos = {}
    for i in range(len(steps)):
        pos[i] = (0, -i * 2)
    
    edge_trace = go.Scatter(
        x=[], y=[],
        line=dict(width=3, color='#CBD5E0'),
        hoverinfo='none',
        mode='lines',
        showlegend=False
    )
    
    for edge in G.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_trace['x'] += tuple([x0, x1, None])
        edge_trace['y'] += tuple([y0, y1, None])
    
    node_trace = go.Scatter(
        x=[], y=[],
        mode='markers+text',
        hoverinfo='text',
        text=[],
        textposition="middle right",
        textfont=dict(size=12, color="white", family="Arial Black"),
        marker=dict(
            size=[],
            color=[],
            line=dict(width=3, color='white'),
            symbol='circle'
        ),
        showlegend=False
    )
    
    hover_texts = []
    
    for node in G.nodes():
        x, y = pos[node]
        node_data = G.nodes[node]
        
        node_trace['x'] += tuple([x])
        node_trace['y'] += tuple([y])
        node_trace['text'] += tuple([f"  {node + 1}  "])
        
        color = node_data['color']
        node_trace['marker']['color'] += tuple([color])
        node_trace['marker']['size'] += tuple([50])
        
        tasks_text = "<br>".join([f"  • {task}" for task in node_data['tasks'][:3]])
        hover_text = (
            f"<b>Étape {node + 1}: {node_data['label']}</b><br>"
            f"⏱️ Durée: {node_data['duration']}<br>"
            f"<br><b>Tâches:</b><br>{tasks_text}"
        )
        if len(node_data['tasks']) > 3:
            hover_text += f"<br>  ... et {len(node_data['tasks']) - 3} autres"
        
        hover_texts.append(hover_text)
    
    node_trace['hovertext'] = hover_texts
    node_trace['hoverinfo'] = 'text'
    
    annotations = []
    for node in G.nodes():
        x, y = pos[node]
        node_data = G.nodes[node]
        
        annotations.append(
            dict(
                x=x + 0.3,
                y=y,
                xref='x',
                yref='y',
                text=f"<b>{node_data['label']}</b><br>{node_data['duration']}",
                showarrow=False,
                xanchor='left',
                font=dict(size=13, color='#1F2937'),
                bgcolor='rgba(255, 255, 255, 0.9)',
                bordercolor=node_data['color'],
                borderwidth=2,
                borderpad=8
            )
        )
    
    fig = go.Figure(
        data=[edge_trace, node_trace],
        layout=go.Layout(
            title=dict(
                text=f"Parcours d'Apprentissage: {roadmap_data.get('concept', 'Concept')}",
                font=dict(size=18, color='#1F2937')
            ),
            showlegend=False,
            hovermode='closest',
            margin=dict(b=20, l=20, r=300, t=60),
            annotations=annotations,
            xaxis=dict(
                showgrid=False,
                zeroline=False,
                showticklabels=False,
                range=[-0.5, 1.5]
            ),
            yaxis=dict(
                showgrid=False,
                zeroline=False,
                showticklabels=False
            ),
            height=150 * len(steps),
            plot_bgcolor='rgba(249, 250, 251, 1)',
            paper_bgcolor='rgba(249, 250, 251, 1)'
        )
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("#### ✅ Détail des Étapes")
    
    for i, step in enumerate(steps):
        with st.expander(f"**Étape {i + 1}: {step['phase']}** ({step['duration']})", expanded=(i == 0)):
            st.markdown(f"**🎯 Objectifs:**")
            
            for j, task in enumerate(step.get('tasks', [])):
                col1, col2 = st.columns([0.05, 0.95])
                with col1:
                    st.checkbox("", key=f"task_{i}_{j}", label_visibility="collapsed")
                with col2:
                    st.markdown(f"{task}")
            
            if step.get('status') == 'prerequisite':
                st.info("💡 **Conseil**: Assure-toi de bien maîtriser ces concepts avant de continuer.")
            elif step.get('status') == 'practice_basic':
                st.success("💪 **Conseil**: La pratique régulière est essentielle à cette étape.")
            elif step.get('status') == 'project':
                st.warning("🚀 **Conseil**: C'est le moment de mettre en pratique tout ce que tu as appris!")
            elif step.get('status') == 'assessment':
                st.error("📝 **Conseil**: Sois honnête dans ton auto-évaluation pour identifier tes lacunes.")
    
    st.markdown("#### 📅 Timeline du Parcours")
    
    gantt_data = []
    
    for i, step in enumerate(steps):
        duration_str = step['duration']
        
        if 'min' in duration_str:
            if '-' in duration_str:
                values = [int(x) for x in duration_str.replace('min', '').split('-')]
                hours = sum(values) / len(values) / 60
            else:
                hours = int(duration_str.replace('min', '').strip()) / 60
        elif 'h' in duration_str:
            hours = float(duration_str.replace('h', '').strip())
        else:
            hours = 1
        
        gantt_data.append({
            'Task': step['phase'],
            'Duration': hours
        })
    
    fig_gantt = go.Figure()
    
    for i, item in enumerate(gantt_data):
        fig_gantt.add_trace(go.Bar(
            name=item['Task'],
            x=[item['Duration']],
            y=[item['Task']],
            orientation='h',
            marker=dict(
                color=phase_colors.get(steps[i].get('status', 'unknown'), '#6B7280'),
                line=dict(color='white', width=2)
            ),
            text=f"{item['Duration']:.1f}h",
            textposition='inside',
            hovertemplate=f"<b>{item['Task']}</b><br>Durée: {item['Duration']:.1f}h<extra></extra>"
        ))
    
    fig_gantt.update_layout(
        title="Répartition du Temps par Étape",
        xaxis_title="Heures",
        yaxis_title="",
        showlegend=False,
        height=400,
        barmode='stack',
        plot_bgcolor='rgba(249, 250, 251, 1)'
    )
    
    st.plotly_chart(fig_gantt, use_container_width=True)
    
    st.markdown("#### 📊 Statistiques du Parcours")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Étapes", len(steps))
    
    with col2:
        total_tasks = sum(len(step.get('tasks', [])) for step in steps)
        st.metric("Total Tâches", total_tasks)
    
    with col3:
        st.metric("Durée Totale", f"{roadmap_data.get('total_estimated_hours', 0)}h")
    
    with col4:
        avg_time_per_step = roadmap_data.get('total_estimated_hours', 0) / len(steps) if steps else 0
        st.metric("Temps Moyen/Étape", f"{avg_time_per_step:.1f}h")


def visualize_quiz_interactive(quiz_data):
    """
    Affiche le quiz de manière interactive avec QCM
    CORRECTION MAJEURE: Utilise un ID unique basé sur le timestamp de génération
    """
    if not quiz_data or "quiz" not in quiz_data:
        return
    
    quiz = quiz_data["quiz"]
    
    if not quiz:
        return
    
    st.markdown("### 🎯 Quiz de Révision Interactif")
    
    # 🔧 CORRECTION: Créer un ID unique basé sur le timestamp actuel
    # Cela force Streamlit à traiter chaque quiz comme nouveau
    if 'quiz_generation_time' not in st.session_state:
        st.session_state.quiz_generation_time = time.time()
    
    # Générer une clé unique qui change à chaque nouvelle recommandation
    quiz_unique_id = hashlib.md5(f"{st.session_state.quiz_generation_time}_{str(quiz)}".encode()).hexdigest()[:12]
    quiz_key = f"quiz_{quiz_unique_id}"
    
    # Initialiser le state pour CE quiz spécifique
    if f'{quiz_key}_score' not in st.session_state:
        st.session_state[f'{quiz_key}_score'] = 0
        st.session_state[f'{quiz_key}_answered'] = []
        st.session_state[f'{quiz_key}_user_answers'] = {}
    
    # Afficher info sur la génération
    col1, col2 = st.columns([4, 1])
    with col1:
        st.info(f"🆕 Quiz généré spécialement pour ce concept")
    with col2:
        if st.button("🔄 Nouveau Quiz", key=f"regenerate_{quiz_key}"):
            # Réinitialiser le timestamp pour forcer un nouveau quiz
            st.session_state.quiz_generation_time = time.time()
            st.session_state.current_recommendation = None
            st.rerun()
    
    for idx, q in enumerate(quiz):
        st.markdown(f"#### Question {idx + 1}")
        st.markdown(f"**{q['question']}**")
        
        if 'options' in q and len(q['options']) > 0:
            options = q['options']
            
            is_answered = idx in st.session_state[f'{quiz_key}_answered']
            
            default_index = None
            if f"quiz_q_{idx}_{quiz_key}" in st.session_state[f'{quiz_key}_user_answers']:
                prev_answer = st.session_state[f'{quiz_key}_user_answers'][f"quiz_q_{idx}_{quiz_key}"]
                if prev_answer in ['A', 'B', 'C', 'D'][:len(options)]:
                    default_index = ['A', 'B', 'C', 'D'].index(prev_answer)
            
            user_answer = st.radio(
                "Choisissez votre réponse:",
                options=['A', 'B', 'C', 'D'][:len(options)],
                format_func=lambda x: f"{x}) {options[ord(x) - ord('A')]}",
                key=f"quiz_q_{idx}_{quiz_key}",
                index=default_index,
                disabled=is_answered
            )
            
            if user_answer:
                st.session_state[f'{quiz_key}_user_answers'][f"quiz_q_{idx}_{quiz_key}"] = user_answer
            
            col1, col2 = st.columns([1, 4])
            with col1:
                if is_answered:
                    correct = q.get('correct', 'A')
                    prev_answer = st.session_state[f'{quiz_key}_user_answers'].get(f"quiz_q_{idx}_{quiz_key}")
                    if prev_answer == correct:
                        st.success("✅ Correct!")
                    else:
                        st.error(f"❌ Incorrect")
                    
                    with col2:
                        explanation = q.get('explanation', 'Pas d\'explication disponible')
                        st.info(f"💡 **Explication**: {explanation}")
                else:
                    if st.button("Vérifier", key=f"check_{idx}_{quiz_key}", disabled=not user_answer):
                        if user_answer:
                            correct = q.get('correct', 'A')
                            
                            st.session_state[f'{quiz_key}_answered'].append(idx)
                            
                            if user_answer == correct:
                                st.session_state[f'{quiz_key}_score'] += 1
                                st.success("✅ Correct!")
                            else:
                                st.error(f"❌ Incorrect. La bonne réponse est {correct}")
                            
                            with col2:
                                explanation = q.get('explanation', 'Pas d\'explication disponible')
                                st.info(f"💡 **Explication**: {explanation}")
                            
                            st.rerun()
        
        else:
            st.text_area("Votre réponse:", key=f"open_q_{idx}_{quiz_key}", height=100)
            
            with st.expander("Voir la réponse"):
                st.markdown(f"**Réponse**: {q.get('answer', 'N/A')}")
        
        st.markdown("---")
    
    if st.session_state[f'{quiz_key}_answered']:
        score_pct = (st.session_state[f'{quiz_key}_score'] / len(quiz)) * 100
        
        st.markdown("### 📊 Votre Score")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Questions Répondues", f"{len(st.session_state[f'{quiz_key}_answered'])}/{len(quiz)}")
        
        with col2:
            st.metric("Score", f"{st.session_state[f'{quiz_key}_score']}/{len(quiz)}")
        
        with col3:
            st.metric("Pourcentage", f"{score_pct:.0f}%")
        
        if score_pct >= 80:
            st.success("🎉 Excellent! Tu maîtrises bien le concept!")
        elif score_pct >= 60:
            st.info("👍 Bien! Continue à pratiquer pour parfaire ta compréhension.")
        else:
            st.warning("💪 Continue tes efforts! Révise les points difficiles.")
        
        if st.button("🔄 Recommencer le Quiz", key=f"restart_{quiz_key}"):
            st.session_state[f'{quiz_key}_score'] = 0
            st.session_state[f'{quiz_key}_answered'] = []
            st.session_state[f'{quiz_key}_user_answers'] = {}
            st.rerun()