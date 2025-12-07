"""
Page 4: Sports and Events (The Competition Arena)
==================================================
Analyzes Olympic data from the perspective of sports and events.

Author: Your Name
Date: December 2024
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="Sports and Events - Paris 2024",
    page_icon="🏟️",
    layout="wide"
)

# Define paths
DATA_DIR = Path(__file__).parent.parent / 'data'

# ============================================================================
# DATA LOADING
# ============================================================================

@st.cache_data
def load_data():
    """Load all necessary datasets for Sports and Events page"""
    try:
        events_enriched = pd.read_csv(DATA_DIR / 'events_enriched.csv')
        sport_summary = pd.read_csv(DATA_DIR / 'sport_summary.csv')
        schedules_cleaned = pd.read_csv(DATA_DIR / 'schedules_cleaned.csv')
        venues_cleaned = pd.read_csv(DATA_DIR / 'venues_cleaned.csv')
        medalists_enriched = pd.read_csv(DATA_DIR / 'medalists_enriched.csv')
        medals_enriched = pd.read_csv(DATA_DIR / 'medals_enriched.csv')
        
        # Parse dates
        schedules_cleaned['start_date'] = pd.to_datetime(schedules_cleaned['start_date'], errors='coerce')
        schedules_cleaned['end_date'] = pd.to_datetime(schedules_cleaned['end_date'], errors='coerce')
        events_enriched['start_date'] = pd.to_datetime(events_enriched['start_date'], errors='coerce')
        events_enriched['end_date'] = pd.to_datetime(events_enriched['end_date'], errors='coerce')
        venues_cleaned['date_start'] = pd.to_datetime(venues_cleaned['date_start'], errors='coerce')
        venues_cleaned['date_end'] = pd.to_datetime(venues_cleaned['date_end'], errors='coerce')
        
        # Calculate Venue Duration Days for Section 3
        venues_cleaned['duration_days'] = (venues_cleaned['date_end'] - venues_cleaned['date_start']).dt.days + 1
        
        return {
            'events': events_enriched,
            'sport_summary': sport_summary,
            'schedules': schedules_cleaned,
            'venues': venues_cleaned,
            'medalists': medalists_enriched,
            'medals': medals_enriched
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

st.sidebar.header("🔍 Sports & Events Filters")

# Sport filter
sports_list = ['All'] + sorted(data['sport_summary']['sport'].dropna().unique().tolist())
selected_sport = st.sidebar.selectbox(
    "Select Sport",
    sports_list,
    index=0,
    key='sport_filter'
)

# Venue filter
venues_list = ['All'] + sorted(data['venues']['venue'].dropna().unique().tolist())
selected_venue = st.sidebar.selectbox(
    "Select Venue",
    venues_list,
    index=0,
    key='venue_filter'
)

# Gender filter
genders = ['All', 'Men', 'Women', 'Mixed']
selected_gender = st.sidebar.selectbox(
    "Select Gender Category",
    genders,
    index=0,
    key='gender_filter'
)


st.sidebar.markdown("---")
st.sidebar.info("💡 **Tip**: Explore schedules, venues, and medal distributions by sport!")

# ============================================================================
# APPLY FILTERS
# ============================================================================

def apply_filters(df):
    """Apply sidebar filters to dataframe"""
    filtered_df = df.copy()
    
    # Sport filter
    if selected_sport != 'All':
        if 'sport' in filtered_df.columns:
            filtered_df = filtered_df[filtered_df['sport'] == selected_sport]
        elif 'discipline' in filtered_df.columns:
            filtered_df = filtered_df[filtered_df['discipline'] == selected_sport]
    
    # Venue filter
    if selected_venue != 'All' and 'venue' in filtered_df.columns:
        filtered_df = filtered_df[filtered_df['venue'] == selected_venue]
    
    # Gender filter
    if selected_gender != 'All' and 'gender' in filtered_df.columns:
        filtered_df = filtered_df[filtered_df['gender'] == selected_gender]
    
    # Suppression du filtre par date
    
    return filtered_df

# ============================================================================
# PAGE HEADER
# ============================================================================

st.title("🏟️ Sports and Events: The Competition Arena")
st.markdown("""
Explore the competitive landscape of Paris 2024. Analyze event schedules, 
venue locations, and medal distributions across different sports and disciplines.
""")

st.markdown("---")

# ============================================================================
# SECTION 1: EVENT SCHEDULE (GANTT CHART)
# ============================================================================

st.header("📅 Event Schedule Timeline")
st.markdown("**Gantt chart showing event schedules by sport or venue**")

# View options
schedule_view = st.radio(
    "Group schedule by:",
    ["Sport/Discipline", "Venue", "Gender Category"],
    horizontal=True,
    key='schedule_view'
)

# Apply filters
filtered_schedules = apply_filters(data['schedules'])

# Limit to top entries for better visualization
if schedule_view == "Sport/Discipline":
    top_disciplines = filtered_schedules['discipline'].value_counts().head(20).index
    schedule_data = filtered_schedules[filtered_schedules['discipline'].isin(top_disciplines)]
    color_column = 'discipline'
    y_column = 'event'
    title_suffix = "by Sport/Discipline (Top 20)"
elif schedule_view == "Venue":
    top_venues = filtered_schedules['venue'].value_counts().head(15).index
    schedule_data = filtered_schedules[filtered_schedules['venue'].isin(top_venues)]
    color_column = 'venue'
    y_column = 'event'
    title_suffix = "by Venue (Top 15)"
else:  # Gender Category
    schedule_data = filtered_schedules
    color_column = 'gender'
    y_column = 'event'
    title_suffix = "by Gender Category"

# Remove rows with missing dates
schedule_data = schedule_data.dropna(subset=['start_date', 'end_date'])

if len(schedule_data) > 0:
    # Create Gantt chart
    fig_gantt = px.timeline(
        schedule_data.head(50),  # Limit to 50 events for readability
        x_start='start_date',
        x_end='end_date',
        y=y_column,
        color=color_column,
        title=f'Event Schedule {title_suffix} (Showing up to 50 events)',
        labels={'event': 'Event', 'start_date': 'Start Date', 'end_date': 'End Date'},
        hover_data=['discipline', 'venue', 'phase', 'status'],
        height=800
    )
    
    fig_gantt.update_yaxes(categoryorder='total ascending')
    fig_gantt.update_layout(
        xaxis_title='Date',
        yaxis_title='Event',
        showlegend=True,
        hovermode='closest'
    )
    
    st.plotly_chart(fig_gantt, use_container_width=True)
    
    # Schedule statistics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("📊 Total Events", len(schedule_data))
    
    with col2:
        num_disciplines = schedule_data['discipline'].nunique()
        st.metric("🏅 Disciplines", num_disciplines)
    
    with col3:
        num_venues = schedule_data['venue'].nunique()
        st.metric("🏟️ Venues", num_venues)
    
    with col4:
        if schedule_data['start_date'].notna().any():
            duration = (schedule_data['end_date'].max() - schedule_data['start_date'].min()).days
            st.metric("📆 Duration", f"{duration} days")
else:
    st.warning("⚠️ No schedule data available for the current filters.")

st.markdown("---")

# ============================================================================
# SECTION 2: MEDAL COUNT BY SPORT (TREEMAP)
# ============================================================================

st.header("🏆 Medal Count by Sport")
st.markdown("**Treemap visualization of medal distribution across sports**")

# Prepare medal data by sport
filtered_medals = apply_filters(data['medals'])

# Group by discipline and medal type
medal_by_sport = filtered_medals.groupby(['discipline', 'medal_type']).size().reset_index(name='count')

if len(medal_by_sport) > 0:
    # Create tabs for different views
    tab1, tab2 = st.tabs(["🔲 Treemap", "📊 Bar Chart"])
    
    with tab1:
        # Treemap
        fig_treemap = px.treemap(
            medal_by_sport,
            path=['discipline', 'medal_type'],
            values='count',
            color='medal_type',
            color_discrete_map={
                'Gold': '#FFE766',
                'Silver': '#C0C0C0',
                'Bronze': '#d99d73'
            },
            title='Medal Distribution by Sport (Treemap)',
            height=700
        )
        
        fig_treemap.update_traces(textinfo='label+value+percent parent')
        st.plotly_chart(fig_treemap, use_container_width=True)
    
    with tab2:
        # Grouped bar chart
        medal_pivot = medal_by_sport.pivot(index='discipline', columns='medal_type', values='count').fillna(0)
        medal_pivot['Total'] = medal_pivot.sum(axis=1)
        medal_pivot = medal_pivot.sort_values('Total', ascending=False).head(20)
        medal_pivot = medal_pivot.reset_index()
        
        # Get available medal columns
        available_medal_types = [col for col in ['Gold', 'Silver', 'Bronze'] if col in medal_pivot.columns]
        
        if not available_medal_types:
            st.warning("No medal data available for bar chart visualization.")
        else:
            # CORRECTION DE L'ERREUR DE COUPURE DANS MELT ICI
            medal_melted = medal_pivot.melt(
                id_vars=['discipline'],
                value_vars=available_medal_types,
                var_name='Medal Type',
                value_name='Count'
            )
            # FIN DE LA CORRECTION
            
            fig_bar = px.bar(
                medal_melted,
                x='discipline',
                y='Count',
                color='Medal Type',
                barmode='group',
                color_discrete_map={
                    'Gold': '#FFE766',
                    'Silver': '#C0C0C0',
                    'Bronze': '#d99d73'
                },
                title='Medal Count by Sport (Top 20)',
                labels={'discipline': 'Sport/Discipline', 'Count': 'Number of Medals'},
                height=600
            )
            
            fig_bar.update_xaxes(tickangle=-45)
            st.plotly_chart(fig_bar, use_container_width=True)
    
    # Sport statistics table
    st.subheader("📋 Medal Statistics by Sport")
    
    # Harmonisation des noms de colonnes pour compatibilité avec le code
    sport_stats = data['sport_summary'].copy()
    # Correction : renommer les colonnes pour correspondre à l'attendu par le code
    sport_stats = sport_stats.rename(columns={
        'Bronze Medal': 'bronze_medals',
        'Gold Medal': 'gold_medals',
        'Silver Medal': 'silver_medals'
    })

    if selected_sport != 'All':
        sport_stats = sport_stats[sport_stats['sport'] == selected_sport]
    
    # Sort by total medals
    sport_stats = sport_stats.sort_values('total_medals', ascending=False).head(20)
    
    display_cols = ['sport', 'gold_medals', 'silver_medals', 'bronze_medals', 'total_medals', 'num_events']
    # 'medals_per_event' peut ne pas exister, on l'ajoute si besoin
    if 'medals_per_event' not in sport_stats.columns and 'total_medals' in sport_stats.columns and 'num_events' in sport_stats.columns:
        sport_stats['medals_per_event'] = sport_stats['total_medals'] / sport_stats['num_events']
    display_cols.append('medals_per_event')

    if all(col in sport_stats.columns for col in display_cols):
        display_df = sport_stats[display_cols].copy()
        display_df.columns = ['Sport', '🥇 Gold', '🥈 Silver', '🥉 Bronze', '📊 Total', '🎯 Events', '📈 Medals/Event']
        
        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True,
            height=400
        )
    else:
        st.warning("⚠️ The required columns for the statistics table are missing in 'sport_summary.csv'.")
else:
    st.warning("⚠️ No medal data available for the current filters.")

st.markdown("---")

# ============================================================================
# SECTION 3: VENUE MAP
# ============================================================================

st.header("🗺️ Olympic Venue Map")
st.markdown("**Interactive map showing locations of Olympic venues in Paris**")

# Prepare venue data
venues_data = data['venues'].copy()

# The venue filter logic is tricky here. We want to show all venues unless a specific sport is selected.
# If a specific sport is selected, we filter venues that host that sport.
if selected_sport != 'All':
    # Filter venues that host the selected sport
    # We use data['venues'] to get the 'sports' column, as 'schedules' DF does not have it.
    venues_data = venues_data[venues_data['sports'].str.contains(selected_sport, na=False, case=False)]

# Apply Venue filter (from sidebar)
if selected_venue != 'All':
    venues_data = venues_data[venues_data['venue'] == selected_venue]

# Remove venues without coordinates
venues_data = venues_data.dropna(subset=['latitude', 'longitude'])

if len(venues_data) > 0:
    # Add event count per venue (using the filtered schedules for accuracy)
    venue_event_count = filtered_schedules.groupby('venue').size().reset_index(name='event_count')
    
    # Merge event count into the venues data
    venues_data = venues_data.merge(venue_event_count, on='venue', how='left')
    venues_data['event_count'] = venues_data['event_count'].fillna(0).astype(int)
    
    # Create scatter mapbox
    fig_map = px.scatter_mapbox(
        venues_data,
        lat='latitude',
        lon='longitude',
        hover_name='venue',
        hover_data={
            'latitude': False,
            'longitude': False,
            'sports': True,
            'event_count': True,
            'duration_days': True
        },
        color='event_count',
        size='event_count',
        color_continuous_scale='Viridis',
        size_max=25,
        zoom=10,
        height=600,
        title='Olympic Venues in Paris and Surrounding Areas'
    )
    
    fig_map.update_layout(
        mapbox_style='open-street-map',
        mapbox=dict(
            center=dict(lat=48.8566, lon=2.3522),  # Paris center
            zoom=10
        ),
        margin=dict(l=0, r=0, t=40, b=0)
    )
    
    st.plotly_chart(fig_map, use_container_width=True)
    
    # Venue statistics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("🏟️ Total Venues", len(venues_data))
    
    with col2:
        total_events = venues_data['event_count'].sum()
        st.metric("🎯 Total Events", int(total_events))
    
    with col3:
        busiest_venue = venues_data.nlargest(1, 'event_count')
        if not busiest_venue.empty and busiest_venue['event_count'].values[0] > 0:
            st.metric("🔥 Busiest Venue", busiest_venue['venue'].values[0])
        else:
            st.metric("🔥 Busiest Venue", "N/A")

    
    with col4:
        avg_events = venues_data['event_count'].mean()
        st.metric("📊 Avg Events/Venue", f"{avg_events:.1f}")
    
    # Venue details table
    st.subheader("📋 Venue Details")
    
    venue_display = venues_data[['venue', 'sports', 'event_count', 'date_start', 'date_end', 'duration_days']].copy()
    venue_display.columns = ['Venue', 'Sports', 'Event Count', 'Start Date', 'End Date', 'Duration (days)']
    venue_display = venue_display.sort_values('Event Count', ascending=False)
    
    st.dataframe(
        venue_display,
        use_container_width=True,
        hide_index=True,
        height=400
    )
else:
    st.warning("⚠️ No venue data available for the current filters.")

st.markdown("---")

# ============================================================================
# SECTION 4: YOUTUBE SEARCH LINK FOR EVENTS
# ============================================================================

st.header("🔗 Find Event on YouTube")
st.markdown("**Select an event and get a direct YouTube search link for it. The event list reacts to the sidebar filters.**")

# Appliquer les filtres de la sidebar sur les événements
filtered_events = apply_filters(data['events'])

# Générer la liste des événements disponibles après filtres
event_options = filtered_events['event'].dropna().unique()
event_options_sorted = sorted(event_options)

selected_event = st.selectbox(
    "Select an event to search on YouTube:",
    event_options_sorted,
    key="youtube_event_select"
)

if selected_event:
    # Générer le lien YouTube avec le nom de l'événement entre guillemets
    search_query = f'"{selected_event}" olympics'
    youtube_url = f"https://www.youtube.com/results?search_query={search_query.replace(' ', '+')}"
    st.markdown(
        f"[🔎 Search for **{selected_event}** on YouTube]({youtube_url})",
        unsafe_allow_html=True
    )

st.markdown("---")

# ============================================================================
# BONUS: SPORT DEEP DIVE
# ============================================================================

st.header("🔍 Sport Deep Dive Analysis")
st.markdown("**Detailed analysis of a selected sport**")

# Sport selector - use all sports list
deep_dive_sport = st.selectbox(
    "Select a sport for detailed analysis:",
    sorted(data['sport_summary']['sport'].unique()),
    key='deep_dive_sport'
)

if deep_dive_sport:
    # Get sport data from summary
    sport_data = data['sport_summary'][data['sport_summary']['sport'] == deep_dive_sport]
    
    if not sport_data.empty:
        sport_info = sport_data.iloc[0]
        
        # Sport overview
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            st.metric("🥇 Gold Medals", int(sport_info.get('gold_medals', 0)))
        
        with col2:
            st.metric("🥈 Silver Medals", int(sport_info.get('silver_medals', 0)))
        
        with col3:
            st.metric("🥉 Bronze Medals", int(sport_info.get('bronze_medals', 0)))
        
        with col4:
            st.metric("🎯 Total Events", int(sport_info.get('num_events', 0)))
        
        with col5:
            num_disciplines_val = int(sport_info.get('num_disciplines', 0))
            st.metric("📊 Disciplines", num_disciplines_val)
        
        # Detailed visualizations
        col_left, col_right = st.columns(2)
        
        with col_left:
            # Medal winners by country
            st.markdown("#### 🌍 Top Countries in " + deep_dive_sport)
            
            # Filter medals by discipline (which is the sport name in this case)
            sport_medals = data['medals'][data['medals']['discipline'] == deep_dive_sport]
            country_medals = sport_medals.groupby('country').size().reset_index(name='medal_count')
            country_medals = country_medals.sort_values('medal_count', ascending=False).head(10)
            
            if not country_medals.empty:
                fig_countries = px.bar(
                    country_medals,
                    x='country',
                    y='medal_count',
                    title=f'Top 10 Countries in {deep_dive_sport}',
                    labels={'country': 'Country', 'medal_count': 'Total Medals'},
                    color='medal_count',
                    color_continuous_scale='Blues',
                    height=400
                )
                fig_countries.update_xaxes(tickangle=-45)
                st.plotly_chart(fig_countries, use_container_width=True)
            else:
                st.info("No medal data available for this sport.")
        
        with col_right:
            # Gender distribution in sport
            st.markdown("#### ⚖️ Gender Distribution in " + deep_dive_sport)
            
            # Use 'schedules' which contains the 'discipline' and 'gender' columns
            sport_schedules = data['schedules'][data['schedules']['discipline'] == deep_dive_sport]
            gender_dist = sport_schedules['gender'].value_counts().reset_index()
            gender_dist.columns = ['Gender', 'Count']
            
            if not gender_dist.empty:
                fig_gender = px.pie(
                    gender_dist,
                    values='Count',
                    names='Gender',
                    title=f'Events by Gender in {deep_dive_sport}',
                    color='Gender',
                    color_discrete_map={
                        'Men': '#3498db',
                        'Women': '#e74c3c',
                        'Mixed': '#9b59b6',
                        'Open': '#95a5a6'
                    },
                    height=400
                )
                st.plotly_chart(fig_gender, use_container_width=True)
            else:
                st.info("No schedule data available for this sport.")
        
        # Event list for this sport
        st.markdown("#### 📋 Events in " + deep_dive_sport)
        
        # Use 'events' which contains the 'sport' column
        sport_events = data['events'][data['events']['sport'] == deep_dive_sport]
        
        if not sport_events.empty:
            event_display = sport_events[['event', 'gender', 'venue', 'start_date']].copy()
            event_display.columns = ['Event', 'Gender', 'Venue', 'Start Date']
            event_display = event_display.sort_values('Start Date')
            
            st.dataframe(
                event_display,
                use_container_width=True,
                hide_index=True,
                height=300
            )
        else:
            st.info("No event details available for this sport.")

st.markdown("---")

# ============================================================================
# BONUS: EVENT PHASE ANALYSIS
# ============================================================================

st.header("🎭 Event Phase Distribution")
st.markdown("**Analysis of competition phases (Qualifications, Finals, etc.)**")

phase_data = apply_filters(data['schedules'])
phase_counts = phase_data['phase'].value_counts().reset_index()
phase_counts.columns = ['Phase', 'Count']

if not phase_counts.empty:
    col1, col2 = st.columns(2)
    
    with col1:
        # Pie chart
        fig_phase_pie = px.pie(
            phase_counts.head(10),
            values='Count',
            names='Phase',
            title='Event Distribution by Phase',
            height=400
        )
        st.plotly_chart(fig_phase_pie, use_container_width=True)
    
    with col2:
        # Bar chart
        fig_phase_bar = px.bar(
            phase_counts.head(15),
            x='Phase',
            y='Count',
            title='Event Count by Phase (Top 15)',
            labels={'Phase': 'Competition Phase', 'Count': 'Number of Events'},
            color='Count',
            color_continuous_scale='Teal',
            height=400
        )
        fig_phase_bar.update_xaxes(tickangle=-45)
        st.plotly_chart(fig_phase_bar, use_container_width=True)

st.markdown("---")

# ============================================================================
# FOOTER
# ============================================================================

st.markdown("""
<div style='text-align: center; color: gray; padding: 20px;'>
    <p>Paris 2024 Olympics Dashboard | Page 4: Sports and Events 🏟️</p>
    <p>Data Source: Paris 2024 Olympics Official Dataset</p>
</div>
""", unsafe_allow_html=True)