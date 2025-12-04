"""
Data Merging Module for Paris 2024 Olympic Games Dashboard

This module takes the cleaned DataFrames and performs the necessary joins 
to create the final, rich tables required for the dashboard visualizations.
"""

import pandas as pd
import streamlit as st
import numpy as np

# 🚀 CACHE: Le décorateur essentiel pour que toutes ces jointures lourdes 
# ne soient effectuées qu'une seule fois au lancement de l'application.

@st.cache_data
def get_merged_data(data: dict) -> dict:
    """
    Exécute toutes les opérations de fusion nécessaires pour les pages du dashboard.
    
    Args:
        data (dict): Dictionnaire des DataFrames nettoyés (issus de load_all_data()).
        
    Returns:
        dict: Dictionnaire contenant les DataFrames finaux fusionnés.
    """
    
    # --------------------------------------------------------------------------
    # I. FUSION GLOBALE : Médailles, Pays (NOC), Noms & Continent (Pages 1 & 2)
    # --------------------------------------------------------------------------
    
    df_medals_total = data.get('medals_total').copy()
    df_nocs = data.get('nocs').copy()
    
    # Assurez-vous d'avoir une colonne total pour les indicateurs
    if 'total' not in df_medals_total.columns:
        df_medals_total['total'] = df_medals_total[['gold', 'silver', 'bronze']].sum(axis=1)
    
    # Renommage pour la jointure et l'affichage
    df_medals_total.rename(columns={'noc': 'code'}, inplace=True)
    
    # Jointure des médailles avec les noms de pays et les continents
    df_global_medals = pd.merge(
        df_medals_total,
        df_nocs[['code', 'country_long', 'continent']],
        on='code',
        how='left'
    )
    
    # Nettoyage final des valeurs manquantes après fusion
    df_global_medals['country_long'] = df_global_medals['country_long'].fillna('Inconnu')
    df_global_medals['continent'] = df_global_medals['continent'].fillna('Autre/Non-Olympiques')
    
    # --------------------------------------------------------------------------
    # II. FUSION ATHLÈTE : Profils détaillés, Coachs et Médaillés (Page 3)
    # --------------------------------------------------------------------------
    
    df_athletes = data.get('athletes').copy()
    df_medalists = data.get('medalists').copy()
    df_coaches = data.get('coaches').copy()
    df_teams = data.get('teams').copy()
    
    # 1. Joindre les Athlètes et leurs Médailles (pour le total des médailles par athlète)
    # df_medalists contient les lignes pour chaque médaille gagnée par un athlète
    df_athlete_medals_count = df_medalists.groupby(['code', 'athlete_full_name']).size().reset_index(name='athlete_medal_count')
    
    # Fusionner le comptage des médailles dans le DF Athletes principal
    df_athlete_profiles = pd.merge(
        df_athletes, 
        df_athlete_medals_count[['code', 'athlete_medal_count']],
        on='code',
        how='left'
    )
    df_athlete_profiles['athlete_medal_count'] = df_athlete_profiles['athlete_medal_count'].fillna(0).astype(int)

    # 2. Joindre les Coachs aux Athlètes/Équipes (Complexité : Coachs sont souvent liés aux équipes ou NOC)
    # Nous allons créer une liste de coachs par NOC, puis la fusionner.
    df_coaches_by_noc = df_coaches.groupby('noc')['coach_full_name'].agg(lambda x: ', '.join(x.unique())).reset_index(name='coach_names_by_country')
    
    # Fusionner les noms des coachs dans le DF Athletes
    df_athlete_profiles = pd.merge(
        df_athlete_profiles,
        df_coaches_by_noc,
        left_on='code_noc', # Assurez-vous que cette colonne existe et représente le NOC dans athletes.csv
        right_on='noc',
        how='left'
    ).drop(columns=['noc'])
    df_athlete_profiles.rename(columns={'code': 'athlete_code'}, inplace=True) # Renommage pour clarté
    df_athlete_profiles['coach_names_by_country'] = df_athlete_profiles['coach_names_by_country'].fillna('N/A')
    
    # --------------------------------------------------------------------------
    # III. FUSION ÉVÉNEMENTS : Calendrier détaillé et Sites (Page 4)
    # --------------------------------------------------------------------------
    
    df_schedules = data.get('schedules').copy()
    df_events = data.get('events').copy()
    df_venues = data.get('venues').copy()
    
    # 1. Lier les Schedules aux Events (Sport et Discipline)
    df_schedule_details = pd.merge(
        df_schedules,
        df_events[['event_id', 'sport', 'discipline', 'event_name']],
        on='event_id',
        how='left'
    )
    
    # 2. Lier les Schedules aux Venues (Coordonnées Lat/Lon)
    df_schedule_final = pd.merge(
        df_schedule_details,
        df_venues[['venue_id', 'venue_name', 'lat', 'lon']],
        on='venue_id',
        how='left'
    )
    
    # --------------------------------------------------------------------------
    # IV. NETTOYAGE FINAL ET RETOUR
    # --------------------------------------------------------------------------
    
    return {
        'global_medals': df_global_medals,          # Total des médailles + Continent (Pages 1 & 2)
        'athlete_profiles': df_athlete_profiles,    # Profils athlètes enrichis (Page 3)
        'schedule_venues': df_schedule_final,       # Calendrier + Sport/Lieu/Coordonnées (Page 4)
        'raw_nocs': df_nocs,                        # NOCs originaux (pour les filtres)
        'raw_events': df_events,                    # Events originaux (pour les filtres)
        'raw_venues': df_venues,                    # Venues originales (pour la carte des sites)
    }


# Comment appeler ce fichier dans vos pages Streamlit :
# from utils.cleaning import load_all_data
# from utils.merging import get_merged_data

# # Charger les données
# cleaned_data = load_all_data() 
# # Fusionner les données
# final_data = get_merged_data(cleaned_data)
# 
# df_for_global_map = final_data['global_medals']
# # ... etc.