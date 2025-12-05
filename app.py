import streamlit as st
import base64
import os

# --- Fonction pour convertir l'image en Base64 ---
def get_base64_image(image_path):
    # Vérifie si le fichier existe
    if not os.path.exists(image_path):
        st.error(f"Image non trouvée : {image_path}")
        return ""
    
    # Lecture et encodage en Base64
    try:
        with open(image_path, "rb") as img_file:
            b64_data = base64.b64encode(img_file.read()).decode()
        ext = image_path.split('.')[-1]
        return f"data:image/{ext};base64,{b64_data}"
    except Exception as e:
        st.error(f"Erreur lors de l'encodage de l'image : {e}")
        return ""

# --- Configuration de la Page ---
st.set_page_config(
    page_title="Paris 2024 Olympics Dashboard",
    page_icon=":trophy:",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Chemin et Base64 de l'Image ---
# ASSUREZ-VOUS que ce chemin est correct par rapport à l'emplacement du script
img_path = "figures/images/welcome.jpg"
img_base64 = get_base64_image(img_path)

# --- Application des Styles CSS pour le Fond Flouté et le Contenu Centré ---
if img_base64:
    # **CORRECTION CLÉS :** Cibler les conteneurs Streamlit (.stApp, data-testid="stAppViewContainer")
    # et s'assurer que le contenu principal est transparent pour laisser voir le fond.
    st.markdown(
        f"""
        <style>
        /* 1. Appliquer le fond flouté et fixé à toute la page Streamlit */
        [data-testid="stAppViewContainer"] {{
            background: url('{img_base64}') no-repeat center center fixed;
            background-size: cover;
        }}
        
        /* 2. Appliquer le filtre de flou et de luminosité (overlay sombre) au conteneur principal */
        /* Nous appliquons le filtre ici plutôt qu'au fond pour un meilleur support par Streamlit */
        .stApp {{
            background-color: transparent; /* Assurer la transparence */
        }}
        
        /* Ciblez le conteneur principal du contenu pour appliquer le filtre et forcer la vue */
        [data-testid="stAppViewBlockContainer"] {{
            background: rgba(255, 255, 255, 0); /* Rendre le fond du bloc de contenu transparent */
            filter: blur(8px) brightness(0.7); /* Appliquer le flou et l'obscurcissement au fond */
            position: fixed; /* Fixer le fond */
            top: 0; left: 0; right: 0; bottom: 0;
            z-index: -1;
        }}
        
        /* 3. Style pour le panneau de bienvenue (qui doit être par-dessus le fond flouté) */
        .centered-content {{
            position: relative; /* Utiliser relative car nous ne fixons plus le panneau */
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            height: 100vh; /* Prendre toute la hauteur de la vue pour le centrage */
            padding: 0 20px;
        }}
        
        /* 4. Style pour la box de texte */
        .welcome-box {{
            width: 80%; /* Ajuster la largeur de la boîte de bienvenue */
            max-width: 800px;
            text-align: center;
            color: #fff;
            z-index: 10; /* Assurez-vous qu'il est au-dessus du flou */
            background: rgba(30, 30, 60, 0.7); /* Augmenter l'opacité pour la lisibilité */
            border-radius: 20px;
            padding: 40px 20px;
            box-shadow: 0 4px 24px rgba(0,0,0,0.5);
            /* Centrage auto dans le conteneur Streamlit */
            margin-left: auto;
            margin-right: auto;
            margin-top: 15vh; /* Ajouter un décalage vers le bas si nécessaire */
        }}

        .welcome-title {{
            font-size: 3em;
            font-weight: bold;
            margin-bottom: 20px;
            font-family: 'Segoe UI', sans-serif;
            text-shadow: 2px 2px 8px #000;
        }}
        .welcome-text {{
            font-size: 1.5em;
            font-family: 'Segoe UI', sans-serif;
            text-shadow: 1px 1px 6px #000;
        }}
        </style>
        
        <div class="welcome-box">
            <div class="welcome-title">Bienvenue aux Jeux Olympiques de Paris 2024 !</div>
            <div class="welcome-text">
                Plongez dans l’univers festif et sportif des Jeux Olympiques.<br>
                Explorez les performances, les événements et l’ambiance unique de Paris.<br>
                Utilisez le menu à gauche pour découvrir toutes les analyses et statistiques.<br><br>
                <b>Que la fête commence ! 🏅</b>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
else:
    st.warning("L'image de fond n'a pas pu être chargée. Vérifiez le chemin et le nom du fichier.")
    
# Pour que l'application s'affiche correctement sans le hack CSS ci-dessus
# Il est souvent nécessaire d'ajouter un élément Streamlit standard, même vide,
# après la balise markdown pour s'assurer que Streamlit génère son conteneur principal
st.empty()