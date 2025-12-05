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

# CSS personnalisé moderne
st.markdown("""
    <style>
    /* Variables CSS */
    :root {
        --primary-gold: #FFD700;
        --secondary-silver: #C0C0C0;
        --tertiary-bronze: #CD7F32;
        --accent: #FF6B35;
    }
    
    .main-title {
        font-size: 3.5rem;
        font-weight: 900;
        text-align: center;
        background: linear-gradient(135deg, var(--primary-gold) 0%, var(--accent) 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        padding: 1rem 0;
        animation: fadeIn 1s ease-out;
        text-shadow: 0 0 30px rgba(255, 215, 0, 0.3);
    }
    
    .subtitle {
        font-size: 1.3rem;
        color: #B4B4B4;
        text-align: center;
        margin-bottom: 2rem;
        animation: fadeIn 1.5s ease-out;
    }
    
    .score-card {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        padding: 1.5rem;
        border-radius: 15px;
        color: white;
        text-align: center;
        margin: 1rem 0;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        transition: all 0.3s ease;
    }
    
    .score-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 40px rgba(240, 147, 251, 0.4);
    }
    
    .correct-answer {
        background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%);
        padding: 1.5rem;
        border-radius: 15px;
        border-left: 5px solid #28a745;
        margin: 1rem 0;
        animation: slideIn 0.5s ease-out;
        box-shadow: 0 4px 15px rgba(40, 167, 69, 0.2);
    }
    
    .correct-answer h3 {
        color: #155724;
        margin-bottom: 0.5rem;
    }
    
    .correct-answer p {
        color: #155724;
        margin: 0.3rem 0;
    }
    
    .wrong-answer {
        background: linear-gradient(135deg, #f8d7da 0%, #f5c6cb 100%);
        padding: 1.5rem;
        border-radius: 15px;
        border-left: 5px solid #dc3545;
        margin: 1rem 0;
        animation: slideIn 0.5s ease-out;
        box-shadow: 0 4px 15px rgba(220, 53, 69, 0.2);
    }
    
    .wrong-answer h3 {
        color: #721c24;
        margin-bottom: 0.5rem;
    }
    
    .wrong-answer p {
        color: #721c24;
        margin: 0.3rem 0;
    }
    
    .question-card {
        background: rgba(30, 30, 46, 0.8);
        backdrop-filter: blur(10px);
        border-radius: 20px;
        padding: 2rem;
        border: 1px solid rgba(255, 107, 53, 0.2);
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
        margin-bottom: 2rem;
    }
    
    .question-card h3 {
        color: var(--primary-gold);
        margin-bottom: 1rem;
    }
    
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    @keyframes slideIn {
        from { transform: translateX(-100%); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    
    /* Boutons stylisés */
    .stButton > button {
        background: linear-gradient(135deg, var(--accent) 0%, #FF8C61 100%);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 12px 30px;
        font-weight: 600;
        font-size: 1rem;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(255, 107, 53, 0.4);
    }
    
    .stButton > button:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 25px rgba(255, 107, 53, 0.6);
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
st.markdown('<h1 class="main-title">🏅 Olympic Medal Predictor</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Paris 2024 - Testez vos connaissances sur les médaillés olympiques !</p>', unsafe_allow_html=True)

# ============================================================================
# SIDEBAR
# ============================================================================

with st.sidebar:
    st.header("🎮 Paramètres du jeu")
    
    # Sélection de la difficulté
    st.session_state.difficulty = st.selectbox(
        "🎯 Difficulté",
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
        st.metric("🎯 Score", f"{stats['correct']}/{stats['total']}")
    with col2:
        st.metric("📈 Précision", f"{stats['accuracy']:.1f}%")
    
    st.metric("🔥 Série actuelle", f"{stats['streak']} 🏆")
    st.metric("⭐ Meilleure série", f"{stats['best_streak']} 🏆")
    
    st.markdown("---")
    
    # Statistiques du dataset
    st.subheader("📈 Base de données")
    st.write(f"🏆 Médailles d'or: {len(df[df['medal'] == 'Gold'])}")
    st.write(f"🌍 Pays: {df['country'].nunique()}")
    st.write(f"🎾 Sports: {df['discipline'].nunique()}")
    st.write(f"🏅 Épreuves: {df['event'].nunique()}")
    
    st.markdown("---")
    
    # Bouton de réinitialisation
    if st.button("🔄 Réinitialiser", use_container_width=True, type="primary"):
        st.session_state.score = 0
        st.session_state.total_questions = 0
        st.session_state.current_question = None
        st.session_state.answered = False
        st.session_state.history = []
        st.rerun()

# ============================================================================
# QUIZ GAME
# ============================================================================

st.markdown("### 🎯 Devinez quel pays a remporté la médaille d'or !")

# Générer ou récupérer la question actuelle
if st.session_state.current_question is None:
    st.session_state.current_question = get_new_question(df, st.session_state.difficulty)
    st.session_state.answered = False

if st.session_state.current_question:
    question = st.session_state.current_question
    
    # Afficher la question dans une carte stylisée
    st.markdown(f"""
    <div class="question-card">
        <h3>🏅 {question['sport']}</h3>
        <p style="font-size: 1.1rem; color: #FAFAFA;"><strong>Épreuve:</strong> {question['event']}</p>
        <p style="color: #B4B4B4;">Genre: {question['gender']} | Date: {question['medal_date']}</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns([3, 1])
    
    with col2:
        st.markdown(f"""
        <div class="score-card">
            <h4>Question</h4>
            <h2>{st.session_state.total_questions + 1}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    # Options de réponse
    if not st.session_state.answered:
        st.markdown("#### 🌍 Sélectionnez le pays médaillé d'or:")
        
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
                    use_container_width=True,
                    type="secondary"
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
                <h3>✅ Excellent ! Bonne réponse !</h3>
                <p><strong>{question['correct_answer']}</strong> a bien remporté la médaille d'or ! 🥇</p>
                <p>🏅 <strong>Athlète:</strong> {question['athlete']}</p>
                <p>📅 <strong>Date:</strong> {question['medal_date']}</p>
            </div>
            """, unsafe_allow_html=True)
            
            st.balloons()
        else:
            st.markdown(f"""
            <div class="wrong-answer">
                <h3>❌ Dommage ! Mauvaise réponse</h3>
                <p>Votre réponse: <strong>{last_answer['your_answer']}</strong></p>
                <p>La bonne réponse était: <strong>{question['correct_answer']}</strong> 🥇</p>
                <p>🏅 <strong>Athlète:</strong> {question['athlete']}</p>
                <p>📅 <strong>Date:</strong> {question['medal_date']}</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Bouton pour question suivante
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("➡️ Question suivante", type="primary", use_container_width=True):
                st.session_state.current_question = get_new_question(df, st.session_state.difficulty)
                st.session_state.answered = False
                st.rerun()

# ============================================================================
# FOOTER
# ============================================================================

st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; padding: 20px;'>
    <p>🏅 <strong>Olympic Medal Predictor</strong> | Paris 2024 Olympics</p>
    <p>Données officielles des Jeux Olympiques de Paris 2024</p>
    <p>Made with ❤️ using Streamlit & Python</p>
</div>
""", unsafe_allow_html=True)