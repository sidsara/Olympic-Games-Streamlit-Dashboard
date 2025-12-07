"""
Page 2: Global Analysis (The World View)
==========================================
Analyzes Olympic data from geographical and hierarchical perspectives.

Author: Your Name
Date: December 2024
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path

# Page configuration
st.set_page_config(
    page_title="Global Analysis - Paris 2024",
    page_icon="🗺️",
    layout="wide"
)

# Define paths
DATA_DIR = Path(__file__).parent.parent / 'data'

# ============================================================================
# DATA LOADING
# ============================================================================

@st.cache_data
def load_data():
    """Load all necessary datasets for Global Analysis page"""
    try:
        medals_total_enriched = pd.read_csv(DATA_DIR / 'medals_total_enriched.csv')
        continent_summary = pd.read_csv(DATA_DIR / 'continent_summary.csv')
        medals_enriched = pd.read_csv(DATA_DIR / 'medals_enriched.csv')
        nocs = pd.read_csv(DATA_DIR / 'nocs_cleaned.csv')
        athletes_enriched = pd.read_csv(DATA_DIR / 'athletes_enriched.csv')
        
        return {
            'medals_total': medals_total_enriched,
            'continent_summary': continent_summary,
            'medals': medals_enriched,
            'nocs': nocs,
            'athletes': athletes_enriched
        }
    except FileNotFoundError as e:
        st.error(f"❌ Error loading data: {e}")
        st.info("Please run cleaning.py and merging.py first to generate the required datasets.")
        st.stop()

# Load data
data = load_data()

# ============================================================================
# SIDEBAR FILTERS
# ============================================================================

st.sidebar.header("🔍 Global Filters")

# Continent filter
continents = ['All'] + sorted(data['medals_total']['continent'].dropna().unique().tolist())
selected_continent = st.sidebar.selectbox(
    "Select Continent",
    continents,
    index=0
)

# Country filter (depends on continent selection)
if selected_continent == 'All':
    countries = ['All'] + sorted(data['medals_total']['country'].unique().tolist())
else:
    countries = ['All'] + sorted(
        data['medals_total'][data['medals_total']['continent'] == selected_continent]['country'].unique().tolist()
    )

selected_country = st.sidebar.selectbox(
    "Select Country",
    countries,
    index=0
)

# Medal type filter
medal_types = ['All', 'Gold', 'Silver', 'Bronze']
selected_medal_type = st.sidebar.multiselect(
    "Select Medal Type(s)",
    medal_types[1:],  # Exclude 'All'
    default=medal_types[1:]
)

# Gender filter
genders = ['All', 'Male', 'Female']
selected_gender = st.sidebar.selectbox(
    "Select Gender",
    genders,
    index=0
)

st.sidebar.markdown("---")
st.sidebar.info("💡 **Tip**: Use filters to explore specific regions, countries, or medal types!")

# ============================================================================
# APPLY FILTERS
# ============================================================================

def apply_filters(df, filter_continent=True, filter_country=True):
    """Apply sidebar filters to dataframe"""
    filtered_df = df.copy()
    
    # Continent filter
    if filter_continent and selected_continent != 'All':
        if 'continent' in filtered_df.columns:
            filtered_df = filtered_df[filtered_df['continent'] == selected_continent]
    
    # Country filter
    if filter_country and selected_country != 'All':
        if 'country' in filtered_df.columns:
            filtered_df = filtered_df[filtered_df['country'] == selected_country]
    
    # Gender filter (only if gender column exists)
    if selected_gender != 'All' and 'gender' in filtered_df.columns:
        filtered_df = filtered_df[filtered_df['gender'] == selected_gender]
    
    return filtered_df

# ============================================================================
# PAGE HEADER
# ============================================================================

st.title("🗺️ Global Analysis: The World View")
st.markdown("""
Explore the Paris 2024 Olympics from a geographical and hierarchical perspective. 
Analyze medal distributions across continents, countries, and sports with interactive visualizations.
""")

st.markdown("---")

# ============================================================================
# SECTION 1: WORLD MEDAL MAP
# ============================================================================

st.header("🌍 World Medal Map")
st.markdown("**Choropleth map showing total medal count by country**")

# CORRECTION: Appliquer TOUS les filtres (continent ET country)
medals_for_map = apply_filters(data['medals_total'], filter_continent=True, filter_country=True)

# Calculate filtered total based on selected medal types
if selected_medal_type:
    medals_for_map['filtered_total'] = 0
    if 'Gold' in selected_medal_type:
        medals_for_map['filtered_total'] += medals_for_map['Gold Medal']
    if 'Silver' in selected_medal_type:
        medals_for_map['filtered_total'] += medals_for_map['Silver Medal']
    if 'Bronze' in selected_medal_type:
        medals_for_map['filtered_total'] += medals_for_map['Bronze Medal']
else:
    medals_for_map['filtered_total'] = medals_for_map['Total']

# Mapping des codes NOC vers ISO-3 standard pour Plotly
iso_mapping = {
    # A
    'AFG': 'AFG',
    'ALB': 'ALB',
    'ALG': 'DZA',
    'AND': 'AND',
    'ANG': 'AGO',
    'ANT': 'ATG',
    'ARG': 'ARG',
    'ARM': 'ARM',
    'ARU': 'ABW',
    'ASA': 'ASM',
    'AUT': 'AUT',
    'AZE': 'AZE',

    # B
    'BAH': 'BHS',
    'BAN': 'BGD',
    'BAR': 'BRB',
    'BDI': 'BDI',
    'BEL': 'BEL',
    'BEN': 'BEN',
    'BER': 'BMU',
    'BHU': 'BTN',
    'BIH': 'BIH',
    'BLR': 'BLR',
    'BOL': 'BOL',
    'BOT': 'BWA',
    'BRA': 'BRA',
    'BRN': 'BRN',
    'BRU': 'BRN',
    'BUL': 'BGR',
    'BUR': 'BFA',
    'BVT': None,  # Délégation spéciale
    'BWA': 'BWA',

    # C
    'CAF': 'CAF',
    'CAM': 'KHM',
    'CAN': 'CAN',
    'CAY': 'CYM',
    'CGO': 'COG',
    'CHA': 'TCD',
    'CHI': 'CHL',
    'CHN': 'CHN',
    'CIV': 'CIV',
    'CMR': 'CMR',
    'COD': 'COD',
    'COK': 'COK',
    'COL': 'COL',
    'COM': 'COM',
    'CPV': 'CPV',
    'CRC': 'CRI',
    'CRO': 'HRV',
    'CUB': 'CUB',
    'CYP': 'CYP',
    'CZE': 'CZE',

    # D
    'DEN': 'DNK',
    'DJI': 'DJI',
    'DMA': 'DMA',
    'DOM': 'DOM',

    # E
    'ECU': 'ECU',
    'EGY': 'EGY',
    'ERI': 'ERI',
    'ESA': 'SLV',
    'ESP': 'ESP',
    'EST': 'EST',
    'ETH': 'ETH',

    # F
    'FIJ': 'FJI',
    'FIN': 'FIN',
    'FRA': 'FRA',

    # G
    'GAB': 'GAB',
    'GAM': 'GMB',
    'GBR': 'GBR',
    'GBS': 'GNB',
    'GEO': 'GEO',
    'GER': 'DEU',
    'GHA': 'GHA',
    'GRE': 'GRC',
    'GRN': 'GRD',
    'GUA': 'GTM',
    'GUI': 'GIN',
    'GUM': 'GUM',
    'GUY': 'GUY',

    # H
    'HAI': 'HTI',
    'HKG': 'HKG',
    'HON': 'HND',
    'HUN': 'HUN',

    # I
    'INA': 'IDN',
    'IND': 'IND',
    'IRI': 'IRN',
    'IRL': 'IRL',
    'IRQ': 'IRQ',
    'ISL': 'ISL',
    'ISR': 'ISR',
    'ISV': 'VIR',
    'ITA': 'ITA',

    # J
    'JAM': 'JAM',
    'JOR': 'JOR',
    'JPN': 'JPN',

    # K
    'KAZ': 'KAZ',
    'KEN': 'KEN',
    'KGZ': 'KGZ',
    'KIR': 'KIR',
    'KOR': 'KOR',
    'KOS': 'XKX',
    'KSA': 'SAU',
    'KUW': 'KWT',

    # L
    'LAO': 'LAO',
    'LAT': 'LVA',
    'LBN': 'LBN',
    'LBR': 'LBR',
    'LCA': 'LCA',
    'LES': 'LSO',
    'LIB': 'LBN',
    'LIE': 'LIE',
    'LTU': 'LTU',
    'LUX': 'LUX',
    'LVA': 'LVA',

    # M
    'MAD': 'MDG',
    'MAR': 'MAR',
    'MAS': 'MYS',
    'MAW': 'MWI',
    'MDA': 'MDA',
    'MDV': 'MDV',
    'MEX': 'MEX',
    'MGL': 'MNG',
    'MKD': 'MKD',
    'MLI': 'MLI',
    'MLT': 'MLT',
    'MNE': 'MNE',
    'MON': 'MCO',
    'MOZ': 'MOZ',
    'MRI': 'MUS',
    'MTN': 'MRT',
    'MYA': 'MMR',

    # N
    'NAM': 'NAM',
    'NCA': 'NIC',
    'NED': 'NLD',
    'NEP': 'NPL',
    'NGR': 'NGA',
    'NIG': 'NER',
    'NOR': 'NOR',
    'NRU': 'NRU',
    'NZL': 'NZL',

    # O
    'OMA': 'OMN',

    # P
    'PAK': 'PAK',
    'PAN': 'PAN',
    'PAR': 'PRY',
    'PER': 'PER',
    'PHI': 'PHL',
    'PLE': 'PSE',
    'PLW': 'PLW',
    'PNG': 'PNG',
    'POL': 'POL',
    'POR': 'PRT',
    'PRI': 'PRI',
    'PRK': 'PRK',
    'PUR': 'PRI',

    # Q
    'QAT': 'QAT',

    # R
    'ROU': 'ROU',
    'RSA': 'ZAF',
    'RUS': 'RUS',
    'RWA': 'RWA',

    # S
    'SAM': 'WSM',
    'SEN': 'SEN',
    'SEY': 'SYC',
    'SIN': 'SGP',
    'SKN': 'KNA',
    'SLE': 'SLE',
    'SLO': 'SVN',
    'SMR': 'SMR',
    'SOL': 'SLB',
    'SOM': 'SOM',
    'SRB': 'SRB',
    'SRI': 'LKA',
    'SUD': 'SDN',
    'SUI': 'CHE',
    'SUR': 'SUR',
    'SVK': 'SVK',
    'SVN': 'SVN',
    'SWE': 'SWE',
    'SWZ': 'SWZ',
    'SYR': 'SYR',

    # T
    'TAN': 'TZA',
    'TGA': 'TON',
    'THA': 'THA',
    'TJK': 'TJK',
    'TKM': 'TKM',
    'TLS': 'TLS',
    'TOG': 'TGO',
    'TPE': 'TWN',
    'TTO': 'TTO',
    'TUN': 'TUN',
    'TUR': 'TUR',
    'TUV': 'TUV',

    # U
    'UAE': 'ARE',
    'UGA': 'UGA',
    'UKR': 'UKR',
    'URU': 'URY',
    'USA': 'USA',
    'UZB': 'UZB',

    # V
    'VAN': 'VUT',
    'VEN': 'VEN',
    'VIE': 'VNM',

    # Y
    'YEM': 'YEM',

    # Z
    'ZAM': 'ZMB',
    'ZIM': 'ZWE',

    # Territoires spéciaux / délégations sans ISO officiel
    'AIN': None,   # Athlètes Individuels Neutres
    'EOR': None,   # Équipe des réfugiés
    'IOC': None,   # Comité international
    'OAR': None,   # Olympic Athletes from Russia
    'ROC': None,   # Russian Olympic Committee
    'RPC': None,   # Paralympic Russia
}


# Créer une colonne iso_code pour la carte
medals_for_map['iso_code'] = medals_for_map['country_code'].map(
    lambda x: iso_mapping.get(x, x)
)

# Filtrer les pays sans code ISO valide
medals_for_map_valid = medals_for_map[
    (medals_for_map['iso_code'].notna()) & 
    (medals_for_map['filtered_total'] > 0)
].copy()

# AMÉLIORATION: Pour une meilleure visualisation, créer un DataFrame complet avec tous les pays
# mais mettre 0 pour les pays non sélectionnés
if selected_country != 'All' or selected_continent != 'All':
    # Créer un DataFrame avec tous les pays (pour afficher la carte complète)
    all_countries = data['medals_total'].copy()
    all_countries['iso_code'] = all_countries['country_code'].map(lambda x: iso_mapping.get(x, x))
    all_countries['filtered_total'] = 0  # Mettre 0 par défaut
    
    # Mettre les vraies valeurs uniquement pour les pays filtrés
    for idx, row in medals_for_map_valid.iterrows():
        all_countries.loc[all_countries['country_code'] == row['country_code'], 'filtered_total'] = row['filtered_total']
    
    medals_for_map_display = all_countries[all_countries['iso_code'].notna()].copy()
else:
    medals_for_map_display = medals_for_map_valid

# Créer la carte choropleth
fig_map = px.choropleth(
    medals_for_map_display,
    locations='iso_code',
    locationmode='ISO-3',
    color='filtered_total',
    hover_name='country',
    hover_data={
        'country_code': True,
        'iso_code': False,
        'Gold Medal': True,
        'Silver Medal': True,
        'Bronze Medal': True,
        'filtered_total': True
    },
    color_continuous_scale=[
        [0, '#f7fbff'],      # Bleu très clair
        [0.2, '#deebf7'],
        [0.4, '#9ecae1'],
        [0.6, '#4292c6'],
        [0.8, '#2171b5'],
        [1, '#08519c']       # Bleu foncé
    ],
    labels={
        'filtered_total': '🏆 Total Medals',
        'country_code': '🌍 NOC Code'
    },
    title='',
    range_color=[0, medals_for_map_display['filtered_total'].max()] if len(medals_for_map_display) > 0 else [0, 1]
)

fig_map.update_layout(
    height=550,
    geo=dict(
        showframe=True,
        framecolor='rgba(102, 126, 234, 0.5)',
        framewidth=2,
        showcoastlines=True,
        coastlinecolor='rgba(50, 50, 50, 0.3)',
        coastlinewidth=1.5,
        projection_type='natural earth',
        showcountries=True,
        countrycolor='rgba(200, 200, 200, 0.3)',
        showland=True,
        landcolor='rgb(250, 250, 250)',
        showlakes=True,
        lakecolor='rgb(230, 240, 255)',
        showocean=True,
        oceancolor='rgb(220, 235, 255)',
    ),
    margin=dict(l=0, r=0, t=10, b=0),
    coloraxis_colorbar=dict(
        title="<b>Medals</b>",
        thickness=15,
        len=0.7,
        tickfont=dict(size=11)
    )
)

st.plotly_chart(fig_map, use_container_width=True)

# Map insights avec correction
col1, col2, col3, col4 = st.columns(4)

with col1:
    countries_on_map = len(medals_for_map_valid)
    total_countries = len(medals_for_map[medals_for_map['filtered_total'] > 0])
    st.metric(
        "Countries Selected", 
        countries_on_map,
        help="Number of countries matching the current filters"
    )

with col2:
    st.metric("Total Medals", int(medals_for_map['filtered_total'].sum()))

with col3:
    if len(medals_for_map_valid) > 0:
        top_country = medals_for_map_valid.nlargest(1, 'filtered_total')
        if not top_country.empty:
            st.metric("Leading Country", top_country['country'].values[0])
    else:
        st.metric("Leading Country", "N/A")

with col4:
    if len(medals_for_map_valid) > 0:
        avg_medals = medals_for_map_valid['filtered_total'].mean()
        st.metric("Avg Medals", f"{avg_medals:.1f}")
    else:
        st.metric("Avg Medals", "0")

# Afficher les pays exclus de la carte (pour debug/info)
if total_countries > countries_on_map:
    with st.expander("ℹ️ Countries with medals not shown on map"):
        excluded = medals_for_map[
            (medals_for_map['filtered_total'] > 0) & 
            (medals_for_map['iso_code'].isna())
        ][['country', 'country_code', 'Gold Medal', 'Silver Medal', 'Bronze Medal', 'Total']]
        
        if not excluded.empty:
            st.warning(f"⚠️ {len(excluded)} country/countries have medals but cannot be displayed on the map due to special NOC codes:")
            st.dataframe(excluded, use_container_width=True, hide_index=True)
        else:
            st.info("All selected countries are displayed on the map.")

st.markdown("---")

# ============================================================================
# SECTION 2: MEDAL HIERARCHY BY CONTINENT
# ============================================================================

st.header("🎯 Medal Hierarchy by Continent")
st.markdown("**Hierarchical view: Continent → Country → Sport → Medal Count**")

# Appliquer tous les filtres (continent, country, gender, medal type) sur les médailles
def apply_all_filters(df):
    filtered_df = df.copy()
    # Continent
    if selected_continent != 'All':
        col_continent = next((c for c in filtered_df.columns if c.lower() == 'continent'), None)
        if col_continent:
            filtered_df = filtered_df[filtered_df[col_continent] == selected_continent]
    # Country
    if selected_country != 'All':
        col_country = next((c for c in filtered_df.columns if c.lower() == 'country'), None)
        if col_country:
            filtered_df = filtered_df[filtered_df[col_country] == selected_country]
    # Gender
    gender_map = {
        'Male': 'M',
        'Female': 'W'
    }
    if selected_gender != 'All':
        # 1. Obtenir le code de genre réel ('M' ou 'W')
        data_gender_code = gender_map.get(selected_gender)
        col_gender = next((c for c in filtered_df.columns if c.lower() == 'gender'), None)
        if col_gender and data_gender_code:
            filtered_df = filtered_df[filtered_df[col_gender] == data_gender_code]
    # Medal type
    if selected_medal_type:
        medal_map = {
            'Gold': 'Gold Medal',
            'Silver': 'Silver Medal',
            'Bronze': 'Bronze Medal'
        }
        data_medal_types = [medal_map[m] for m in selected_medal_type if m in medal_map]
        col_medal_type = next((c for c in filtered_df.columns if c.lower() == 'medal_type'), None)
        if col_medal_type and data_medal_types:
            filtered_df = filtered_df[filtered_df[col_medal_type].isin(data_medal_types)]
    return filtered_df

medals_hierarchy = apply_all_filters(data['medals'])

# Créer la hiérarchie
hierarchy_data = medals_hierarchy.groupby(
    ['continent', 'country', 'discipline', 'medal_type']
).size().reset_index(name='count')

tab1, tab2 = st.tabs(["📊 Sunburst Chart", "🔲 Treemap"])

with tab1:
        fig_sunburst = px.sunburst(
            hierarchy_data,
            path=['continent', 'country', 'discipline', 'medal_type'],
            values='count',
            color='medal_type',
            color_discrete_map={
                'Gold': '#FFE766',
                'Silver': '#C0C0C0',
                'Bronze': '#d99d73'
            },
            title='Medal Distribution Hierarchy (Click to drill down)',
            height=700
        )
        fig_sunburst.update_traces(textinfo='label+percent entry')
        st.plotly_chart(fig_sunburst, use_container_width=True)

with tab2:

        fig_treemap = px.treemap(
            hierarchy_data,
            path=['continent', 'country', 'discipline', 'medal_type'],
            values='count',
            color='medal_type',
            color_discrete_map={
                'Gold': '#FFE766',
                'Silver': '#C0C0C0',
                'Bronze': '#d99d73'
            },
            title='Medal Distribution Treemap',
            height=700
        )
        fig_treemap.update_traces(textinfo='label+value+percent parent')
        st.plotly_chart(fig_treemap, use_container_width=True)

st.markdown("---")

# ============================================================================
# SECTION 3: CONTINENT VS. MEDALS BAR CHART
# ============================================================================

st.header("🌐 Continent Performance Comparison")
st.markdown("**Medal distribution across continents**")

# Prepare continent data
continent_data = apply_filters(data['continent_summary'], filter_continent=True, filter_country=False)

# Reshape data for grouped bar chart
continent_melted = continent_data.melt(
    id_vars=['continent'],
    value_vars=['Gold Medal', 'Silver Medal', 'Bronze Medal'],
    var_name='Medal Type',
    value_name='Count'
)

# Clean medal type names
continent_melted['Medal Type'] = continent_melted['Medal Type'].str.replace(' Medal', '')

# Create grouped bar chart
fig_continent = px.bar(
    continent_melted,
    x='continent',
    y='Count',
    color='Medal Type',
    barmode='group',
    color_discrete_map={
        'Gold': '#FFE766',
        'Silver': '#C0C0C0',
        'Bronze': '#d99d73'
    },
    title='Medal Count by Continent',
    labels={'continent': 'Continent', 'Count': 'Number of Medals'},
    height=500
)

fig_continent.update_layout(
    xaxis_title='Continent',
    yaxis_title='Number of Medals',
    legend_title='Medal Type',
    hovermode='x unified'
)

st.plotly_chart(fig_continent, use_container_width=True)

# Continent statistics
st.subheader("📊 Continent Statistics")
col1, col2 = st.columns(2)

with col1:
    # Top performing continent
    top_continent = continent_data.nlargest(1, 'Total')
    if not top_continent.empty:
        st.success(f"""
        **🏆 Leading Continent**: {top_continent['continent'].values[0]}  
        **Total Medals**: {int(top_continent['Total'].values[0])}  
        **Gold Medals**: {int(top_continent['Gold Medal'].values[0])}
        """)

with col2:
    # Continent with highest gold ratio
    best_gold_ratio = continent_data.nlargest(1, 'gold_ratio')
    if not best_gold_ratio.empty:
        st.info(f"""
        **⭐ Best Gold Ratio**: {best_gold_ratio['continent'].values[0]}  
        **Gold Ratio**: {best_gold_ratio['gold_ratio'].values[0]:.1%}  
        **Avg Medals/Country**: {best_gold_ratio['avg_medals_per_country'].values[0]:.1f}
        """)

st.markdown("---")

# ============================================================================
# SECTION 4: COUNTRY VS. MEDALS (TOP 20)
# ============================================================================

st.header("🏆 Top 20 Countries Medal Performance")
st.markdown("**Detailed medal breakdown for leading nations**")

# Prepare country data
country_data = apply_filters(data['medals_total'], filter_continent=True, filter_country=False)

# Get top 20 countries by total medals
top_20_countries = country_data.nlargest(20, 'Total')

# Reshape for grouped bar chart
country_melted = top_20_countries.melt(
    id_vars=['country', 'country_code'],
    value_vars=['Gold Medal', 'Silver Medal', 'Bronze Medal'],
    var_name='Medal Type',
    value_name='Count'
)

country_melted['Medal Type'] = country_melted['Medal Type'].str.replace(' Medal', '')

# Create grouped bar chart
fig_country = px.bar(
    country_melted,
    x='country',
    y='Count',
    color='Medal Type',
    barmode='group',
    color_discrete_map={
        'Gold': '#FFE766',
        'Silver': '#C0C0C0',
        'Bronze': '#d99d73'
    },
    title='Top 20 Countries by Medal Count',
    labels={'country': 'Country', 'Count': 'Number of Medals'},
    height=600,
    hover_data=['country_code']
)

fig_country.update_layout(
    xaxis_title='Country',
    yaxis_title='Number of Medals',
    legend_title='Medal Type',
    xaxis={'categoryorder': 'total descending'},
    hovermode='x unified'
)

fig_country.update_xaxes(tickangle=-45)

st.plotly_chart(fig_country, use_container_width=True)

# Country ranking table
st.subheader("📋 Top 20 Countries - Detailed Rankings")

ranking_df = top_20_countries[['rank_by_total', 'country', 'Gold Medal', 'Silver Medal', 'Bronze Medal', 'Total', 'continent']].copy()
ranking_df.columns = ['Rank', 'Country', '🥇 Gold', '🥈 Silver', '🥉 Bronze', '📊 Total', 'Continent']

st.dataframe(
    ranking_df,
    use_container_width=True,
    hide_index=True,
    height=400
)

st.markdown("---")

# ============================================================================
# BONUS: HEAD-TO-HEAD COUNTRY COMPARISON
# ============================================================================

st.header("⚔️ Head-to-Head Country Comparison")
st.markdown("**Compare two countries side by side**")

col1, col2 = st.columns(2)

with col1:
    country1 = st.selectbox(
        "Select First Country",
        sorted(data['medals_total']['country'].unique()),
        key='country1'
    )

with col2:
    country2 = st.selectbox(
        "Select Second Country",
        sorted(data['medals_total']['country'].unique()),
        key='country2'
    )

if country1 and country2:
    # Get data for both countries
    c1_data = data['medals_total'][data['medals_total']['country'] == country1].iloc[0]
    c2_data = data['medals_total'][data['medals_total']['country'] == country2].iloc[0]
    
    # Display comparison
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"### {country1}")
        st.metric("🥇 Gold", int(c1_data['Gold Medal']))
        st.metric("🥈 Silver", int(c1_data['Silver Medal']))
        st.metric("🥉 Bronze", int(c1_data['Bronze Medal']))
        st.metric("📊 Total", int(c1_data['Total']))
        st.metric("🏅 Rank", int(c1_data['rank_by_total']))
    
    with col2:
        st.markdown("### Comparison")
        
        # Create comparison chart
        comparison_data = pd.DataFrame({
            'Country': [country1, country2],
            'Gold': [c1_data['Gold Medal'], c2_data['Gold Medal']],
            'Silver': [c1_data['Silver Medal'], c2_data['Silver Medal']],
            'Bronze': [c1_data['Bronze Medal'], c2_data['Bronze Medal']]
        })
        
        comparison_melted = comparison_data.melt(
            id_vars=['Country'],
            value_vars=['Gold', 'Silver', 'Bronze'],
            var_name='Medal Type',
            value_name='Count'
        )
        
        fig_comparison = px.bar(
            comparison_melted,
            x='Medal Type',
            y='Count',
            color='Country',
            barmode='group',
            height=300
        )
        
        st.plotly_chart(fig_comparison, use_container_width=True)
    
    with col3:
        st.markdown(f"### {country2}")
        st.metric("🥇 Gold", int(c2_data['Gold Medal']))
        st.metric("🥈 Silver", int(c2_data['Silver Medal']))
        st.metric("🥉 Bronze", int(c2_data['Bronze Medal']))
        st.metric("📊 Total", int(c2_data['Total']))
        st.metric("🏅 Rank", int(c2_data['rank_by_total']))

st.markdown("---")

# ============================================================================
# FOOTER
# ============================================================================

st.markdown("""
<div style='text-align: center; color: gray; padding: 20px;'>
    <p>Paris 2024 Olympics Dashboard | Page 2: Global Analysis 🗺️</p>
    <p>Data Source: Paris 2024 Olympics Official Dataset</p>
</div>
""", unsafe_allow_html=True)