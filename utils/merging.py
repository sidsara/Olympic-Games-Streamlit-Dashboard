"""
Olympic Games Data Merging Script
==================================
This script creates merged datasets by combining cleaned CSV files
to facilitate analysis in the Streamlit dashboard.

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


def create_athletes_enriched():
    """
    Create athletes_enriched.csv
    Combines: athletes + nocs (for continent) + teams (for team info) + coaches
    
    Used in: Page 3 (Athlete Performance - Complete profile cards with all athlete details)
    """
    print("Creating athletes_enriched.csv...")
    
    # Load cleaned data
    athletes = pd.read_csv(DATA_DIR / 'athletes_cleaned.csv')
    nocs = pd.read_csv(DATA_DIR / 'nocs_cleaned.csv')
    teams = pd.read_csv(DATA_DIR / 'teams_cleaned.csv')
    coaches = pd.read_csv(DATA_DIR / 'coaches_cleaned.csv')
    
    # Merge with NOCs to get continent
    athletes_enriched = athletes.merge(
        nocs[['code', 'continent']], 
        left_on='country_code', 
        right_on='code', 
        how='left',
        suffixes=('', '_noc')
    )
    athletes_enriched = athletes_enriched.drop('code_noc', axis=1, errors='ignore')
    
    # Add team information (for team sports)
    # Create a mapping from athlete code to team info
    teams_expanded = teams.copy()
    teams_expanded['athletes_codes_list'] = teams_expanded['athletes_codes'].str.split(';')
    
    # Create a dictionary mapping athlete codes to team names
    athlete_to_team = {}
    athlete_to_coaches = {}
    
    for _, row in teams_expanded.iterrows():
        if pd.notna(row['athletes_codes_list']) and isinstance(row['athletes_codes_list'], list):
            for athlete_code in row['athletes_codes_list']:
                athlete_code = athlete_code.strip()
                if athlete_code:
                    athlete_to_team[athlete_code] = row['team']
                    athlete_to_coaches[athlete_code] = row['coaches']
    
    # Add team and coaches info to athletes
    athletes_enriched['team_name'] = athletes_enriched['code'].map(athlete_to_team)
    athletes_enriched['team_coaches'] = athletes_enriched['code'].map(athlete_to_coaches)
    
    # Combine individual coach info with team coaches
    athletes_enriched['all_coaches'] = athletes_enriched.apply(
        lambda row: row['coach'] if pd.notna(row['coach']) and row['coach'] != 'N/A' 
        else row['team_coaches'] if pd.notna(row['team_coaches']) 
        else 'N/A', 
        axis=1
    )
    
    # Save enriched data
    athletes_enriched.to_csv(DATA_DIR / 'athletes_enriched.csv', index=False)
    print(f"✓ Created athletes_enriched: {len(athletes_enriched)} records, {len(athletes_enriched.columns)} columns")
    return athletes_enriched


def create_medals_enriched():
    """
    Create medals_enriched.csv
    Combines: medals + nocs (for continent) + athletes (for age/demographics)
    
    Used in: Page 1 (Overview - Medal distribution)
             Page 2 (Global Analysis - All medal visualizations by continent/country)
             Page 3 (Athlete Performance - Top athletes analysis)
    """
    print("Creating medals_enriched.csv...")
    
    # Load cleaned data
    medals = pd.read_csv(DATA_DIR / 'medals_cleaned.csv')
    nocs = pd.read_csv(DATA_DIR / 'nocs_cleaned.csv')
    athletes = pd.read_csv(DATA_DIR / 'athletes_cleaned.csv')
    
    # Convert code to string for consistent merging
    medals['code'] = medals['code'].astype(str)
    athletes['code'] = athletes['code'].astype(str)
    
    # Merge with NOCs to get continent
    medals_enriched = medals.merge(
        nocs[['code', 'continent']], 
        left_on='country_code', 
        right_on='code', 
        how='left',
        suffixes=('', '_noc')
    )
    medals_enriched = medals_enriched.drop('code_noc', axis=1, errors='ignore')
    
    # Merge with athletes to get age and other demographics
    medals_enriched = medals_enriched.merge(
        athletes[['code', 'age', 'height', 'weight', 'birth_place']], 
        left_on='code', 
        right_on='code', 
        how='left',
        suffixes=('', '_athlete')
    )
    
    # Create medal rank (Gold=1, Silver=2, Bronze=3)
    medal_rank = {'Gold': 1, 'Silver': 2, 'Bronze': 3}
    medals_enriched['medal_rank'] = medals_enriched['medal_type'].map(medal_rank)
    
    # Create binary columns for each medal type (useful for filtering)
    medals_enriched['is_gold'] = (medals_enriched['medal_type'] == 'Gold').astype(int)
    medals_enriched['is_silver'] = (medals_enriched['medal_type'] == 'Silver').astype(int)
    medals_enriched['is_bronze'] = (medals_enriched['medal_type'] == 'Bronze').astype(int)
    
    # Save enriched data
    medals_enriched.to_csv(DATA_DIR / 'medals_enriched.csv', index=False)
    print(f"✓ Created medals_enriched: {len(medals_enriched)} records, {len(medals_enriched.columns)} columns")
    return medals_enriched


def create_medals_total_enriched():
    """
    Create medals_total_enriched.csv
    Combines: medals_total + nocs (for continent and full country info)
    
    Used in: Page 1 (Overview - Top 10 standings, KPIs)
             Page 2 (Global Analysis - World map, continent comparisons, country rankings)
    """
    print("Creating medals_total_enriched.csv...")
    
    # Load cleaned data
    medals_total = pd.read_csv(DATA_DIR / 'medals_total_cleaned.csv')
    nocs = pd.read_csv(DATA_DIR / 'nocs_cleaned.csv')
    
    # Merge with NOCs to get continent
    medals_total_enriched = medals_total.merge(
        nocs[['code', 'continent']], 
        left_on='country_code', 
        right_on='code', 
        how='left',
        suffixes=('', '_noc')
    )
    medals_total_enriched = medals_total_enriched.drop('code_noc', axis=1, errors='ignore')
    
    # Calculate additional metrics
    medals_total_enriched['gold_ratio'] = (
        medals_total_enriched['Gold Medal'] / medals_total_enriched['Total']
    ).fillna(0).round(3)
    
    medals_total_enriched['silver_ratio'] = (
        medals_total_enriched['Silver Medal'] / medals_total_enriched['Total']
    ).fillna(0).round(3)
    
    medals_total_enriched['bronze_ratio'] = (
        medals_total_enriched['Bronze Medal'] / medals_total_enriched['Total']
    ).fillna(0).round(3)
    
    # Create medal quality score (Gold=3, Silver=2, Bronze=1)
    medals_total_enriched['medal_quality_score'] = (
        medals_total_enriched['Gold Medal'] * 3 + 
        medals_total_enriched['Silver Medal'] * 2 + 
        medals_total_enriched['Bronze Medal'] * 1
    )
    
    # Rank countries
    medals_total_enriched['rank_by_total'] = medals_total_enriched['Total'].rank(
        method='min', ascending=False
    ).astype(int)
    
    medals_total_enriched['rank_by_gold'] = medals_total_enriched['Gold Medal'].rank(
        method='min', ascending=False
    ).astype(int)
    
    medals_total_enriched['rank_by_quality'] = medals_total_enriched['medal_quality_score'].rank(
        method='min', ascending=False
    ).astype(int)
    
    # Sort by total medals descending
    medals_total_enriched = medals_total_enriched.sort_values('Total', ascending=False)
    
    # Save enriched data
    medals_total_enriched.to_csv(DATA_DIR / 'medals_total_enriched.csv', index=False)
    print(f"✓ Created medals_total_enriched: {len(medals_total_enriched)} records, {len(medals_total_enriched.columns)} columns")
    return medals_total_enriched


def create_events_enriched():
    """
    Create events_enriched.csv
    Combines: events + schedules (for timing info) + venues (for location)
    
    Used in: Page 4 (Sports and Events - All event visualizations)
    """
    print("Creating events_enriched.csv...")
    
    # Load cleaned data
    events = pd.read_csv(DATA_DIR / 'events_cleaned.csv')
    schedules = pd.read_csv(DATA_DIR / 'schedules_cleaned.csv')
    venues = pd.read_csv(DATA_DIR / 'venues_cleaned.csv')
    
    # Merge events with schedules
    events_enriched = events.merge(
        schedules[['event', 'discipline', 'start_date', 'end_date', 'venue', 
                   'phase', 'gender', 'status', 'day_of_week', 'duration_hours']],
        on='event',
        how='left',
        suffixes=('', '_schedule')
    )
    
    # Handle multiple schedules per event (keep the earliest start date)
    events_enriched = events_enriched.sort_values('start_date')
    events_enriched = events_enriched.drop_duplicates(subset=['event', 'sport'], keep='first')
    
    # Merge with venues to get location info
    events_enriched = events_enriched.merge(
        venues[['venue', 'latitude', 'longitude', 'date_start', 'date_end']],
        on='venue',
        how='left',
        suffixes=('', '_venue')
    )
    
    # Parse dates
    events_enriched['start_date'] = pd.to_datetime(events_enriched['start_date'], errors='coerce')
    events_enriched['end_date'] = pd.to_datetime(events_enriched['end_date'], errors='coerce')
    
    # Extract date components
    events_enriched['start_day'] = events_enriched['start_date'].dt.day
    events_enriched['start_month'] = events_enriched['start_date'].dt.month
    events_enriched['start_hour'] = events_enriched['start_date'].dt.hour
    
    # Save enriched data
    events_enriched.to_csv(DATA_DIR / 'events_enriched.csv', index=False)
    print(f"✓ Created events_enriched: {len(events_enriched)} records, {len(events_enriched.columns)} columns")
    return events_enriched


def create_medalists_enriched():
    """
    Create medalists_enriched.csv
    Combines: medalists + nocs (for continent) + events (for sport details)
    
    Used in: Page 3 (Athlete Performance - Top medalists)
             Page 4 (Sports and Events - Medal analysis by sport)
    """
    print("Creating medalists_enriched.csv...")
    
    # Load cleaned data
    medalists = pd.read_csv(DATA_DIR / 'medalists_cleaned.csv')
    nocs = pd.read_csv(DATA_DIR / 'nocs_cleaned.csv')
    events = pd.read_csv(DATA_DIR / 'events_cleaned.csv')
    
    # Convert code_athlete to string for consistent handling
    if 'code_athlete' in medalists.columns:
        medalists['code_athlete'] = medalists['code_athlete'].astype(str)
    
    # Merge with NOCs to get continent
    medalists_enriched = medalists.merge(
        nocs[['code', 'continent']], 
        left_on='country_code', 
        right_on='code', 
        how='left',
        suffixes=('', '_noc')
    )
    medalists_enriched = medalists_enriched.drop('code_noc', axis=1, errors='ignore')
    
    # Merge with events to get sport info
    medalists_enriched = medalists_enriched.merge(
        events[['event', 'sport', 'sport_code']],
        on='event',
        how='left',
        suffixes=('', '_event')
    )
    
    # Calculate age at medal winning
    medalists_enriched['birth_date'] = pd.to_datetime(medalists_enriched['birth_date'], errors='coerce')
    medalists_enriched['medal_date'] = pd.to_datetime(medalists_enriched['medal_date'], errors='coerce')
    
    medalists_enriched['age_at_medal'] = (
        (medalists_enriched['medal_date'] - medalists_enriched['birth_date']).dt.days / 365.25
    ).round(0).astype('Int64')
    
    # Create medal rank
    medal_rank = {'Gold': 1, 'Silver': 2, 'Bronze': 3}
    medalists_enriched['medal_rank'] = medalists_enriched['medal_type'].map(medal_rank)
    
    # Save enriched data
    medalists_enriched.to_csv(DATA_DIR / 'medalists_enriched.csv', index=False)
    print(f"✓ Created medalists_enriched: {len(medalists_enriched)} records, {len(medalists_enriched.columns)} columns")
    return medalists_enriched


def create_continent_summary():
    """
    Create continent_summary.csv
    Aggregates medal data by continent for quick analysis
    
    Used in: Page 2 (Global Analysis - Continent vs Medals bar chart, hierarchical views)
    """
    print("Creating continent_summary.csv...")
    
    # Load medals_total_enriched
    medals_total_enriched = pd.read_csv(DATA_DIR / 'medals_total_enriched.csv')
    
    # Group by continent
    continent_summary = medals_total_enriched.groupby('continent').agg({
        'Gold Medal': 'sum',
        'Silver Medal': 'sum',
        'Bronze Medal': 'sum',
        'Total': 'sum',
        'country_code': 'count'  # Number of countries
    }).reset_index()
    
    # Rename columns
    continent_summary = continent_summary.rename(columns={
        'country_code': 'num_countries'
    })
    
    # Calculate ratios
    continent_summary['gold_ratio'] = (
        continent_summary['Gold Medal'] / continent_summary['Total']
    ).fillna(0).round(3)
    
    continent_summary['avg_medals_per_country'] = (
        continent_summary['Total'] / continent_summary['num_countries']
    ).round(2)
    
    # Sort by total medals
    continent_summary = continent_summary.sort_values('Total', ascending=False)
    
    # Save summary
    continent_summary.to_csv(DATA_DIR / 'continent_summary.csv', index=False)
    print(f"✓ Created continent_summary: {len(continent_summary)} records, {len(continent_summary.columns)} columns")
    return continent_summary


def create_sport_summary():
    """Create sport-level summary statistics"""
    print("Creating sport_summary.csv...")
    
    medalists = pd.read_csv(DATA_DIR / 'medalists_enriched.csv')
    events = pd.read_csv(DATA_DIR / 'events_enriched.csv')
    
    # Count unique disciplines per sport
    discipline_counts = medalists.groupby('sport')['discipline'].nunique().reset_index(name='num_disciplines')
    
    # Count events per sport (use 'event' column, not 'event_name')
    event_counts = events.groupby('sport')['event'].nunique().reset_index(name='num_events')
    
    # Count athletes per sport (use 'name' column from medalists)
    athlete_counts = medalists.groupby('sport')['name'].nunique().reset_index(name='num_athletes')
    
    # Count medals by type per sport
    medal_counts = medalists.groupby(['sport', 'medal_type']).size().reset_index(name='count')
    medal_pivot = medal_counts.pivot(index='sport', columns='medal_type', values='count').fillna(0).reset_index()
    
    # Ensure all medal type columns exist
    for col in ['Bronze Medal', 'Gold Medal', 'Silver Medal']:
        if col not in medal_pivot.columns:
            medal_pivot[col] = 0
    
    medal_pivot.columns.name = None
    medal_pivot = medal_pivot.rename(columns={
        'Bronze Medal': 'Bronze Medal',
        'Gold Medal': 'Gold Medal', 
        'Silver Medal': 'Silver Medal'
    })
    
    medal_pivot['total_medals'] = (
        medal_pivot['Gold Medal'] + 
        medal_pivot['Silver Medal'] + 
        medal_pivot['Bronze Medal']
    )
    
    # Merge all summaries
    sport_summary = discipline_counts.merge(event_counts, on='sport', how='left')
    sport_summary = sport_summary.merge(athlete_counts, on='sport', how='left')
    sport_summary = sport_summary.merge(medal_pivot, on='sport', how='left')
    
    # Fill NaN with 0
    sport_summary = sport_summary.fillna(0)
    
    # Sort by total medals
    sport_summary = sport_summary.sort_values('total_medals', ascending=False)
    
    # Save
    sport_summary.to_csv(DATA_DIR / 'sport_summary.csv', index=False)
    print(f"✓ Created sport_summary: {len(sport_summary)} records, {len(sport_summary.columns)} columns")
    
    return sport_summary


def create_athlete_medals_summary():
    """
    Create athlete_medals_summary.csv
    Aggregates medals per athlete for top performer analysis
    
    Used in: Page 3 (Athlete Performance - Top Athletes by Medals bar chart)
    """
    print("Creating athlete_medals_summary.csv...")
    
    # Load data
    medalists = pd.read_csv(DATA_DIR / 'medalists_enriched.csv')
    athletes = pd.read_csv(DATA_DIR / 'athletes_enriched.csv')
    
    # Convert codes to string for consistent merging
    if 'code_athlete' in medalists.columns:
        medalists['code_athlete'] = medalists['code_athlete'].astype(str)
    athletes['code'] = athletes['code'].astype(str)
    
    # Count medals by athlete and type
    athlete_medals = medalists.groupby(['name', 'country_code', 'country', 'gender', 'continent'])['medal_type'].value_counts().unstack(fill_value=0)
    athlete_medals = athlete_medals.reset_index()
    
    # The columns from unstack will be 'Gold Medal', 'Silver Medal', 'Bronze Medal'
    # Ensure all medal columns exist
    for col in ['Gold Medal', 'Silver Medal', 'Bronze Medal']:
        if col not in athlete_medals.columns:
            athlete_medals[col] = 0
    
    # Calculate total medals
    athlete_medals['total_medals'] = (
        athlete_medals['Gold Medal'] + 
        athlete_medals['Silver Medal'] + 
        athlete_medals['Bronze Medal']
    )
    
    # Calculate quality score
    athlete_medals['medal_quality_score'] = (
        athlete_medals['Gold Medal'] * 3 + 
        athlete_medals['Silver Medal'] * 2 + 
        athlete_medals['Bronze Medal'] * 1
    )
    
    # Merge with athletes to get additional info (age, sport, etc.)
    athlete_medals = athlete_medals.merge(
        athletes[['name', 'code', 'age', 'disciplines']],
        on='name',
        how='left',
        suffixes=('', '_athlete')
    )
    
    # Sort by total medals, then by quality score
    athlete_medals = athlete_medals.sort_values(
        ['total_medals', 'medal_quality_score'], 
        ascending=[False, False]
    )
    
    # Add rank
    athlete_medals['rank'] = range(1, len(athlete_medals) + 1)
    
    # Save summary
    athlete_medals.to_csv(DATA_DIR / 'athlete_medals_summary.csv', index=False)
    print(f"✓ Created athlete_medals_summary: {len(athlete_medals)} records, {len(athlete_medals.columns)} columns")
    return athlete_medals


def create_gender_distribution():
    """
    Create gender_distribution.csv
    Analyzes gender distribution across countries, continents, and sports
    
    Used in: Page 3 (Athlete Performance - Gender Distribution visualizations)
    """
    print("Creating gender_distribution.csv...")
    
    # Load data
    athletes = pd.read_csv(DATA_DIR / 'athletes_enriched.csv')
    
    # Overall gender distribution
    overall = athletes['gender'].value_counts().reset_index()
    overall.columns = ['gender', 'count']
    overall['category'] = 'Overall'
    overall['subcategory'] = 'All'
    
    # Gender by continent
    by_continent = athletes.groupby(['continent', 'gender']).size().reset_index(name='count')
    by_continent['category'] = 'Continent'
    by_continent = by_continent.rename(columns={'continent': 'subcategory'})
    
    # Gender by country (top 30 countries by athlete count)
    top_countries = athletes['country'].value_counts().head(30).index
    by_country = athletes[athletes['country'].isin(top_countries)].groupby(['country', 'gender']).size().reset_index(name='count')
    by_country['category'] = 'Country'
    by_country = by_country.rename(columns={'country': 'subcategory'})
    
    # Gender by sport
    # First, expand disciplines (athletes may compete in multiple)
    athletes_expanded = athletes.copy()
    athletes_expanded['disciplines'] = athletes_expanded['disciplines'].str.split(',')
    athletes_expanded = athletes_expanded.explode('disciplines')
    athletes_expanded['disciplines'] = athletes_expanded['disciplines'].str.strip()
    
    by_sport = athletes_expanded.groupby(['disciplines', 'gender']).size().reset_index(name='count')
    by_sport['category'] = 'Sport'
    by_sport = by_sport.rename(columns={'disciplines': 'subcategory'})
    
    # Combine all
    gender_distribution = pd.concat([overall, by_continent, by_country, by_sport], ignore_index=True)
    
    # Calculate percentages within each category
    gender_distribution['total_in_category'] = gender_distribution.groupby(['category', 'subcategory'])['count'].transform('sum')
    gender_distribution['percentage'] = (
        gender_distribution['count'] / gender_distribution['total_in_category'] * 100
    ).round(2)
    
    # Save distribution
    gender_distribution.to_csv(DATA_DIR / 'gender_distribution.csv', index=False)
    print(f"✓ Created gender_distribution: {len(gender_distribution)} records, {len(gender_distribution.columns)} columns")
    return gender_distribution


def main():
    """
    Main function to run all merging operations
    """
    print("\n" + "="*60)
    print("OLYMPIC GAMES DATA MERGING PROCESS")
    print("="*60 + "\n")
    
    # Create all merged datasets
    create_athletes_enriched()
    create_medals_enriched()
    create_medals_total_enriched()
    create_events_enriched()
    create_medalists_enriched()
    create_continent_summary()
    create_sport_summary()
    create_athlete_medals_summary()
    create_gender_distribution()
    
    print("\n" + "="*60)
    print("✓ ALL DATASETS MERGED SUCCESSFULLY!")
    print("="*60 + "\n")
    
    # Print summary of created files
    print("Created Merged Files:")
    print("-" * 60)
    
    merged_files = [
        'athletes_enriched.csv',
        'medals_enriched.csv',
        'medals_total_enriched.csv',
        'events_enriched.csv',
        'medalists_enriched.csv',
        'continent_summary.csv',
        'sport_summary.csv',
        'athlete_medals_summary.csv',
        'gender_distribution.csv'
    ]
    
    for file in merged_files:
        filepath = DATA_DIR / file
        if filepath.exists():
            df = pd.read_csv(filepath)
            print(f"{file:35s}: {len(df):6d} records, {len(df.columns):3d} columns")
        else:
            print(f"{file:35s}: ❌ NOT FOUND")
    
    print("-" * 60)
    print("\n📊 Data Pipeline Complete!")
    print("Your enriched datasets are ready for the Streamlit dashboard!")
    print("\nNext steps:")
    print("1. Review the merged files in the data/ directory")
    print("2. Start building your Streamlit pages")
    print("3. Use these enriched datasets for powerful visualizations\n")


if __name__ == "__main__":
    main()