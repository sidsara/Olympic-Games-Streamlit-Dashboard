import streamlit as st

st.set_page_config(
    page_title="Paris 2024 Olympics Dashboard",
    page_icon=":trophy:",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
# 🏅 Paris 2024 Olympics Dashboard

Bienvenue sur le tableau de bord interactif des Jeux Olympiques de Paris 2024 !

Utilisez le menu de gauche pour naviguer entre les différentes pages :
- **Overview** : Vue d'ensemble et KPIs
- **Global Analysis** : Analyse géographique et hiérarchique
- **Athlete Performance** : Statistiques individuelles des athlètes
- **Sports & Events** : Informations sur les sports et les événements

---
""")

st.info("Sélectionnez une page dans la barre latérale pour commencer l'exploration.")