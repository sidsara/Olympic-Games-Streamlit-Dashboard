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
        font-size: 2.8rem;
        font-weight: bold;
        background: linear-gradient(90deg, #b3e5fc 0%, #FFD700 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 1rem;
        letter-spacing: 2px;
        text-shadow: 2px 2px 8px rgba(179, 229, 252, 0.15);
        animation: bounce 1.2s infinite alternate;
    }
    @keyframes bounce {
        0% { transform: translateY(0);}
        100% { transform: translateY(-10px);}
    }
    .subtitle {
        font-size: 1.2rem;
        color: #333;
        text-align: center;
        margin-bottom: 2rem;
        font-style: italic;
        background: linear-gradient(90deg, #b3e5fc 0%, #FFD700 100%);
        border-radius: 8px;
        padding: 0.5rem;
        box-shadow: 0 2px 8px rgba(179, 229, 252, 0.15);
    }
    .score-card {
        background: linear-gradient(135deg, #b3e5fc 0%, #FFD700 100%);
        padding: 1.2rem;
        border-radius: 12px;
        text-align: center;
        margin: 1rem 0;
        border: 2px solid #FFD700;
        box-shadow: 0 2px 8px rgba(179, 229, 252, 0.15);
        animation: pulse 1.5s infinite;
    }
    @keyframes pulse {
        0% { box-shadow: 0 0 0 0 rgba(144, 164, 174, 0.3);}
        70% { box-shadow: 0 0 10px 10px rgba(144, 164, 174, 0.1);}
        100% { box-shadow: 0 0 0 0 rgba(144, 164, 174, 0.3);}
    }
    .score-card h4 {
        color: #333;
        margin-bottom: 0.5rem;
        font-size: 1.1rem;
        font-weight: bold;
        text-shadow: 1px 1px 6px #b3e5fc;
    }
    .score-card h2 {
        color: #333;
        margin: 0;
        font-size: 2.2rem;
        font-family: 'Comic Sans MS', cursive, sans-serif;
    }
    .correct-answer {
        background: linear-gradient(90deg, #B2FF59 0%, #00E676 100%);
        padding: 1.2rem;
        border-radius: 12px;
        border-left: 6px solid #43A047;
        margin: 1rem 0;
        box-shadow: 0 2px 8px rgba(67, 160, 71, 0.3);
        animation: tada 0.7s;
    }
    @keyframes tada {
        0% { transform: scale(1);}
        10%, 20% { transform: scale(0.9) rotate(-3deg);}
        30%, 50%, 70%, 90% { transform: scale(1.1) rotate(3deg);}
        40%, 60%, 80% { transform: scale(1.1) rotate(-3deg);}
        100% { transform: scale(1);}
    }
    .correct-answer h3 {
        color: #155724;
        margin-bottom: 0.5rem;
        font-size: 1.5rem;
        font-weight: bold;
        letter-spacing: 1px;
    }
    .correct-answer p {
        color: #155724;
        margin: 0.3rem 0;
        font-size: 1.1rem;
    }
    .wrong-answer {
        background: linear-gradient(90deg, #FFCDD2 0%, #FF5252 100%);
        padding: 1.2rem;
        border-radius: 12px;
        border-left: 6px solid #B71C1C;
        margin: 1rem 0;
        box-shadow: 0 2px 8px rgba(183, 28, 28, 0.3);
        animation: shake 0.5s;
    }
    @keyframes shake {
        0% { transform: translateX(0);}
        20% { transform: translateX(-8px);}
        40% { transform: translateX(8px);}
        60% { transform: translateX(-8px);}
        80% { transform: translateX(8px);}
        100% { transform: translateX(0);}
    }
    .wrong-answer h3 {
        color: #721c24;
        margin-bottom: 0.5rem;
        font-size: 1.5rem;
        font-weight: bold;
        letter-spacing: 1px;
    }
    .wrong-answer p {
        color: #721c24;
        margin: 0.3rem 0;
        font-size: 1.1rem;
    }
    .question-card {
        background: linear-gradient(135deg, #b3e5fc 0%, #FFD700 100%);
        border-radius: 16px;
        padding: 1.5rem;
        border: 2px solid #FFD700;
        box-shadow: 0 2px 12px rgba(179, 229, 252, 0.15);
        margin-bottom: 1.5rem;
        animation: fadeIn 0.7s;
        position: relative;
    }
    @keyframes fadeIn {
        from { opacity: 0;}
        to { opacity: 1;}
    }
    .question-card h3 {
        color: #546E7A;
        margin-bottom: 0.8rem;
        font-size: 1.7rem;
        font-family: 'Comic Sans MS', cursive, sans-serif;
        text-shadow: 1px 1px 6px rgba(84, 110, 122, 0.2);
    }
    .question-card p {
        color: #333;
        margin: 0.3rem 0;
        font-size: 1.1rem;
    }
    .question-number {
        position: absolute;
        top: -25px;
        right: 25px;
        background: linear-gradient(90deg, #b3e5fc 0%, #FFD700 100%);
        color: #333;
        font-size: 1.3rem;
        font-weight: bold;
        padding: 0.5rem 1.2rem;
        border-radius: 50px;
        box-shadow: 0 2px 8px rgba(179, 229, 252, 0.15);
        border: 2px solid #FFD700;
        z-index: 2;
    }
    .info-text {
        color: #666;
        font-size: 1rem;
        font-style: italic;
    }
    .fun-emoji {
        font-size: 2.2rem;
        text-align: center;
        margin-bottom: 0.5rem;
        animation: bounce 1.2s infinite alternate;
    }
    .option-btn {
        font-size: 1.1rem !important;
        font-weight: bold !important;
        background: linear-gradient(90deg, #B0BEC5 0%, #78909C 100%) !important;
        color: #fff !important;
        border-radius: 10px !important;
        margin-bottom: 10px !important;
        border: 2px solid #90A4AE !important;
        box-shadow: 0 2px 8px rgba(144, 164, 174, 0.2) !important;
        transition: transform 0.1s;
    }
    .option-btn:hover {
        transform: scale(1.05);
        background: linear-gradient(90deg, #78909C 0%, #546E7A 100%) !important;
        color: #fff !important;
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

# Titre principal fun
st.markdown('<div class="fun-emoji">🎉🤩🏅</div>', unsafe_allow_html=True)
st.markdown('<p class="main-title">🏅 Olympic Medal Quiz Party!</p>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Testez vos connaissances et amusez-vous avec les médaillés des Jeux Olympiques de Paris 2024 🎈</p>', unsafe_allow_html=True)
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

st.markdown("## 🎯 Quiz Olympique Fun")

# Générer ou récupérer la question actuelle
if st.session_state.current_question is None:
    st.session_state.current_question = get_new_question(df, st.session_state.difficulty)
    st.session_state.answered = False

if st.session_state.current_question:
    question = st.session_state.current_question

    # Ajout d'un emoji sport aléatoire pour le fun
    sport_emojis = ["🏊", "🏃", "🤸", "🏋️", "🚴", "🤾", "🏌️", "🏓", "🏸", "🏒", "🏀", "⚽", "🏈", "🥊", "🥋", "⛷️", "🏂", "🏄", "🚣", "🤽", "🏇", "🏹", "🧗"]
    sport_emoji = random.choice(sport_emojis)

    # Afficher la question dans une carte avec le numéro de question intégré
    st.markdown(f"""
    <div class="question-card">
        <div class="question-number">Q{st.session_state.total_questions + 1}</div>
        <h3>{sport_emoji} {question['sport']}</h3>
        <p><strong>Épreuve:</strong> {question['event']}</p>
        <p class="info-text">Genre: {question['gender']} • Date: {question['medal_date']}</p>
    </div>
    """, unsafe_allow_html=True)

    # Options de réponse
    st.markdown("#### Quel pays a remporté la médaille d'or ?")
    # Adapter le nombre de colonnes selon la difficulté
    if len(question['options']) <= 3:
        cols = st.columns(3)
    elif len(question['options']) <= 4:
        cols = st.columns(2)
    else:
        cols = st.columns(3)

    if not st.session_state.answered:
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

        # Bouton pour question suivante, UN SEUL
        if st.button("➡️ Question suivante", use_container_width=True, type="primary"):
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