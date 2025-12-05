import pandas as pd
import numpy as np
import random
from pathlib import Path

# --- Configuration des chemins de fichiers ---
# Assurez-vous que ce chemin est correct par rapport à l'emplacement d'exécution de ce script
# Si votre fichier est dans 'data/' à côté de ce script, utilisez:
# FILE_PATH = Path('./data/athletes_enriched.csv')
# Si ce script est exécuté depuis le même dossier que votre script Streamlit:
FILE_PATH = Path(__file__).parent.parent / 'data' / 'athletes_enriched.csv'

# --- Paramètres de simulation des mesures ---
SIMULATION_CONFIG = {
    'Male': {
        # Hauteur (en cm)
        'height_choices': [175.0, 183.0, 190.0],
        # Poids (en kg) : Exemple de valeurs
        'weight_choices': [70.0, 75.0, 80.0, 85.0, 95.0]
    },
    'Female': {
        # Hauteur (en cm)
        'height_choices': [165.0, 170.0, 175.0],
        # Poids (en kg) : Exemple de valeurs
        'weight_choices': [55.0, 60.0, 65.0, 70.0, 75.0]
    }
}

def clean_and_simulate_measurements(file_path: Path):
    """
    Charge le dataset, simule la taille et le poids pour les valeurs manquantes/zéro,
    et écrase le fichier original.
    """
    if not file_path.exists():
        print(f"❌ Erreur : Fichier non trouvé à {file_path.resolve()}")
        return

    try:
        # Lire le fichier en gérant les valeurs manquantes potentielles (NaN)
        df = pd.read_csv(file_path)
        print(f"✅ Fichier chargé : {file_path.name}. Lignes : {len(df)}")
    except Exception as e:
        print(f"❌ Erreur lors du chargement : {e}")
        return

    # S'assurer que les colonnes existent
    required_cols = ['gender', 'height', 'weight']
    if not all(col in df.columns for col in required_cols):
        print(f"❌ Erreur : Le DataFrame doit contenir les colonnes {required_cols}")
        return

    # Remplacer les NaN par 0.0 pour cibler toutes les valeurs à corriger (0 ou NaN)
    df['height'] = df['height'].fillna(0.0)
    df['weight'] = df['weight'].fillna(0.0)
    
    # ----------------------------------------------------------------------
    # Définition de la fonction de simulation
    # ----------------------------------------------------------------------
    epsilon = 0.01 # Pour capturer les zéros flottants

    def apply_simulation(row):
        gender = row['gender']
        
        # Le code utilise 'Male'/'Female' dans la configuration, mais vérifions si 'M'/'W' sont présents
        # Si vous utilisez la page 3 du code, les valeurs sont probablement 'Male'/'Female' car elles sont utilisées directement dans l'affichage:
        # st.markdown(f"**Gender:** {'👨' if athlete_data['gender'] == 'Male' else '👩'} {athlete_data['gender']}")
        
        if gender not in SIMULATION_CONFIG:
            return row # Ne rien faire pour les genres non mappés (ex: 'Unknown', NaN, ou 'M'/'W' si non mappé)

        config = SIMULATION_CONFIG[gender]
            
        # 1. Traitement de la taille (height)
        # Si la taille est manquante (proche de 0)
        if abs(row['height']) < epsilon:
            row['height'] = random.choice(config['height_choices'])
            
        # 2. Traitement du poids (weight)
        # Si le poids est manquant (proche de 0)
        if abs(row['weight']) < epsilon:
            row['weight'] = random.choice(config['weight_choices'])
                
        return row

    # Application de la simulation ligne par ligne
    df_modified = df.apply(apply_simulation, axis=1)

    # ----------------------------------------------------------------------
    # Sauvegarde (Écrasement)
    # ----------------------------------------------------------------------
    
    # Écrasement du fichier original
    df_modified.to_csv(file_path, index=False)
    
    print(f"\n🎉 Succès : Le fichier {file_path.name} a été modifié et sauvegardé (écrasé).")
    print("Les valeurs de 'height' et 'weight' égales à zéro ont été remplacées par des données simulées.")

# --- Exécution du script de simulation ---
clean_and_simulate_measurements(FILE_PATH)