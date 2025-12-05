"""
Olympic Games Data Cleaning Script
===================================
This script cleans and preprocesses all datasets from the Paris 2024 Olympics
for use in the Streamlit dashboard application.

Author: Your Name
Date: December 2024
"""

import pandas as pd
import numpy as np
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# Define paths
DATA_DIR = Path(__file__).parent.parent / 'data'

def clean_athletes():
    """
    Clean athletes.csv
    Used in: Page 1 (Overview - Total Athletes KPI)
             Page 3 (Athlete Performance - Profile Cards, Age Distribution, Gender Distribution, Top Athletes)
    """
    print("Cleaning athletes.csv...")
    df = pd.read_csv(DATA_DIR / 'athletes.csv')
    
    # Remove duplicates
    df = df.drop_duplicates(subset=['code'], keep='first')
    
    # Handle missing values
    df['name'] = df['name'].fillna('Unknown')
    df['name_short'] = df['name_short'].fillna(df['name'])
    df['gender'] = df['gender'].fillna('Unknown')
    df['country_code'] = df['country_code'].fillna('UNK')
    df['country'] = df['country'].fillna('Unknown')
    df['country_long'] = df['country_long'].fillna(df['country'])
    
    # Clean height and weight (convert to numeric)
    df['height'] = pd.to_numeric(df['height'], errors='coerce')
    df['weight'] = pd.to_numeric(df['weight'], errors='coerce')
    
    # Parse birth_date and calculate age
    df['birth_date'] = pd.to_datetime(df['birth_date'], errors='coerce')
    olympics_date = pd.Timestamp('2024-07-26')  # Opening ceremony date
    df['age'] = (olympics_date - df['birth_date']).dt.days / 365.25
    df['age'] = df['age'].round(0).astype('Int64')  # Use nullable integer
    
    # Clean disciplines and events (handle multiple values)
    df['disciplines'] = df['disciplines'].fillna('Unknown')
    df['events'] = df['events'].fillna('Unknown')
    
    # Clean text fields
    text_columns = ['birth_place', 'birth_country', 'residence_place', 'residence_country', 
                    'nickname', 'hobbies', 'occupation', 'education', 'coach']
    for col in text_columns:
        if col in df.columns:
            df[col] = df[col].fillna('N/A')
    
    # Save cleaned data
    df.to_csv(DATA_DIR / 'athletes_cleaned.csv', index=False)
    print(f"✓ Cleaned athletes: {len(df)} records")
    return df


def clean_coaches():
    """
    Clean coaches.csv
    Used in: Page 3 (Athlete Performance - Profile Cards for coach information)
    """
    print("Cleaning coaches.csv...")
    df = pd.read_csv(DATA_DIR / 'coaches.csv')
    
    # Remove duplicates
    df = df.drop_duplicates(subset=['code'], keep='first')
    
    # Handle missing values
    df['name'] = df['name'].fillna('Unknown')
    df['gender'] = df['gender'].fillna('Unknown')
    df['function'] = df['function'].fillna('Coach')
    df['country_code'] = df['country_code'].fillna('UNK')
    df['country'] = df['country'].fillna('Unknown')
    df['country_long'] = df['country_long'].fillna(df['country'])
    df['disciplines'] = df['disciplines'].fillna('Unknown')
    
    # Parse birth_date
    df['birth_date'] = pd.to_datetime(df['birth_date'], errors='coerce')
    
    # Save cleaned data
    df.to_csv(DATA_DIR / 'coaches_cleaned.csv', index=False)
    print(f"✓ Cleaned coaches: {len(df)} records")
    return df


def clean_events():
    """
    Clean events.csv
    Used in: Page 1 (Overview - Total Sports KPI, Number of Events KPI)
             Page 4 (Sports and Events - All event-related visualizations)
    """
    print("Cleaning events.csv...")
    df = pd.read_csv(DATA_DIR / 'events.csv')
    
    # Remove duplicates
    df = df.drop_duplicates(subset=['event', 'sport'], keep='first')
    
    # Handle missing values
    df['event'] = df['event'].fillna('Unknown Event')
    df['sport'] = df['sport'].fillna('Unknown Sport')
    df['sport_code'] = df['sport_code'].fillna('UNK')
    df['tag'] = df['tag'].fillna('')
    df['sport_url'] = df['sport_url'].fillna('')
    
    # Standardize text
    df['event'] = df['event'].str.strip()
    df['sport'] = df['sport'].str.strip()
    
    # Save cleaned data
    df.to_csv(DATA_DIR / 'events_cleaned.csv', index=False)
    print(f"✓ Cleaned events: {len(df)} records")
    return df


def clean_medalists():
    """
    Clean medalists.csv
    Used in: Page 3 (Athlete Performance - Top Athletes by Medals)
             Page 4 (Sports and Events - Medal analysis by sport)
    """
    print("Cleaning medalists.csv...")
    df = pd.read_csv(DATA_DIR / 'medalists.csv')
    
    # Remove duplicates
    df = df.drop_duplicates()
    
    # Handle missing values
    df['name'] = df['name'].fillna('Unknown')
    df['gender'] = df['gender'].fillna('Unknown')
    df['country_code'] = df['country_code'].fillna('UNK')
    df['country'] = df['country'].fillna('Unknown')
    df['country_long'] = df['country_long'].fillna(df['country'])
    df['discipline'] = df['discipline'].fillna('Unknown')
    df['event'] = df['event'].fillna('Unknown')
    df['medal_type'] = df['medal_type'].fillna('Unknown')
    
    # Parse dates
    df['medal_date'] = pd.to_datetime(df['medal_date'], errors='coerce')
    df['birth_date'] = pd.to_datetime(df['birth_date'], errors='coerce')
    
    # Clean medal codes
    df['medal_code'] = pd.to_numeric(df['medal_code'], errors='coerce').astype('Int64')
    
    # Standardize medal types
    medal_mapping = {
        'GOLD': 'Gold',
        'SILVER': 'Silver',
        'BRONZE': 'Bronze'
    }
    df['medal_type'] = df['medal_type'].str.upper().map(medal_mapping).fillna(df['medal_type'])
    
    # Save cleaned data
    df.to_csv(DATA_DIR / 'medalists_cleaned.csv', index=False)
    print(f"✓ Cleaned medalists: {len(df)} records")
    return df


def clean_medals():
    """
    Clean medals.csv
    Used in: Page 1 (Overview - Medal Distribution)
             Page 2 (Global Analysis - Medal maps and charts)
    """
    print("Cleaning medals.csv...")
    df = pd.read_csv(DATA_DIR / 'medals.csv')
    
    # Remove duplicates
    df = df.drop_duplicates()
    
    # Handle missing values
    df['name'] = df['name'].fillna('Unknown')
    df['gender'] = df['gender'].fillna('Unknown')
    df['country_code'] = df['country_code'].fillna('UNK')
    df['country'] = df['country'].fillna('Unknown')
    df['country_long'] = df['country_long'].fillna(df['country'])
    df['discipline'] = df['discipline'].fillna('Unknown')
    df['event'] = df['event'].fillna('Unknown')
    df['medal_type'] = df['medal_type'].fillna('Unknown')
    
    # Parse dates
    df['medal_date'] = pd.to_datetime(df['medal_date'], errors='coerce')
    
    # Clean medal codes
    df['medal_code'] = pd.to_numeric(df['medal_code'], errors='coerce').astype('Int64')
    
    # Standardize medal types
    medal_mapping = {
        'GOLD': 'Gold',
        'SILVER': 'Silver',
        'BRONZE': 'Bronze'
    }
    df['medal_type'] = df['medal_type'].str.upper().map(medal_mapping).fillna(df['medal_type'])
    
    # Save cleaned data
    df.to_csv(DATA_DIR / 'medals_cleaned.csv', index=False)
    print(f"✓ Cleaned medals: {len(df)} records")
    return df


def clean_medals_total():
    """
    Clean medals_total.csv
    Used in: Page 1 (Overview - Total Medals KPI, Top 10 Medal Standings)
             Page 2 (Global Analysis - World Medal Map, Continent comparisons)
    """
    print("Cleaning medals_total.csv...")
    df = pd.read_csv(DATA_DIR / 'medals_total.csv')
    
    # Remove duplicates
    df = df.drop_duplicates(subset=['country_code'], keep='first')
    
    # Handle missing values
    df['country_code'] = df['country_code'].fillna('UNK')
    df['country'] = df['country'].fillna('Unknown')
    df['country_long'] = df['country_long'].fillna(df['country'])
    
    # Clean medal columns (ensure they're numeric)
    medal_columns = ['Gold Medal', 'Silver Medal', 'Bronze Medal', 'Total']
    for col in medal_columns:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)
    
    # Verify Total column
    df['Total_calculated'] = df['Gold Medal'] + df['Silver Medal'] + df['Bronze Medal']
    if not df['Total'].equals(df['Total_calculated']):
        print("  ⚠ Warning: Total column mismatch detected, recalculating...")
        df['Total'] = df['Total_calculated']
    df = df.drop('Total_calculated', axis=1)
    
    # Remove countries with zero medals
    df = df[df['Total'] > 0]
    
    # Save cleaned data
    df.to_csv(DATA_DIR / 'medals_total_cleaned.csv', index=False)
    print(f"✓ Cleaned medals_total: {len(df)} records")
    return df


def clean_nocs():
    """
    Clean nocs.csv
    Used in: Page 1 (Overview - Total Countries KPI)
             Page 2 (Global Analysis - All geographical visualizations)
             All Pages (Global Filters - Country selection)
    """
    print("Cleaning nocs.csv...")
    df = pd.read_csv(DATA_DIR / 'nocs.csv')
    
    # Remove duplicates
    df = df.drop_duplicates(subset=['code'], keep='first')
    
    # Handle missing values
    df['code'] = df['code'].fillna('UNK')
    df['country'] = df['country'].fillna('Unknown')
    df['country_long'] = df['country_long'].fillna(df['country'])
    df['tag'] = df['tag'].fillna('')
    df['note'] = df['note'].fillna('')
    
    # Add continent information (manual mapping for geographical analysis)
    continent_mapping = {
        # Europe
        'ALB': 'Europe', 'AND': 'Europe', 'ARM': 'Europe', 'AUT': 'Europe', 'AZE': 'Europe',
        'BLR': 'Europe', 'BEL': 'Europe', 'BIH': 'Europe', 'BGR': 'Europe', 'HRV': 'Europe',
        'CYP': 'Europe', 'CZE': 'Europe', 'DEN': 'Europe', 'EST': 'Europe', 'FIN': 'Europe',
        'FRA': 'Europe', 'GEO': 'Europe', 'GER': 'Europe', 'GRE': 'Europe', 'HUN': 'Europe',
        'ISL': 'Europe', 'IRL': 'Europe', 'ISR': 'Europe', 'ITA': 'Europe', 'KOS': 'Europe',
        'LAT': 'Europe', 'LIE': 'Europe', 'LTU': 'Europe', 'LUX': 'Europe', 'MLT': 'Europe',
        'MDA': 'Europe', 'MON': 'Europe', 'MNE': 'Europe', 'NED': 'Europe', 'MKD': 'Europe',
        'NOR': 'Europe', 'POL': 'Europe', 'POR': 'Europe', 'ROU': 'Europe', 'SMR': 'Europe',
        'SRB': 'Europe', 'SVK': 'Europe', 'SLO': 'Europe', 'ESP': 'Europe', 'SWE': 'Europe',
        'SUI': 'Europe', 'TUR': 'Europe', 'UKR': 'Europe', 'GBR': 'Europe',
        
        # Asia
        'AFG': 'Asia', 'BRN': 'Asia', 'BAN': 'Asia', 'BHU': 'Asia', 'BRU': 'Asia',
        'CAM': 'Asia', 'CHN': 'Asia', 'TPE': 'Asia', 'IND': 'Asia', 'INA': 'Asia',
        'IRI': 'Asia', 'IRQ': 'Asia', 'JPN': 'Asia', 'JOR': 'Asia', 'KAZ': 'Asia',
        'KOR': 'Asia', 'PRK': 'Asia', 'KUW': 'Asia', 'KGZ': 'Asia', 'LAO': 'Asia',
        'LIB': 'Asia', 'MAS': 'Asia', 'MDV': 'Asia', 'MGL': 'Asia', 'MYA': 'Asia',
        'NEP': 'Asia', 'OMA': 'Asia', 'PAK': 'Asia', 'PLE': 'Asia', 'PHI': 'Asia',
        'QAT': 'Asia', 'KSA': 'Asia', 'SGP': 'Asia', 'SRI': 'Asia', 'SYR': 'Asia',
        'TJK': 'Asia', 'THA': 'Asia', 'TLS': 'Asia', 'TKM': 'Asia', 'UAE': 'Asia',
        'UZB': 'Asia', 'VIE': 'Asia', 'YEM': 'Asia', 'HKG': 'Asia',
        
        # Africa
        'ALG': 'Africa', 'ANG': 'Africa', 'BEN': 'Africa', 'BOT': 'Africa', 'BUR': 'Africa',
        'BDI': 'Africa', 'CMR': 'Africa', 'CPV': 'Africa', 'CAF': 'Africa', 'CHA': 'Africa',
        'COM': 'Africa', 'CGO': 'Africa', 'COD': 'Africa', 'CIV': 'Africa', 'DJI': 'Africa',
        'EGY': 'Africa', 'GEQ': 'Africa', 'ERI': 'Africa', 'SWZ': 'Africa', 'ETH': 'Africa',
        'GAB': 'Africa', 'GAM': 'Africa', 'GHA': 'Africa', 'GUI': 'Africa', 'GBS': 'Africa',
        'KEN': 'Africa', 'LES': 'Africa', 'LBR': 'Africa', 'LBA': 'Africa', 'MAD': 'Africa',
        'MAW': 'Africa', 'MLI': 'Africa', 'MTN': 'Africa', 'MRI': 'Africa', 'MAR': 'Africa',
        'MOZ': 'Africa', 'NAM': 'Africa', 'NIG': 'Africa', 'NGR': 'Africa', 'RWA': 'Africa',
        'STP': 'Africa', 'SEN': 'Africa', 'SEY': 'Africa', 'SLE': 'Africa', 'SOM': 'Africa',
        'RSA': 'Africa', 'SSD': 'Africa', 'SUD': 'Africa', 'TAN': 'Africa', 'TOG': 'Africa',
        'TUN': 'Africa', 'UGA': 'Africa', 'ZAM': 'Africa', 'ZIM': 'Africa',
        
        # North America
        'ATG': 'North America', 'ARU': 'North America', 'BAH': 'North America', 'BAR': 'North America',
        'BIZ': 'North America', 'BER': 'North America', 'VGB': 'North America', 'CAN': 'North America',
        'CAY': 'North America', 'CRC': 'North America', 'CUB': 'North America', 'DMA': 'North America',
        'DOM': 'North America', 'ESA': 'North America', 'GRN': 'North America', 'GUA': 'North America',
        'HAI': 'North America', 'HON': 'North America', 'JAM': 'North America', 'MEX': 'North America',
        'NCA': 'North America', 'PAN': 'North America', 'PUR': 'North America', 'SKN': 'North America',
        'LCA': 'North America', 'VIN': 'North America', 'TTO': 'North America', 'ISV': 'North America',
        'USA': 'North America',
        
        # South America
        'ARG': 'South America', 'BOL': 'South America', 'BRA': 'South America', 'CHI': 'South America',
        'COL': 'South America', 'ECU': 'South America', 'GUY': 'South America', 'PAR': 'South America',
        'PER': 'South America', 'SUR': 'South America', 'URU': 'South America', 'VEN': 'South America',
        
        # Oceania
        'ASA': 'Oceania', 'AUS': 'Oceania', 'COK': 'Oceania', 'FIJ': 'Oceania', 'GUM': 'Oceania',
        'KIR': 'Oceania', 'MHL': 'Oceania', 'FSM': 'Oceania', 'NRU': 'Oceania', 'NZL': 'Oceania',
        'PLW': 'Oceania', 'PNG': 'Oceania', 'SAM': 'Oceania', 'SOL': 'Oceania', 'TGA': 'Oceania',
        'TUV': 'Oceania', 'VAN': 'Oceania',
        
        # Special cases
        'ROT': 'Multiple', 'IOP': 'Multiple'  # Refugee Olympic Team, Independent Olympic Participants
    }
    
    df['continent'] = df['code'].map(continent_mapping).fillna('Unknown')
    
    # Save cleaned data
    df.to_csv(DATA_DIR / 'nocs_cleaned.csv', index=False)
    print(f"✓ Cleaned nocs: {len(df)} records")
    return df


def clean_schedules():
    """
    Clean schedules.csv
    Used in: Page 4 (Sports and Events - Event Schedule, Timeline/Gantt Chart)
    """
    print("Cleaning schedules.csv...")
    df = pd.read_csv(DATA_DIR / 'schedules.csv')
    
    # Remove duplicates
    df = df.drop_duplicates()
    
    # Handle missing values
    df['discipline'] = df['discipline'].fillna('Unknown')
    df['event'] = df['event'].fillna('Unknown')
    df['phase'] = df['phase'].fillna('Unknown')
    df['gender'] = df['gender'].fillna('Unknown')
    df['venue'] = df['venue'].fillna('Unknown')
    df['status'] = df['status'].fillna('Scheduled')
    
    # Parse dates
    df['start_date'] = pd.to_datetime(df['start_date'], errors='coerce')
    df['end_date'] = pd.to_datetime(df['end_date'], errors='coerce')
    
    # Create day of week column
    df['day_of_week'] = df['start_date'].dt.day_name()
    
    # Calculate duration in hours
    df['duration_hours'] = (df['end_date'] - df['start_date']).dt.total_seconds() / 3600
    
    # Clean codes
    df['discipline_code'] = df['discipline_code'].fillna('UNK')
    df['venue_code'] = df['venue_code'].fillna('UNK')
    df['location_code'] = df['location_code'].fillna('UNK')
    
    # Save cleaned data
    df.to_csv(DATA_DIR / 'schedules_cleaned.csv', index=False)
    print(f"✓ Cleaned schedules: {len(df)} records")
    return df


def clean_teams():
    """
    Clean teams.csv
    Used in: Page 3 (Athlete Performance - Team information in profile cards)
    """
    print("Cleaning teams.csv...")
    df = pd.read_csv(DATA_DIR / 'teams.csv')
    
    # Remove duplicates
    df = df.drop_duplicates(subset=['code'], keep='first')
    
    # Handle missing values
    df['team'] = df['team'].fillna('Unknown Team')
    df['team_gender'] = df['team_gender'].fillna('Unknown')
    df['country_code'] = df['country_code'].fillna('UNK')
    df['country'] = df['country'].fillna('Unknown')
    df['country_long'] = df['country_long'].fillna(df['country'])
    df['discipline'] = df['discipline'].fillna('Unknown')
    
    # Clean numeric columns
    df['num_athletes'] = pd.to_numeric(df['num_athletes'], errors='coerce').fillna(0).astype(int)
    df['num_coaches'] = pd.to_numeric(df['num_coaches'], errors='coerce').fillna(0).astype(int)
    
    # Clean list columns
    list_columns = ['athletes', 'coaches', 'athletes_codes', 'coaches_codes']
    for col in list_columns:
        if col in df.columns:
            df[col] = df[col].fillna('')
    
    # Save cleaned data
    df.to_csv(DATA_DIR / 'teams_cleaned.csv', index=False)
    print(f"✓ Cleaned teams: {len(df)} records")
    return df


def clean_venues():
    """
    Clean venues.csv
    Used in: Page 4 (Sports and Events - Venue Map)
    """
    print("Cleaning venues.csv...")
    df = pd.read_csv(DATA_DIR / 'venues.csv')
    
    # Remove duplicates
    df = df.drop_duplicates(subset=['venue'], keep='first')
    
    # Handle missing values
    df['venue'] = df['venue'].fillna('Unknown Venue')
    df['sports'] = df['sports'].fillna('Unknown')
    df['tag'] = df['tag'].fillna('')
    df['url'] = df['url'].fillna('')
    
    # Parse dates
    df['date_start'] = pd.to_datetime(df['date_start'], errors='coerce')
    df['date_end'] = pd.to_datetime(df['date_end'], errors='coerce')
    
    # Calculate duration in days
    df['duration_days'] = (df['date_end'] - df['date_start']).dt.days
    
    # Add coordinates for Paris venues (manual mapping for map visualization)
    venue_coordinates = {
        'Stade de France': (48.9244, 2.3601),
        'Aquatics Centre': (48.9279, 2.3619),
        'Paris La Défense Arena': (48.8959, 2.2287),
        'Eiffel Tower Stadium': (48.8584, 2.2945),
        'Grand Palais': (48.8662, 2.3124),
        'Invalides': (48.8566, 2.3122),
        'Champ de Mars Arena': (48.8556, 2.2986),
        'Trocadéro': (48.8620, 2.2876),
        'Pont Alexandre III': (48.8638, 2.3135),
        'Roland-Garros Stadium': (48.8467, 2.2520),
        'Bercy Arena': (48.8394, 2.3791),
        'Parc des Princes': (48.8415, 2.2530),
        'Porte de La Chapelle Arena': (48.8985, 2.3595),
        'North Paris Arena': (48.9342, 2.3601),
        'South Paris Arena': (48.8211, 2.3658),
        'Concorde': (48.8656, 2.3212),
        'La Concorde': (48.8656, 2.3212),
        'Château de Versailles': (48.8049, 2.1204),
        'Marina de Marseille': (43.2799, 5.3599),
        'Stade Vélodrome': (43.2698, 5.3958),
        'Stade de Lyon': (45.7652, 4.9821),
        'Stade Pierre-Mauroy': (50.6119, 3.1304),
        'Stade de Bordeaux': (44.8978, -0.5610),
        'Stade de Nice': (43.7053, 7.1926),
        'Stade Geoffroy-Guichard': (45.4608, 4.3900),
        'Tahiti': (-17.5334, -149.5668),
        'Teahupo\'o': (-17.8667, -149.2833),
    }
    
    df['latitude'] = df['venue'].map(lambda x: venue_coordinates.get(x, (48.8566, 2.3522))[0])
    df['longitude'] = df['venue'].map(lambda x: venue_coordinates.get(x, (48.8566, 2.3522))[1])
    
    # Save cleaned data
    df.to_csv(DATA_DIR / 'venues_cleaned.csv', index=False)
    print(f"✓ Cleaned venues: {len(df)} records")
    return df


def main():
    """
    Main function to run all cleaning operations
    """
    print("\n" + "="*60)
    print("OLYMPIC GAMES DATA CLEANING PROCESS")
    print("="*60 + "\n")
    
    # Clean all datasets
    clean_athletes()
    clean_coaches()
    clean_events()
    clean_medalists()
    clean_medals()
    clean_medals_total()
    clean_nocs()
    clean_schedules()
    clean_teams()
    clean_venues()
    
    print("\n" + "="*60)
    print("✓ ALL DATASETS CLEANED SUCCESSFULLY!")
    print("="*60 + "\n")
    
    # Print summary statistics
    print("Summary Statistics:")
    print("-" * 60)
    
    files = [
        'athletes_cleaned.csv', 'coaches_cleaned.csv', 'events_cleaned.csv',
        'medalists_cleaned.csv', 'medals_cleaned.csv', 'medals_total_cleaned.csv',
        'nocs_cleaned.csv', 'schedules_cleaned.csv', 'teams_cleaned.csv',
        'venues_cleaned.csv'
    ]
    
    for file in files:
        df = pd.read_csv(DATA_DIR / file)
        print(f"{file:30s}: {len(df):6d} records, {len(df.columns):3d} columns")
    
    print("-" * 60)
    print("\nCleaned files are ready for merging and dashboard creation!")
    print("Next step: Run merging.py to create combined datasets.\n")


if __name__ == "__main__":
    main()