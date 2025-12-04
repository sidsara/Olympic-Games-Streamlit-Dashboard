"""
Data Cleaning Module for Paris 2024 Olympic Games Dashboard
This module handles the initial cleaning and preprocessing of raw CSV files,
including the exclusion of specified NOC data.
"""

import pandas as pd
import numpy as np
from pathlib import Path
import streamlit as st
from datetime import datetime

class OlympicDataCleaner:
    """Class to handle cleaning operations for Olympic datasets"""
    
    # 🚨 CONSTANTE D'EXCLUSION NOC : Code NOC à retirer de tous les DataFrames
    NOC_TO_EXCLUDE = 'ISR'
    
    def __init__(self, data_path='data'):
        """
        Initialize the cleaner with the path to data directory
        
        Args:
            data_path (str): Path to the directory containing CSV files
        """
        self.data_path = Path(data_path)
    
    def _exclude_noc(self, df: pd.DataFrame, noc_column_name: str) -> pd.DataFrame:
        """
        Méthode d'aide pour filtrer les lignes selon le code NOC à exclure.
        """
        if noc_column_name in df.columns:
            # S'assurer que les données NOC sont en majuscules pour la comparaison
            df_filtered = df[df[noc_column_name].astype(str).str.strip().str.upper() != self.NOC_TO_EXCLUDE]
            # st.info(f"Filtre appliqué : {len(df) - len(df_filtered)} lignes retirées dans DF ({noc_column_name})")
            return df_filtered
        
        # st.warning(f"Colonne '{noc_column_name}' non trouvée dans le DF pour le filtrage NOC. DF retourné sans filtre.")
        return df

    # --- NETTOYAGE DES ATHLÈTES ---
    @st.cache_data  # 🚀 CACHE
    def clean_athletes(_self) -> pd.DataFrame:
        """Clean athletes.csv file"""
        df = pd.read_csv(_self.data_path / 'athletes.csv')
        df.columns = df.columns.str.strip().str.lower()
        
        # 🛑 FILTRE NOC : Appliqué avant le nettoyage des doublons
        # On suppose que le NOC est dans 'code_noc' ou 'noc'
        if 'code_noc' in df.columns:
            df = _self._exclude_noc(df, noc_column_name='code_noc')
        elif 'noc' in df.columns:
            df = _self._exclude_noc(df, noc_column_name='noc')
        
        # Remove duplicates
        df = df.drop_duplicates(subset=['code'], keep='first')
        
        # Handle missing values
        df['height'] = pd.to_numeric(df['height'], errors='coerce')
        df['weight'] = pd.to_numeric(df['weight'], errors='coerce')
        
        # Calculate age if birth_date exists
        if 'birth_date' in df.columns:
            df['birth_date'] = pd.to_datetime(df['birth_date'], errors='coerce')
            olympic_date = pd.to_datetime('2024-07-26')
            df['age'] = ((olympic_date - df['birth_date']).dt.days / 365.25).round(0)
        
        # Standardize gender values
        if 'gender' in df.columns:
            df['gender'] = df['gender'].str.strip().str.title()
        
        return df
    
    # --- NETTOYAGE DES MÉDAILLES ---
    @st.cache_data
    def clean_medals(_self) -> pd.DataFrame:
        """Clean medals.csv file (medals by event/athlete)"""
        df = pd.read_csv(_self.data_path / 'medals.csv')
        df.columns = df.columns.str.strip().str.lower()
        
        # 🛑 FILTRE NOC
        df = _self._exclude_noc(df, noc_column_name='noc')
        
        # Remove duplicates
        df = df.drop_duplicates()
        
        # Standardize medal types
        if 'medal_type' in df.columns:
            df['medal_type'] = df['medal_type'].str.strip().str.title()
        
        return df
    
    # --- NETTOYAGE TOTAL DES MÉDAILLES ---
    @st.cache_data
    def clean_medals_total(_self) -> pd.DataFrame:
        """Clean medals_total.csv file (medals by country)"""
        df = pd.read_csv(_self.data_path / 'medals_total.csv')
        df.columns = df.columns.str.strip().str.lower()
        
        # 🛑 FILTRE NOC
        df = _self._exclude_noc(df, noc_column_name='noc')
        
        # Ensure numeric columns
        for col in ['gold', 'silver', 'bronze', 'total']:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)
        
        # Remove rows with zero medals (après nettoyage)
        if 'total' in df.columns:
            df = df[df['total'] > 0]
        
        return df
    
    # --- NETTOYAGE DES MÉDAILLÉS ---
    @st.cache_data
    def clean_medalists(_self) -> pd.DataFrame:
        """Clean medalists.csv file"""
        df = pd.read_csv(_self.data_path / 'medalists.csv')
        df.columns = df.columns.str.strip().str.lower()
        
        # 🛑 FILTRE NOC
        df = _self._exclude_noc(df, noc_column_name='noc')
        
        # Remove duplicates
        df = df.drop_duplicates()
        
        # Standardize medal types
        if 'medal_type' in df.columns:
            df['medal_type'] = df['medal_type'].str.strip().str.title()
        
        return df
    
    # --- NETTOYAGE DES CODES NOC (Pays) ---
    @st.cache_data
    def clean_nocs(_self) -> pd.DataFrame:
        """Clean nocs.csv file and add continent mapping"""
        df = pd.read_csv(_self.data_path / 'nocs.csv')
        df.columns = df.columns.str.strip().str.lower()
        
        # 🛑 FILTRE NOC : La colonne du code NOC est 'code'
        df = _self._exclude_noc(df, noc_column_name='code')
        
        # Remove duplicates based on NOC code
        df = df.drop_duplicates(subset=['code'], keep='first')
        
        # Strip whitespace from string columns
        for col in df.select_dtypes(include=['object']).columns:
            df[col] = df[col].str.strip()
            
        # 🌟 IDÉE CRÉATIVE : Mappage Continent/NOC
        # La liste 'ISR' a été volontairement retirée ci-dessous
        continent_mapping = {
            # Europe
            'ALB': 'Europe', 'AND': 'Europe', 'ARM': 'Europe', 'AUT': 'Europe', 'AZE': 'Europe',
            'BLR': 'Europe', 'BEL': 'Europe', 'BIH': 'Europe', 'BUL': 'Europe', 'CRO': 'Europe',
            'CYP': 'Europe', 'CZE': 'Europe', 'DEN': 'Europe', 'EST': 'Europe', 'FIN': 'Europe',
            'FRA': 'Europe', 'GEO': 'Europe', 'GER': 'Europe', 'GBR': 'Europe', 'GRE': 'Europe',
            'HUN': 'Europe', 'ISL': 'Europe', 'IRL': 'Europe', 'ITA': 'Europe', 'KOS': 'Europe',
            'LAT': 'Europe', 'LIE': 'Europe', 'LTU': 'Europe', 'LUX': 'Europe', 'MKD': 'Europe',
            'MLT': 'Europe', 'MDA': 'Europe', 'MON': 'Europe', 'MNE': 'Europe', 'NED': 'Europe',
            'NOR': 'Europe', 'POL': 'Europe', 'POR': 'Europe', 'ROU': 'Europe', 'SMR': 'Europe',
            'SRB': 'Europe', 'SVK': 'Europe', 'SLO': 'Europe', 'ESP': 'Europe', 'SWE': 'Europe',
            'SUI': 'Europe', 'TUR': 'Europe', 'UKR': 'Europe', 'RUS': 'Europe',
            
            # Asia
            'AFG': 'Asia', 'BRN': 'Asia', 'BAN': 'Asia', 'BHU': 'Asia', 'BRU': 'Asia',
            'CAM': 'Asia', 'CHN': 'Asia', 'TPE': 'Asia', 'HKG': 'Asia', 'IND': 'Asia',
            'INA': 'Asia', 'IRQ': 'Asia', 'IRI': 'Asia', 'JOR': 'Asia', 'JPN': 'Asia',
            'KAZ': 'Asia', 'KUW': 'Asia', 'KGZ': 'Asia', 'LAO': 'Asia', 'LBN': 'Asia',
            'MAS': 'Asia', 'MDV': 'Asia', 'MGL': 'Asia', 'MYA': 'Asia', 'NEP': 'Asia',
            'PRK': 'Asia', 'OMA': 'Asia', 'PAK': 'Asia', 'PLE': 'Asia', 'PHI': 'Asia',
            'QAT': 'Asia', 'KOR': 'Asia', 'KSA': 'Asia', 'SGP': 'Asia', 'SRI': 'Asia',
            'SYR': 'Asia', 'TJK': 'Asia', 'THA': 'Asia', 'TLS': 'Asia', 'TKM': 'Asia',
            'UAE': 'Asia', 'UZB': 'Asia', 'VIE': 'Asia', 'YEM': 'Asia',
            
            # Africa
            'ALG': 'Africa', 'ANG': 'Africa', 'BEN': 'Africa', 'BOT': 'Africa', 'BUR': 'Africa',
            'BDI': 'Africa', 'CMR': 'Africa', 'CPV': 'Africa', 'CAF': 'Africa', 'CHA': 'Africa',
            'COM': 'Africa', 'CGO': 'Africa', 'COD': 'Africa', 'CIV': 'Africa', 'DJI': 'Africa',
            'EGY': 'Africa', 'GEQ': 'Africa', 'ERI': 'Africa', 'ETH': 'Africa', 'GAB': 'Africa',
            'GAM': 'Africa', 'GHA': 'Africa', 'GUI': 'Africa', 'GBS': 'Africa', 'KEN': 'Africa',
            'LES': 'Africa', 'LBR': 'Africa', 'LBA': 'Africa', 'MAD': 'Africa', 'MAW': 'Africa',
            'MLI': 'Africa', 'MTN': 'Africa', 'MRI': 'Africa', 'MAR': 'Africa', 'MOZ': 'Africa',
            'NAM': 'Africa', 'NIG': 'Africa', 'NGR': 'Africa', 'RWA': 'Africa', 'STP': 'Africa',
            'SEN': 'Africa', 'SEY': 'Africa', 'SLE': 'Africa', 'SOM': 'Africa', 'RSA': 'Africa',
            'SSD': 'Africa', 'SUD': 'Africa', 'TAN': 'Africa', 'TOG': 'Africa', 'TUN': 'Africa',
            'UGA': 'Africa', 'ZAM': 'Africa', 'ZIM': 'Africa',
            
            # North America
            'ATG': 'North America', 'BAH': 'North America', 'BAR': 'North America', 'BIZ': 'North America',
            'BER': 'North America', 'CAN': 'North America', 'CAY': 'North America', 'CRC': 'North America',
            'CUB': 'North America', 'DMA': 'North America', 'DOM': 'North America', 'SLV': 'North America',
            'GRN': 'North America', 'GUA': 'North America', 'HAI': 'North America', 'HON': 'North America',
            'JAM': 'North America', 'MEX': 'North America', 'NCA': 'North America', 'PAN': 'North America',
            'PUR': 'North America', 'SKN': 'North America', 'LCA': 'North America', 'VIN': 'North America',
            'TTO': 'North America', 'USA': 'North America', 'ISV': 'North America',
            
            # South America
            'ARG': 'South America', 'ARU': 'South America', 'BOL': 'South America', 'BRA': 'South America',
            'CHI': 'South America', 'COL': 'South America', 'ECU': 'South America', 'GUY': 'South America',
            'PAR': 'South America', 'PER': 'South America', 'SUR': 'South America', 'URU': 'South America',
            'VEN': 'South America',
            
            # Oceania
            'ASA': 'Oceania', 'AUS': 'Oceania', 'COK': 'Oceania', 'FIJ': 'Oceania', 'GUM': 'Oceania',
            'KIR': 'Oceania', 'MHL': 'Oceania', 'FSM': 'Oceania', 'NRU': 'Oceania', 'NZL': 'Oceania',
            'PLW': 'Oceania', 'PNG': 'Oceania', 'SAM': 'Oceania', 'SOL': 'Oceania', 'TGA': 'Oceania',
            'TUV': 'Oceania', 'VAN': 'Oceania',
        }
        
        df['continent'] = df['code'].map(continent_mapping)
        
        return df
    
    # --- NETTOYAGE DES ÉVÉNEMENTS ---
    @st.cache_data
    def clean_events(_self) -> pd.DataFrame:
        """Clean events.csv file"""
        df = pd.read_csv(_self.data_path / 'events.csv')
        df.columns = df.columns.str.strip().str.lower()
        
        # Remove duplicates
        df = df.drop_duplicates()
        
        # Strip whitespace from string columns
        for col in df.select_dtypes(include=['object']).columns:
            df[col] = df[col].str.strip()
        
        return df
    
    # --- NETTOYAGE DES CALENDRIERS ---
    @st.cache_data
    def clean_schedules(_self) -> pd.DataFrame:
        """Clean schedules.csv file"""
        # Assurez-vous que le nom du fichier est correct : schedules.csv
        try:
            df = pd.read_csv(_self.data_path / 'schedules.csv')
        except FileNotFoundError:
            try:
                # Tentative avec un nom alternatif au cas où l'utilisateur l'aurait nommé ainsi
                df = pd.read_csv(_self.data_path / 'schedule.csv')
            except FileNotFoundError:
                st.error("Erreur: schedules.csv ou schedule.csv non trouvé.")
                return pd.DataFrame()
                
        df.columns = df.columns.str.strip().str.lower()
        
        # Parse datetime columns
        if 'start_date' in df.columns:
            df['start_date'] = pd.to_datetime(df['start_date'], errors='coerce')
        if 'end_date' in df.columns:
            df['end_date'] = pd.to_datetime(df['end_date'], errors='coerce')
        
        return df
    
    # --- NETTOYAGE DES SITES ---
    @st.cache_data
    def clean_venues(_self) -> pd.DataFrame:
        """Clean venues.csv file"""
        df = pd.read_csv(_self.data_path / 'venues.csv')
        df.columns = df.columns.str.strip().str.lower()
        
        # Remove duplicates
        df = df.drop_duplicates()
        
        # Clean numeric coordinates
        if 'lat' in df.columns:
            df['lat'] = pd.to_numeric(df['lat'], errors='coerce')
        if 'lon' in df.columns:
            df['lon'] = pd.to_numeric(df['lon'], errors='coerce')
        
        return df
    
    # --- NETTOYAGE DES COACHS ---
    @st.cache_data
    def clean_coaches(_self) -> pd.DataFrame:
        """Clean coaches.csv file"""
        df = pd.read_csv(_self.data_path / 'coaches.csv')
        df.columns = df.columns.str.strip().str.lower()
        
        # 🛑 FILTRE NOC
        df = _self._exclude_noc(df, noc_column_name='noc')
        
        # Remove duplicates
        df = df.drop_duplicates()
        
        # Strip whitespace from string columns
        for col in df.select_dtypes(include=['object']).columns:
            df[col] = df[col].str.strip()
        
        return df
    
    # --- NETTOYAGE DES ÉQUIPES ---
    @st.cache_data
    def clean_teams(_self) -> pd.DataFrame:
        """Clean teams.csv file"""
        df = pd.read_csv(_self.data_path / 'teams.csv')
        df.columns = df.columns.str.strip().str.lower()
        
        # 🛑 FILTRE NOC
        df = _self._exclude_noc(df, noc_column_name='noc')
        
        # Remove duplicates
        df = df.drop_duplicates()
        
        return df


# 🚀 FONCTION PRINCIPALE DE CHARGEMENT : C'est celle que vos pages Streamlit appelleront.
@st.cache_data
def load_all_data(data_path='data') -> dict:
    """
    Load and clean all Olympic datasets with caching
    
    Args:
        data_path (str): Path to the directory containing CSV files
        
    Returns:
        dict: Dictionary containing all cleaned dataframes
    """
    cleaner = OlympicDataCleaner(data_path)
    data = {}
    
    # L'utilisation du bloc try/except permet à l'application de continuer même si un fichier manque.
    try:
        data['athletes'] = cleaner.clean_athletes()
    except Exception as e:
        st.warning(f"Could not load athletes data: {e}")
    
    try:
        data['medals'] = cleaner.clean_medals()
    except Exception as e:
        st.warning(f"Could not load medals data: {e}")
    
    try:
        data['medals_total'] = cleaner.clean_medals_total()
    except Exception as e:
        st.warning(f"Could not load medals_total data: {e}")
    
    try:
        data['medalists'] = cleaner.clean_medalists()
    except Exception as e:
        st.warning(f"Could not load medalists data: {e}")
    
    try:
        data['nocs'] = cleaner.clean_nocs()
    except Exception as e:
        st.warning(f"Could not load nocs data: {e}")
    
    try:
        data['events'] = cleaner.clean_events()
    except Exception as e:
        st.warning(f"Could not load events data: {e}")
    
    try:
        data['schedules'] = cleaner.clean_schedules()
    except Exception as e:
        st.warning(f"Could not load schedules data: {e}")
    
    try:
        data['venues'] = cleaner.clean_venues()
    except Exception as e:
        st.warning(f"Could not load venues data: {e}")
    
    try:
        data['coaches'] = cleaner.clean_coaches()
    except Exception as e:
        st.warning(f"Could not load coaches data: {e}")
    
    try:
        data['teams'] = cleaner.clean_teams()
    except Exception as e:
        st.warning(f"Could not load teams data: {e}")
    
    return data