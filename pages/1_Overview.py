"""
Paris 2024 Olympics Dashboard - Overview Page
==============================================
The Command Center: High-level summary and KPIs

Author: Your Name
Date: December 2024
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import sys

# Add utils to path
sys.path.append(str(Path(__file__).parent.parent))

from utils.ui import colored_header

# Page configuration
st.set_page_config(
    page_title="Paris 2024 Olympics - Overview",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #0066CC;
        text-align: center;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-container {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .stMetric {
        background-color: white;
        padding: 1rem;
        border-radius: 8px;
    }
    </style>
""", unsafe_allow_html=True)

# Data loading with caching
@st.cache_data
def load_data():
    """Load all necessary datasets"""
    data_dir = Path(__file__).parent.parent / 'data'
    
    return {
        'athletes': pd.read_csv(data_dir / 'athletes_cleaned.csv'),
        'nocs': pd.read_csv(data_dir / 'nocs_cleaned.csv'),
        'events': pd.read_csv(data_dir / 'events_cleaned.csv'),
        'medals_total': pd.read_csv(data_dir / 'medals_total_enriched.csv'),
        'medals': pd.read_csv(data_dir / 'medals_enriched.csv'),
        'continent_summary': pd.read_csv(data_dir / 'continent_summary.csv')
    }

# Load data
try:
    data = load_data()
except Exception as e:
    st.error(f"Error loading data: {e}")
    st.stop()

# ============================================================================
# SIDEBAR - GLOBAL FILTERS
# ============================================================================
st.sidebar.title("🎯 Global Filters")
st.sidebar.markdown("---")

# Get unique values for filters
all_countries = sorted(data['nocs']['country'].unique())
all_continents = sorted(data['nocs']['continent'].unique())
all_sports = sorted(data['events']['sport'].unique())

# Country filter
selected_countries = st.sidebar.multiselect(
    "🌍 Select Countries",
    options=all_countries,
    default=None,
    help="Filter data by specific countries"
)

# Continent filter (Creative Challenge!)
selected_continents = st.sidebar.multiselect(
    "🗺️ Select Continents",
    options=all_continents,
    default=None,
    help="Filter data by continent"
)

# Sport filter
selected_sports = st.sidebar.multiselect(
    "🏅 Select Sports",
    options=all_sports,
    default=None,
    help="Filter data by specific sports"
)

# Medal type filters
st.sidebar.markdown("### 🏆 Medal Types")
show_gold = st.sidebar.checkbox("Gold", value=True)
show_silver = st.sidebar.checkbox("Silver", value=True)
show_bronze = st.sidebar.checkbox("Bronze", value=True)

st.sidebar.markdown("---")
st.sidebar.info("💡 **Tip:** Use filters to explore specific countries, continents, or sports!")

# ============================================================================
# APPLY FILTERS
# ============================================================================
def apply_filters(df, filter_type='medals_total'):
    """Apply global filters to dataframe"""
    filtered_df = df.copy()
    
    # Apply country filter
    if selected_countries:
        if 'country' in filtered_df.columns:
            filtered_df = filtered_df[filtered_df['country'].isin(selected_countries)]
        elif 'country_long' in filtered_df.columns:
            # Get country codes for selected countries
            country_codes = data['nocs'][data['nocs']['country'].isin(selected_countries)]['code'].unique()
            if 'country_code' in filtered_df.columns:
                filtered_df = filtered_df[filtered_df['country_code'].isin(country_codes)]
    
    # Apply continent filter
    if selected_continents:
        if 'continent' in filtered_df.columns:
            filtered_df = filtered_df[filtered_df['continent'].isin(selected_continents)]
        elif 'country_code' in filtered_df.columns:
            # Get country codes for selected continents
            continent_codes = data['nocs'][data['nocs']['continent'].isin(selected_continents)]['code'].unique()
            filtered_df = filtered_df[filtered_df['country_code'].isin(continent_codes)]
    
    # Apply sport filter
    if selected_sports:
        if filter_type == 'athletes':
            # Pour les athletes, la colonne 'disciplines' est une liste (string representation)
            # Ex: "['Wrestling']" ou "['Swimming', 'Diving']"
            def athlete_has_sport(disciplines_str):
                if pd.isna(disciplines_str):
                    return False
                # Nettoyer la string et extraire les sports
                # disciplines_str est du genre: "['Wrestling']"
                try:
                    # Enlever les crochets et guillemets, split par virgule
                    sports_list = disciplines_str.strip("[]").replace("'", "").replace('"', '').split(',')
                    sports_list = [s.strip() for s in sports_list]
                    # Vérifier si un des sports sélectionnés est dans la liste
                    return any(sport in sports_list for sport in selected_sports)
                except:
                    return False
            
            filtered_df = filtered_df[filtered_df['disciplines'].apply(athlete_has_sport)]
        
        elif filter_type in ['events', 'medals']:
            if 'sport' in filtered_df.columns:
                filtered_df = filtered_df[filtered_df['sport'].isin(selected_sports)]
            elif 'discipline' in filtered_df.columns:
                filtered_df = filtered_df[filtered_df['discipline'].isin(selected_sports)]
    
    # Apply medal type filters
    if filter_type == 'medals' and 'medal_type' in filtered_df.columns:
        medal_types = []
        if show_gold:
            medal_types.append('Gold Medal')
        if show_silver:
            medal_types.append('Silver Medal')
        if show_bronze:
            medal_types.append('Bronze Medal')
        
        if medal_types:
            filtered_df = filtered_df[filtered_df['medal_type'].isin(medal_types)]
    
    return filtered_df


def get_filtered_medals_total():
    """
    Recalculate medals_total from medals_enriched with sport filter applied
    """
    # Start with medals_enriched which has sport/discipline info
    filtered_medals = apply_filters(data['medals'], 'medals')
    
    # Si aucun filtre sport, utiliser medals_total_enriched directement
    if not selected_sports:
        filtered_medals_total = apply_filters(data['medals_total'], 'medals_total')
        return filtered_medals_total
    
    # Sinon, recalculer les totaux à partir des médailles filtrées
    if len(filtered_medals) == 0:
        # Retourner un DataFrame vide avec les bonnes colonnes
        return pd.DataFrame(columns=data['medals_total'].columns)
    
    # Grouper par pays et compter les médailles
    medal_counts = filtered_medals.groupby(['country_code', 'country', 'country_long', 'continent', 'medal_type']).size().reset_index(name='count')
    
    # Pivoter pour avoir Gold Medal, Silver Medal, Bronze Medal en colonnes
    medal_pivot = medal_counts.pivot_table(
        index=['country_code', 'country', 'country_long', 'continent'],
        columns='medal_type',
        values='count',
        fill_value=0
    ).reset_index()
    
    # S'assurer que toutes les colonnes de médailles existent
    for col in ['Gold Medal', 'Silver Medal', 'Bronze Medal']:
        if col not in medal_pivot.columns:
            medal_pivot[col] = 0
    
    # Calculer le total
    medal_pivot['Total'] = (
        medal_pivot['Gold Medal'] + 
        medal_pivot['Silver Medal'] + 
        medal_pivot['Bronze Medal']
    )
    
    # Ajouter code (duplicate de country_code pour compatibilité)
    medal_pivot['code'] = medal_pivot['country_code']
    
    # Calculer les ratios
    medal_pivot['gold_ratio'] = (
        medal_pivot['Gold Medal'] / medal_pivot['Total']
    ).fillna(0).round(3)
    
    medal_pivot['silver_ratio'] = (
        medal_pivot['Silver Medal'] / medal_pivot['Total']
    ).fillna(0).round(3)
    
    medal_pivot['bronze_ratio'] = (
        medal_pivot['Bronze Medal'] / medal_pivot['Total']
    ).fillna(0).round(3)
    
    # Calculer medal_quality_score
    medal_pivot['medal_quality_score'] = (
        medal_pivot['Gold Medal'] * 3 + 
        medal_pivot['Silver Medal'] * 2 + 
        medal_pivot['Bronze Medal'] * 1
    )
    
    # Calculer les rangs
    medal_pivot['rank_by_total'] = medal_pivot['Total'].rank(
        method='min', ascending=False
    ).astype(int)
    
    medal_pivot['rank_by_gold'] = medal_pivot['Gold Medal'].rank(
        method='min', ascending=False
    ).astype(int)
    
    medal_pivot['rank_by_quality'] = medal_pivot['medal_quality_score'].rank(
        method='min', ascending=False
    ).astype(int)
    
    # Trier par total
    medal_pivot = medal_pivot.sort_values('Total', ascending=False)
    
    return medal_pivot


# Apply filters to datasets
filtered_athletes = apply_filters(data['athletes'], 'athletes')
filtered_events = apply_filters(data['events'], 'events')
filtered_medals_total = get_filtered_medals_total()
filtered_medals = apply_filters(data['medals'], 'medals')

# ============================================================================
# HEADER
# ============================================================================
_, col_logo, _ = st.columns([1, 2, 1])
with col_logo:
    st.image("figures/logos/logo.png", width=320)
st.markdown("---")

# ============================================================================
# KPI METRICS SECTION
# ============================================================================
st.markdown("## 📊 Key Performance Indicators")

# Calculate KPIs
total_athletes = len(filtered_athletes)
total_countries = filtered_medals_total['country_code'].nunique() if len(filtered_medals_total) > 0 else data['nocs']['code'].nunique()
total_sports = filtered_events['sport'].nunique() if len(filtered_events) > 0 else data['events']['sport'].nunique()

# Calculate total medals based on medal type filters
medal_columns = []
if show_gold:
    medal_columns.append('Gold Medal')
if show_silver:
    medal_columns.append('Silver Medal')
if show_bronze:
    medal_columns.append('Bronze Medal')

if medal_columns and len(filtered_medals_total) > 0:
    total_medals = filtered_medals_total[medal_columns].sum().sum()
else:
    total_medals = filtered_medals_total['Total'].sum() if len(filtered_medals_total) > 0 else data['medals_total']['Total'].sum()

total_events = len(filtered_events)

# Display KPIs in columns
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric(
        label="👥 Total Athletes",
        value=f"{total_athletes:,}",
        delta=None,
        help="Total number of athletes participating"
    )

with col2:
    st.metric(
        label="🌍 Total Countries",
        value=f"{total_countries:,}",
        delta=None,
        help="Total number of participating countries (NOCs)"
    )

with col3:
    st.metric(
        label="🏃 Total Sports",
        value=f"{total_sports:,}",
        delta=None,
        help="Total number of different sports"
    )

with col4:
    st.metric(
        label="🏆 Medals Awarded",
        value=f"{int(total_medals):,}",
        delta=None,
        help="Total number of medals awarded"
    )

with col5:
    st.metric(
        label="🎯 Total Events",
        value=f"{total_events:,}",
        delta=None,
        help="Total number of Olympic events"
    )

st.markdown("---")

# ============================================================================
# VISUALIZATIONS SECTION
# ============================================================================

# Row 1: Medal Distribution and Top 10 Countries
col_left, col_right = st.columns([1, 1])

with col_left:
    st.markdown("### 🎨 Global Medal Distribution")
    
    # Prepare data for pie chart
    medal_dist_data = []
    if show_gold and len(filtered_medals_total) > 0:
        medal_dist_data.append({'Medal Type': 'Gold', 'Count': filtered_medals_total['Gold Medal'].sum()})
    if show_silver and len(filtered_medals_total) > 0:
        medal_dist_data.append({'Medal Type': 'Silver', 'Count': filtered_medals_total['Silver Medal'].sum()})
    if show_bronze and len(filtered_medals_total) > 0:
        medal_dist_data.append({'Medal Type': 'Bronze', 'Count': filtered_medals_total['Bronze Medal'].sum()})
    
    if medal_dist_data:
        medal_dist_df = pd.DataFrame(medal_dist_data)
        
        fig_pie = px.pie(
            medal_dist_df,
            values='Count',
            names='Medal Type',
            color='Medal Type',
            color_discrete_map={
                'Gold': '#FFE766',
                'Silver': '#C0C0C0',
                'Bronze': '#d99d73'
            },
            hole=0.4,  # Donut chart
            title="Distribution of Medals by Type"
        )
        
        fig_pie.update_traces(
            textposition='inside',
            textinfo='percent+label',
            hovertemplate='<b>%{label}</b><br>Count: %{value}<br>Percentage: %{percent}<extra></extra>'
        )
        
        fig_pie.update_layout(
            showlegend=True,
            height=400,
            margin=dict(t=50, b=0, l=0, r=0)
        )
        
        st.plotly_chart(fig_pie, use_container_width=True)
    else:
        st.info("No medals to display with current filters.")

with col_right:
    st.markdown("### 🏆 Top 10 Medal Standings")
    
    if len(filtered_medals_total) > 0:
        # Calculate total based on selected medal types
        top_10_df = filtered_medals_total.copy()
        
        if medal_columns:
            top_10_df['Filtered_Total'] = top_10_df[medal_columns].sum(axis=1)
        else:
            top_10_df['Filtered_Total'] = 0
        
        top_10_df = top_10_df.nlargest(10, 'Filtered_Total')
        
        # Prepare data for stacked bar chart
        bar_data = []
        for _, row in top_10_df.iterrows():
            if show_gold:
                bar_data.append({'Country': row['country'], 'Medal Type': 'Gold', 'Count': row['Gold Medal']})
            if show_silver:
                bar_data.append({'Country': row['country'], 'Medal Type': 'Silver', 'Count': row['Silver Medal']})
            if show_bronze:
                bar_data.append({'Country': row['country'], 'Medal Type': 'Bronze', 'Count': row['Bronze Medal']})
        
        if bar_data:
            bar_df = pd.DataFrame(bar_data)
            
            fig_bar = px.bar(
                bar_df,
                y='Country',
                x='Count',
                color='Medal Type',
                orientation='h',
                color_discrete_map={
                    'Gold': '#FFE766',
                    'Silver': '#C0C0C0',
                    'Bronze': '#d99d73'
                },
                title="Top 10 Countries by Medal Count",
                labels={'Count': 'Number of Medals', 'Country': ''}
            )
            
            fig_bar.update_layout(
                height=400,
                xaxis_title="Number of Medals",
                yaxis_title="",
                legend_title="Medal Type",
                hovermode='y unified',
                yaxis={'categoryorder': 'total ascending'}
            )
            
            st.plotly_chart(fig_bar, use_container_width=True)
        else:
            st.info("No data to display with current filters.")
    else:
        st.info("No countries to display with current filters.")

st.markdown("---")

# Row 2: Additional insights
st.markdown("## 🌍 Continental Performance Overview")

col1, col2 = st.columns([2, 1])

with col1:
    if len(filtered_medals_total) > 0:
        # Group by continent
        continent_medals = filtered_medals_total.groupby('continent').agg({
            'Gold Medal': 'sum',
            'Silver Medal': 'sum',
            'Bronze Medal': 'sum',
            'Total': 'sum'
        }).reset_index()
        
        continent_medals = continent_medals[continent_medals['Total'] > 0]
        continent_medals = continent_medals.sort_values('Total', ascending=True)
        
        # Prepare data for grouped bar chart
        continent_bar_data = []
        for _, row in continent_medals.iterrows():
            if show_gold:
                continent_bar_data.append({'Continent': row['continent'], 'Medal Type': 'Gold', 'Count': row['Gold Medal']})
            if show_silver:
                continent_bar_data.append({'Continent': row['continent'], 'Medal Type': 'Silver', 'Count': row['Silver Medal']})
            if show_bronze:
                continent_bar_data.append({'Continent': row['continent'], 'Medal Type': 'Bronze', 'Count': row['Bronze Medal']})
        
        if continent_bar_data:
            continent_bar_df = pd.DataFrame(continent_bar_data)
            
            fig_continent = px.bar(
                continent_bar_df,
                y='Continent',
                x='Count',
                color='Medal Type',
                orientation='h',
                color_discrete_map={
                    'Gold': '#FFE766',
                    'Silver': '#C0C0C0',
                    'Bronze': '#d99d73'
                },
                title="Medal Distribution by Continent",
                barmode='group'
            )
            
            fig_continent.update_layout(
                height=400,
                xaxis_title="Number of Medals",
                yaxis_title="",
                legend_title="Medal Type",
                hovermode='y unified'
            )
            
            st.plotly_chart(fig_continent, use_container_width=True)
        else:
            st.info("No continental data to display.")
    else:
        st.info("No data available for continental analysis.")

with col2:
    st.markdown("### 📈 Quick Stats")
    
    if len(filtered_medals_total) > 0:
        # Most successful country
        top_country = filtered_medals_total.nlargest(1, 'Total')
        if len(top_country) > 0:
            st.metric(
                "🥇 Most Successful Country",
                top_country.iloc[0]['country'],
                f"{int(top_country.iloc[0]['Total'])} medals"
            )
        
        # Most gold medals
        top_gold = filtered_medals_total.nlargest(1, 'Gold Medal')
        if len(top_gold) > 0:
            st.metric(
                "⭐ Most Gold Medals",
                top_gold.iloc[0]['country'],
                f"{int(top_gold.iloc[0]['Gold Medal'])} gold"
            )
        
        # Average medals per country
        avg_medals = filtered_medals_total['Total'].mean()
        st.metric(
            "📊 Avg Medals/Country",
            f"{avg_medals:.1f}",
            None
        )
        
        # Continent with most medals
        if 'continent' in filtered_medals_total.columns:
            continent_totals = filtered_medals_total.groupby('continent')['Total'].sum()
            top_continent = continent_totals.idxmax() if len(continent_totals) > 0 else "N/A"
            top_continent_count = continent_totals.max() if len(continent_totals) > 0 else 0
            
            st.metric(
                "🌍 Top Continent",
                top_continent,
                f"{int(top_continent_count)} medals"
            )
    else:
        st.info("No statistics available with current filters.")

st.markdown("---")

# Footer
st.markdown("### 🚀 Ready to Explore More?")
st.markdown("""
Navigate to other pages using the sidebar to dive deeper into:
- 🗺️ **Global Analysis**: Geographical insights and world maps
- 👤 **Athlete Performance**: Individual athlete profiles and statistics
- 🏟️ **Sports & Events**: Event schedules and venue information
""")

st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #666; padding: 20px;'>
        <p>📊 Paris 2024 Olympics Dashboard | Built with Streamlit & Python</p>
        <p>Data Source: Kaggle - Paris 2024 Olympic Summer Games</p>
    </div>
    """,
    unsafe_allow_html=True
)