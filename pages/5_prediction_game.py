"""
Page 5: Prediction Game (Olympic Quiz Challenge)
================================================
Interactive quiz game to test knowledge of Paris 2024 Olympic medal winners

Author: Your Name
Date: December 2024
"""

import streamlit as st
import pandas as pd
from datetime import datetime
from pathlib import Path
import random

# Configuration de la page
st.set_page_config(
    page_title="🏅 Olympic Medal Predictor",
    page_icon="🏅",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Define paths
DATA_DIR = Path(__file__).parent.parent / 'data'

# CSS simplifié et cohérent avec les autres pages
st.markdown("""
    <style>
    .main-title {
        font-size: 2.5rem;
        font-weight: bold;
        color: #0066CC;
        text-align: center;
        margin-bottom: 1rem;
    }
    
    .subtitle {
        font-size: 1.1rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .score-card {
        background-color: #f0f2f6;
        padding: 1.2rem;
        border-radius: 8px;
        text-align: center;
        margin: 1rem 0;
        border: 1px solid #ddd;
    }
    
    .score-card h4 {
        color: #0066CC;
        margin-bottom: 0.5rem;
        font-size: 0.9rem;
    }
    
    .score-card h2 {
        color: #333;
        margin: 0;
    }
    
    .correct-answer {
        background-color: #d4edda;
        padding: 1.2rem;
        border-radius: 8px;
        border-left: 4px solid #28a745;
        margin: 1rem 0;
    }
    
    .correct-answer h3 {
        color: #155724;
        margin-bottom: 0.5rem;
        font-size: 1.3rem;
    }
    
    .correct-answer p {
        color: #155724;
        margin: 0.3rem 0;
    }
    
    .wrong-answer {
        background-color: #f8d7da;
        padding: 1.2rem;
        border-radius: 8px;
        border-left: 4px solid #dc3545;
        margin: 1rem 0;
    }
    
    .wrong-answer h3 {
        color: #721c24;
        margin-bottom: 0.5rem;
        font-size: 1.3rem;
    }
    
    .wrong-answer p {
        color: #721c24;
        margin: 0.3rem 0;
    }
    
    .question-card {
        background-color: #ffffff;
        border-radius: 10px;
        padding: 1.5rem;
        border: 1px solid #ddd;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin-bottom: 1.5rem;
    }
    
    .question-card h3 {
        color: #0066CC;
        margin-bottom: 0.8rem;
        font-size: 1.5rem;
    }
    
    .question-card p {
        color: #333;
        margin: 0.3rem 0;
    }
    
    .info-text {
        color: #666;
        font-size: 0.9rem;
    }
    </style>
""", unsafe_allow_html=True)

# ============================================================================
# DATA LOADING
# ============================================================================

@st.cache_data
def load_olympic_data():
    """Charge les données réelles des JO Paris 2024"""
    try:
        medals_enriched = pd.read_csv(DATA_DIR / 'medals_enriched.csv')
        # Nettoyer les données
        medals_enriched = medals_enriched.dropna(subset=['medal_type', 'country', 'discipline', 'event'])
        
        # Créer une colonne simplifiée pour le type de médaille
        medals_enriched['medal'] = medals_enriched['medal_type'].str.replace(' Medal', '')
        
        return medals_enriched
    except Exception as e:
        st.error(f"❌ Erreur lors du chargement des données: {e}")
        return None

# ============================================================================
# GAME LOGIC FUNCTIONS
# ============================================================================

def get_new_question(df, difficulty='medium'):
    """Génère une nouvelle question aléatoire basée sur les vraies données"""
    # Filtrer uniquement les médailles d'or
    gold_medals = df[df['medal'] == 'Gold'].copy()
    
    if len(gold_medals) == 0:
        return None
    
    # Sélectionner une question aléatoire
    question_row = gold_medals.sample(1).iloc[0]
    correct_answer = question_row['country']
    
    # Obtenir d'autres pays comme réponses incorrectes
    all_countries = df['country'].unique().tolist()
    other_countries = [c for c in all_countries if c != correct_answer]
    
    # Sélectionner le nombre de réponses selon la difficulté
    if difficulty == 'easy':
        num_wrong = 2  # 3 choix au total
    elif difficulty == 'hard':
        num_wrong = 5  # 6 choix au total
    else:  # medium
        num_wrong = 3  # 4 choix au total
    
    wrong_answers = random.sample(other_countries, min(num_wrong, len(other_countries)))
    options = [correct_answer] + wrong_answers
    random.shuffle(options)
    
    return {
        'sport': question_row['discipline'],
        'event': question_row['event'],
        'correct_answer': correct_answer,
        'options': options,
        'athlete': question_row.get('name', 'Unknown'),
        'medal_date': question_row.get('medal_date', 'N/A'),
        'gender': question_row.get('gender', 'N/A')
    }

def calculate_stats(history):
    """Calcule les statistiques du joueur"""
    if len(history) == 0:
        return {
            'total': 0,
            'correct': 0,
            'accuracy': 0,
            'streak': 0,
            'best_streak': 0
        }
    
    df = pd.DataFrame(history)
    correct_count = df['correct'].sum()
    total = len(df)
    accuracy = (correct_count / total * 100) if total > 0 else 0
    
    # Calculer la série actuelle
    current_streak = 0
    best_streak = 0
    temp_streak = 0
    
    for correct in df['correct']:
        if correct:
            temp_streak += 1
            best_streak = max(best_streak, temp_streak)
        else:
            temp_streak = 0
    
    # Série actuelle (depuis la fin)
    for correct in reversed(df['correct'].tolist()):
        if correct:
            current_streak += 1
        else:
            break
    
    return {
        'total': total,
        'correct': correct_count,
        'accuracy': accuracy,
        'streak': current_streak,
        'best_streak': best_streak
    }

# ============================================================================
# SESSION STATE INITIALIZATION
# ============================================================================

if 'score' not in st.session_state:
    st.session_state.score = 0
if 'total_questions' not in st.session_state:
    st.session_state.total_questions = 0
if 'current_question' not in st.session_state:
    st.session_state.current_question = None
if 'answered' not in st.session_state:
    st.session_state.answered = False
if 'history' not in st.session_state:
    st.session_state.history = []
if 'difficulty' not in st.session_state:
    st.session_state.difficulty = 'medium'

# ============================================================================
# MAIN APP
# ============================================================================

# Charger les données
df = load_olympic_data()

if df is None or len(df) == 0:
    st.error("❌ Impossible de charger les données olympiques. Vérifiez que le fichier medals_enriched.csv existe.")
    st.stop()

# Titre principal
st.markdown('<p class="main-title">🏅 Jeu de Prédiction des Médailles</p>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Testez vos connaissances sur les médaillés des Jeux Olympiques de Paris 2024</p>', unsafe_allow_html=True)
st.markdown("---")

# ============================================================================
# SIDEBAR
# ============================================================================

with st.sidebar:
    st.header("🎮 Paramètres")
    
    # Sélection de la difficulté
    st.session_state.difficulty = st.selectbox(
        "Niveau de difficulté",
        options=['easy', 'medium', 'hard'],
        format_func=lambda x: {'easy': '😊 Facile (3 choix)', 'medium': '😐 Moyen (4 choix)', 'hard': '😈 Difficile (6 choix)'}[x],
        index=1
    )
    
    st.markdown("---")
    
    # Statistiques du joueur
    stats = calculate_stats(st.session_state.history)
    
    st.subheader("📊 Vos statistiques")
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Score", f"{stats['correct']}/{stats['total']}")
    with col2:
        st.metric("Précision", f"{stats['accuracy']:.1f}%")
    
    st.metric("🔥 Série actuelle", f"{stats['streak']}")
    st.metric("⭐ Meilleure série", f"{stats['best_streak']}")
    
    st.markdown("---")
    
    # Statistiques du dataset
    st.subheader("📈 Base de données")
    st.write(f"**Médailles d'or:** {len(df[df['medal'] == 'Gold'])}")
    st.write(f"**Pays:** {df['country'].nunique()}")
    st.write(f"**Sports:** {df['discipline'].nunique()}")
    st.write(f"**Épreuves:** {df['event'].nunique()}")
    
    st.markdown("---")
    
    # Bouton de réinitialisation
    if st.button("🔄 Réinitialiser", use_container_width=True):
        st.session_state.score = 0
        st.session_state.total_questions = 0
        st.session_state.current_question = None
        st.session_state.answered = False
        st.session_state.history = []
        st.rerun()

# ============================================================================
# QUIZ GAME
# ============================================================================

st.markdown("## 🎯 Quiz")

# Générer ou récupérer la question actuelle
if st.session_state.current_question is None:
    st.session_state.current_question = get_new_question(df, st.session_state.difficulty)
    st.session_state.answered = False

if st.session_state.current_question:
    question = st.session_state.current_question
    
    # Afficher la question dans une carte
    st.markdown(f"""
    <div class="question-card">
        <h3>🏅 {question['sport']}</h3>
        <p><strong>Épreuve:</strong> {question['event']}</p>
        <p class="info-text">Genre: {question['gender']} • Date: {question['medal_date']}</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns([3, 1])
    
    with col2:
        st.markdown(f"""
        <div class="score-card">
            <h4>QUESTION</h4>
            <h2>{st.session_state.total_questions + 1}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    # Options de réponse
    if not st.session_state.answered:
        st.markdown("#### Quel pays a remporté la médaille d'or ?")
        
        # Adapter le nombre de colonnes selon la difficulté
        if len(question['options']) <= 3:
            cols = st.columns(3)
        elif len(question['options']) <= 4:
            cols = st.columns(2)
        else:
            cols = st.columns(3)
        
        for idx, option in enumerate(question['options']):
            with cols[idx % len(cols)]:
                if st.button(
                    f"🌍 {option}", 
                    key=f"option_{idx}", 
                    use_container_width=True
                ):
                    st.session_state.answered = True
                    st.session_state.total_questions += 1
                    
                    is_correct = (option == question['correct_answer'])
                    
                    if is_correct:
                        st.session_state.score += 1
                    
                    # Enregistrer dans l'historique
                    st.session_state.history.append({
                        'sport': question['sport'],
                        'event': question['event'],
                        'your_answer': option,
                        'correct_answer': question['correct_answer'],
                        'correct': is_correct,
                        'athlete': question['athlete'],
                        'timestamp': datetime.now(),
                        'difficulty': st.session_state.difficulty
                    })
                    st.rerun()
    
    # Afficher le résultat
    if st.session_state.answered and len(st.session_state.history) > 0:
        last_answer = st.session_state.history[-1]
        
        if last_answer['correct']:
            st.markdown(f"""
            <div class="correct-answer">
                <h3>✅ Bonne réponse !</h3>
                <p><strong>{question['correct_answer']}</strong> a bien remporté la médaille d'or.</p>
                <p><strong>Athlète:</strong> {question['athlete']}</p>
                <p><strong>Date:</strong> {question['medal_date']}</p>
            </div>
            """, unsafe_allow_html=True)
            
            st.balloons()
        else:
            st.markdown(f"""
            <div class="wrong-answer">
                <h3>❌ Mauvaise réponse</h3>
                <p><strong>Votre réponse:</strong> {last_answer['your_answer']}</p>
                <p><strong>Bonne réponse:</strong> {question['correct_answer']}</p>
                <p><strong>Athlète:</strong> {question['athlete']}</p>
                <p><strong>Date:</strong> {question['medal_date']}</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Bouton pour question suivante
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("➡️ Question suivante", use_container_width=True):
                st.session_state.current_question = get_new_question(df, st.session_state.difficulty)
                st.session_state.answered = False
                st.rerun()

# ============================================================================
# FOOTER
# ============================================================================

st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; padding: 20px;'>
    <p>📊 Jeu de Prédiction des Médailles | Paris 2024 Olympics Dashboard</p>
    <p>Data Source: Kaggle - Paris 2024 Olympic Summer Games</p>
</div>
""", unsafe_allow_html=True)