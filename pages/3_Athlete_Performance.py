"""
Page 3: Athlete Performance (The Human Story)
==============================================
Analyzes Olympic data from the perspective of athletes.

Author: Your Name
Date: December 2024
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
from pathlib import Path

# Page configuration
st.set_page_config(
    page_title="Athlete Performance - Paris 2024",
    page_icon="👤",
    layout="wide"
)

# Define paths
DATA_DIR = Path(__file__).parent.parent / 'data'

# ============================================================================
# DATA LOADING
# ============================================================================

@st.cache_data
def load_data():
    """Load all necessary datasets for Athlete Performance page"""
    try:
        # Load the athletes dataset with images if available
        athletes_with_images = DATA_DIR / 'athletes_with_images.csv'
        if athletes_with_images.exists():
            athletes_enriched = pd.read_csv(athletes_with_images)
        else:
            athletes_enriched = pd.read_csv(DATA_DIR / 'athletes_enriched.csv')

        athlete_medals_summary = pd.read_csv(DATA_DIR / 'athlete_medals_summary.csv')
        gender_distribution = pd.read_csv(DATA_DIR / 'gender_distribution.csv')
        medals_enriched = pd.read_csv(DATA_DIR / 'medals_enriched.csv')
        medalists_enriched = pd.read_csv(DATA_DIR / 'medalists_enriched.csv')
        
        return {
            'athletes': athletes_enriched,
            'athlete_medals': athlete_medals_summary,
            'gender_dist': gender_distribution,
            'medals': medals_enriched,
            'medalists': medalists_enriched
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

st.sidebar.header("🔍 Athlete Filters")

# Country filter
countries = ['All'] + sorted(data['athletes']['country'].dropna().unique().tolist())
selected_country = st.sidebar.selectbox(
    "Select Country",
    countries,
    index=0,
    key='country_filter'
)

# Sport filter
sports = ['All'] + sorted(data['athletes']['disciplines'].dropna().unique().tolist())
selected_sport = st.sidebar.selectbox(
    "Select Sport/Discipline",
    sports,
    index=0,
    key='sport_filter'
)

# Gender filter
genders = ['All', 'Male', 'Female']
selected_gender = st.sidebar.selectbox(
    "Select Gender",
    genders,
    index=0,
    key='gender_filter'
)

# Age range filter
if data['athletes']['age'].notna().any():
    min_age = int(data['athletes']['age'].min())
    max_age = int(data['athletes']['age'].max())
    age_range = st.sidebar.slider(
        "Age Range",
        min_value=min_age,
        max_value=max_age,
        value=(min_age, max_age),
        key='age_filter'
    )
else:
    age_range = (0, 100)

st.sidebar.markdown("---")
st.sidebar.info("💡 **Tip**: Use filters to explore specific countries or sports!")

# ============================================================================
# APPLY FILTERS
# ============================================================================

def apply_filters(df):
    """Apply sidebar filters to dataframe"""
    filtered_df = df.copy()
    
    if selected_country != 'All' and 'country' in filtered_df.columns:
        filtered_df = filtered_df[filtered_df['country'] == selected_country]
    
    if selected_sport != 'All' and 'disciplines' in filtered_df.columns:
        filtered_df = filtered_df[filtered_df['disciplines'].str.contains(selected_sport, na=False)]
    
    if selected_gender != 'All' and 'gender' in filtered_df.columns:
        filtered_df = filtered_df[filtered_df['gender'] == selected_gender]
    
    if 'age' in filtered_df.columns:
        filtered_df = filtered_df[
            (filtered_df['age'] >= age_range[0]) & 
            (filtered_df['age'] <= age_range[1])
        ]
    
    return filtered_df

# ============================================================================
# PAGE HEADER
# ============================================================================

st.title("👤 Athlete Performance: The Human Story")
st.info("📸 Athlete photos are retrieved from Wikipedia automatically when available.")
st.markdown("""
Dive deep into the athletes' world. Explore individual profiles, demographics, 
and discover the champions of Paris 2024.
""")

st.markdown("---")

# ============================================================================
# SECTION 1: ATHLETE DETAILED PROFILE CARD
# ============================================================================

st.header("🔍 Athlete Profile Search")
st.markdown("**Search and explore detailed athlete information**")

search_col1, search_col2 = st.columns([3, 1])

with search_col1:
    athlete_names = sorted(data['athletes']['name'].dropna().unique().tolist())
    selected_athlete = st.selectbox(
        "Search for an athlete by name",
        options=[''] + athlete_names,
        format_func=lambda x: "-- Select an athlete --" if x == '' else x,
        key='athlete_search'
    )

with search_col2:
    st.markdown("###")
    search_button = st.button("🔎 Search", use_container_width=True)

if selected_athlete and selected_athlete != '':
    athlete_data = data['athletes'][data['athletes']['name'] == selected_athlete].iloc[0]
    
    st.markdown("---")
    st.subheader(f"📋 Profile: {athlete_data['name']}")
    
    col1, col2, col3, col4 = st.columns([1, 2, 2, 2])
    
    with col1:
        # Display athlete image if available
        if 'image_url' in athlete_data and pd.notna(athlete_data['image_url']):
            st.image(athlete_data['image_url'], width=180, caption="Official photo")
        else:
            st.markdown("""
            <div style='text-align: center; padding: 20px; background-color: #f0f2f6; border-radius: 10px;'>
                <div style='font-size: 80px;'>👤</div>
                <p style='font-size: 12px; color: gray;'>No Image Available</p>
            </div>
            """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("#### 🏳️ Basic Information")
        st.markdown(f"**Full Name:** {athlete_data['name']}")
        st.markdown(f"**Country:** {athlete_data['country']} ({athlete_data['country_code']})")
        st.markdown(f"**Gender:** {'👨' if athlete_data['gender'] == 'Male' else '👩'} {athlete_data['gender']}")
        
        age_display = f"{int(athlete_data['age'])}" if pd.notna(athlete_data['age']) else "N/A"
        st.markdown(f"**Age:** {age_display} years")
    
    with col3:
        st.markdown("#### 📊 Physical Stats")
        height_display = f"{athlete_data['height']:.0f} cm" if pd.notna(athlete_data['height']) else "N/A"
        weight_display = f"{athlete_data['weight']:.0f} kg" if pd.notna(athlete_data['weight']) else "N/A"
        st.markdown(f"**Height:** {height_display}")
        st.markdown(f"**Weight:** {weight_display}")
    
    with col4:
        st.markdown("#### 🏅 Sports & Team")
        sports_display = athlete_data['disciplines'] if pd.notna(athlete_data['disciplines']) else "N/A"
        st.markdown(f"**Sport(s):** {sports_display}")
        team_display = athlete_data['team_name'] if pd.notna(athlete_data['team_name']) else "Individual"
        st.markdown(f"**Team:** {team_display}")
    
    athlete_medals = data['medalists'][data['medalists']['name'] == selected_athlete]
    if not athlete_medals.empty:
        st.markdown("#### 🏆 Medal Achievements")
        gold = len(athlete_medals[athlete_medals['medal_type'] == 'Gold'])
        silver = len(athlete_medals[athlete_medals['medal_type'] == 'Silver'])
        bronze = len(athlete_medals[athlete_medals['medal_type'] == 'Bronze'])
        colg, cols, colb, colt = st.columns(4)
        colg.metric("🥇 Gold", gold)
        cols.metric("🥈 Silver", silver)
        colb.metric("🥉 Bronze", bronze)
        colt.metric("📊 Total", len(athlete_medals))
    else:
        st.info("ℹ️ This athlete did not win any medals at Paris 2024.")

st.markdown("---")

# (Le reste du fichier continue inchangé — analyses d’âge, de genre, etc.)


# ============================================================================
# SECTION 2: ATHLETE AGE DISTRIBUTION
# ============================================================================

st.header("📊 Athlete Age Distribution")
st.markdown("**Analyze age patterns across sports and genders**")

# Apply filters to athletes data
filtered_athletes = apply_filters(data['athletes'])

# Remove rows with missing age
filtered_athletes_with_age = filtered_athletes[filtered_athletes['age'].notna()]

if len(filtered_athletes_with_age) > 0:
    # Create tabs for different views
    tab1, tab2 = st.tabs(["📦 Box Plot", "🎻 Violin Plot"])
    
    with tab1:
        # Box plot by gender and sport
        view_option = st.radio(
            "View age distribution by:",
            ["Gender", "Sport/Discipline"],
            horizontal=True,
            key='age_view_box'
        )
        
        if view_option == "Gender":
            fig_age_box = px.box(
                filtered_athletes_with_age,
                x='gender',
                y='age',
                color='gender',
                title='Age Distribution by Gender',
                labels={'age': 'Age (years)', 'gender': 'Gender'},
                color_discrete_map={'Male': '#3498db', 'Female': '#e74c3c'},
                points='outliers',
                height=500
            )
        else:
            # Get top sports by athlete count
            top_sports = filtered_athletes_with_age['disciplines'].value_counts().head(15).index
            sports_data = filtered_athletes_with_age[filtered_athletes_with_age['disciplines'].isin(top_sports)]
            
            fig_age_box = px.box(
                sports_data,
                x='disciplines',
                y='age',
                color='disciplines',
                title='Age Distribution by Sport (Top 15)',
                labels={'age': 'Age (years)', 'disciplines': 'Sport'},
                points='outliers',
                height=500
            )
            fig_age_box.update_xaxes(tickangle=-45)
        
        fig_age_box.update_layout(showlegend=False)
        st.plotly_chart(fig_age_box, use_container_width=True)
    
    with tab2:
        # Violin plot
        view_option_violin = st.radio(
            "View age distribution by:",
            ["Gender", "Sport/Discipline"],
            horizontal=True,
            key='age_view_violin'
        )
        
        if view_option_violin == "Gender":
            fig_age_violin = px.violin(
                filtered_athletes_with_age,
                x='gender',
                y='age',
                color='gender',
                title='Age Distribution by Gender (Violin Plot)',
                labels={'age': 'Age (years)', 'gender': 'Gender'},
                color_discrete_map={'Male': '#3498db', 'Female': '#e74c3c'},
                box=True,
                points='outliers',
                height=500
            )
        else:
            # Get top sports
            top_sports = filtered_athletes_with_age['disciplines'].value_counts().head(10).index
            sports_data = filtered_athletes_with_age[filtered_athletes_with_age['disciplines'].isin(top_sports)]
            
            fig_age_violin = px.violin(
                sports_data,
                x='disciplines',
                y='age',
                color='disciplines',
                title='Age Distribution by Sport (Top 10)',
                labels={'age': 'Age (years)', 'disciplines': 'Sport'},
                box=True,
                points='outliers',
                height=500
            )
            fig_age_violin.update_xaxes(tickangle=-45)
        
        fig_age_violin.update_layout(showlegend=False)
        st.plotly_chart(fig_age_violin, use_container_width=True)
    
    # Age statistics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("👶 Youngest Athlete", f"{int(filtered_athletes_with_age['age'].min())} years")
    with col2:
        st.metric("👴 Oldest Athlete", f"{int(filtered_athletes_with_age['age'].max())} years")
    with col3:
        st.metric("📊 Average Age", f"{filtered_athletes_with_age['age'].mean():.1f} years")
    with col4:
        st.metric("📍 Median Age", f"{filtered_athletes_with_age['age'].median():.1f} years")
else:
    st.warning("⚠️ No athlete data available with the current filters.")

st.markdown("---")

# ============================================================================
# SECTION 3: GENDER DISTRIBUTION
# ============================================================================

st.header("⚖️ Gender Distribution Analysis")
st.markdown("**Explore gender balance across continents, countries, and sports**")

# Filter options
gender_view = st.selectbox(
    "Select View Level:",
    ["Overall", "By Continent", "By Country (Top 30)", "By Sport"],
    key='gender_view'
)

# Filter gender distribution data
if gender_view == "Overall":
    gender_data = data['gender_dist'][data['gender_dist']['category'] == 'Overall']
elif gender_view == "By Continent":
    gender_data = data['gender_dist'][data['gender_dist']['category'] == 'Continent']
elif gender_view == "By Country (Top 30)":
    gender_data = data['gender_dist'][data['gender_dist']['category'] == 'Country']
else:  # By Sport
    gender_data = data['gender_dist'][data['gender_dist']['category'] == 'Sport']
    # Get top 15 sports
    top_sports_by_count = gender_data.groupby('subcategory')['count'].sum().nlargest(15).index
    gender_data = gender_data[gender_data['subcategory'].isin(top_sports_by_count)]

# Apply country filter if needed
if selected_country != 'All' and gender_view == "By Country (Top 30)":
    gender_data = gender_data[gender_data['subcategory'] == selected_country]

if len(gender_data) > 0:
    # Create visualization tabs
    tab1, tab2 = st.tabs(["🥧 Pie Chart", "📊 Bar Chart"])
    
    with tab1:
        if gender_view == "Overall":
            # Simple pie chart for overall
            fig_gender_pie = px.pie(
                gender_data,
                values='count',
                names='gender',
                title='Overall Gender Distribution',
                color='gender',
                color_discrete_map={'Male': '#3498db', 'Female': '#e74c3c', 'Unknown': '#95a5a6'},
                height=500
            )
            fig_gender_pie.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig_gender_pie, use_container_width=True)
        else:
            # Sunburst for hierarchical view
            fig_gender_sunburst = px.sunburst(
                gender_data,
                path=['subcategory', 'gender'],
                values='count',
                color='gender',
                color_discrete_map={'Male': '#3498db', 'Female': '#e74c3c', 'Unknown': '#95a5a6'},
                title=f'Gender Distribution - {gender_view}',
                height=600
            )
            st.plotly_chart(fig_gender_sunburst, use_container_width=True)
    
    with tab2:
        # Stacked bar chart
        if gender_view != "Overall":
            fig_gender_bar = px.bar(
                gender_data,
                x='subcategory',
                y='percentage',
                color='gender',
                title=f'Gender Distribution (%) - {gender_view}',
                labels={'subcategory': gender_view.replace('By ', ''), 'percentage': 'Percentage (%)'},
                color_discrete_map={'Male': '#3498db', 'Female': '#e74c3c', 'Unknown': '#95a5a6'},
                text='percentage',
                height=500,
                barmode='stack'
            )
            fig_gender_bar.update_traces(texttemplate='%{text:.1f}%', textposition='inside')
            fig_gender_bar.update_xaxes(tickangle=-45)
            st.plotly_chart(fig_gender_bar, use_container_width=True)
        else:
            # Simple bar for overall
            fig_gender_bar = px.bar(
                gender_data,
                x='gender',
                y='count',
                color='gender',
                title='Overall Gender Distribution',
                labels={'gender': 'Gender', 'count': 'Number of Athletes'},
                color_discrete_map={'Male': '#3498db', 'Female': '#e74c3c', 'Unknown': '#95a5a6'},
                text='count',
                height=500
            )
            fig_gender_bar.update_traces(textposition='outside')
            st.plotly_chart(fig_gender_bar, use_container_width=True)
    
    # Gender statistics
    total_count = gender_data['count'].sum()
    male_count = gender_data[gender_data['gender'] == 'Male']['count'].sum()
    female_count = gender_data[gender_data['gender'] == 'Female']['count'].sum()
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("👥 Total Athletes", int(total_count))
    with col2:
        st.metric("👨 Male Athletes", int(male_count))
    with col3:
        st.metric("👩 Female Athletes", int(female_count))
    with col4:
        gender_ratio = (female_count / male_count * 100) if male_count > 0 else 0
        st.metric("⚖️ Female/Male Ratio", f"{gender_ratio:.1f}%")
else:
    st.warning("⚠️ No gender distribution data available for the current selection.")

st.markdown("---")

# ============================================================================
# SECTION 4: TOP ATHLETES BY MEDALS
# ============================================================================

st.header("🏆 Top Athletes by Medals")
st.markdown("**Celebrating the champions of Paris 2024**")

# Filter options
top_n = st.slider("Number of top athletes to display:", 5, 30, 10, key='top_athletes_slider')

# Apply basic filters to medal data
filtered_medal_athletes = data['athlete_medals'].copy()

if selected_country != 'All':
    filtered_medal_athletes = filtered_medal_athletes[filtered_medal_athletes['country'] == selected_country]

if selected_gender != 'All':
    filtered_medal_athletes = filtered_medal_athletes[filtered_medal_athletes['gender'] == selected_gender]

# Get top N athletes
top_athletes = filtered_medal_athletes.head(top_n)

if len(top_athletes) > 0:
    # Create stacked bar chart
    top_athletes_melted = top_athletes.melt(
        id_vars=['name', 'country', 'rank'],
        value_vars=['gold_count', 'silver_count', 'bronze_count'],
        var_name='Medal Type',
        value_name='Count'
    )
    
    # Clean medal type names
    top_athletes_melted['Medal Type'] = top_athletes_melted['Medal Type'].str.replace('_count', '').str.capitalize()
    
    fig_top_athletes = px.bar(
        top_athletes_melted,
        x='name',
        y='Count',
        color='Medal Type',
        title=f'Top {top_n} Athletes by Medal Count',
        labels={'name': 'Athlete', 'Count': 'Number of Medals'},
        color_discrete_map={
            'Gold': '#FFD700',
            'Silver': '#C0C0C0',
            'Bronze': '#CD7F32'
        },
        text='Count',
        height=600,
        hover_data=['country']
    )
    
    fig_top_athletes.update_traces(textposition='inside')
    fig_top_athletes.update_xaxes(tickangle=-45)
    fig_top_athletes.update_layout(barmode='stack', xaxis={'categoryorder': 'total descending'})
    
    st.plotly_chart(fig_top_athletes, use_container_width=True)
    
    # Detailed table
    st.subheader(f"📋 Top {top_n} Athletes - Detailed View")
    
    display_cols = ['rank', 'name', 'country', 'gender', 'gold_count', 'silver_count', 'bronze_count', 'total_medals', 'disciplines']
    display_df = top_athletes[display_cols].copy()
    display_df.columns = ['Rank', 'Name', 'Country', 'Gender', '🥇 Gold', '🥈 Silver', '🥉 Bronze', '📊 Total', 'Sport(s)']
    
    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True,
        height=400
    )
    
    # Champion spotlight
    st.markdown("---")
    st.subheader("🌟 Champion Spotlight")
    
    champion = top_athletes.iloc[0]
    
    spotlight_col1, spotlight_col2, spotlight_col3 = st.columns([1, 2, 2])
    
    with spotlight_col1:
        st.markdown("""
        <div style='text-align: center; padding: 20px; background-color: #FFD700; border-radius: 10px;'>
            <div style='font-size: 80px;'>🏆</div>
            <p style='font-size: 14px; font-weight: bold;'>TOP MEDALIST</p>
        </div>
        """, unsafe_allow_html=True)
    
    with spotlight_col2:
        st.markdown(f"### {champion['name']}")
        st.markdown(f"**Country:** {champion['country']}")
        st.markdown(f"**Gender:** {champion['gender']}")
        st.markdown(f"**Sport(s):** {champion['disciplines']}")
    
    with spotlight_col3:
        st.metric("🥇 Gold Medals", int(champion['gold_count']))
        st.metric("🥈 Silver Medals", int(champion['silver_count']))
        st.metric("🥉 Bronze Medals", int(champion['bronze_count']))
        st.metric("📊 Total Medals", int(champion['total_medals']))
else:
    st.warning("⚠️ No medal data available for the current filters.")

st.markdown("---")

# ============================================================================
# BONUS: ATHLETE STATISTICS DASHBOARD
# ============================================================================

st.header("📈 Athlete Statistics Dashboard")
st.markdown("**Quick insights about the athlete population**")

filtered_athletes = apply_filters(data['athletes'])

stat_col1, stat_col2, stat_col3, stat_col4, stat_col5 = st.columns(5)

with stat_col1:
    st.metric("👥 Total Athletes", len(filtered_athletes))

with stat_col2:
    num_countries = filtered_athletes['country'].nunique()
    st.metric("🌍 Countries Represented", num_countries)

with stat_col3:
    num_sports = filtered_athletes['disciplines'].nunique()
    st.metric("🏅 Sports/Disciplines", num_sports)

with stat_col4:
    avg_height = filtered_athletes['height'].mean()
    height_display = f"{avg_height:.0f} cm" if pd.notna(avg_height) else "N/A"
    st.metric("📏 Avg Height", height_display)

with stat_col5:
    avg_weight = filtered_athletes['weight'].mean()
    weight_display = f"{avg_weight:.0f} kg" if pd.notna(avg_weight) else "N/A"
    st.metric("⚖️ Avg Weight", weight_display)

st.markdown("---")

# ============================================================================
# FOOTER
# ============================================================================

st.markdown("""
<div style='text-align: center; color: gray; padding: 20px;'>
    <p>Paris 2024 Olympics Dashboard | Page 3: Athlete Performance 👤</p>
    <p>Data Source: Paris 2024 Olympics Official Dataset</p>
</div>
""", unsafe_allow_html=True)