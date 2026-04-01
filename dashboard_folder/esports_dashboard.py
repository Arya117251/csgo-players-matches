import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
import google.generativeai as genai
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# ========================================
# PAGE CONFIG & STYLING
# ========================================

st.set_page_config(
    page_title="CS:GO Esports Analytics",
    page_icon="🎮",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for esports theme
st.markdown("""
<style>
    /* Main background */
    .stApp {
        background-color: #0E1117;
    }

    /* Headers */
    h1, h2, h3 {
        color: #9D4EDD !important;
        font-family: 'Rajdhani', sans-serif;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 2px;
    }

    /* Metric cards */
    [data-testid="stMetricValue"] {
        color: #00F5FF;
        font-size: 2rem;
        font-weight: bold;
    }

    [data-testid="stMetricLabel"] {
        color: #9D4EDD;
        font-size: 1rem;
        text-transform: uppercase;
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #1a1d29;
        border-right: 2px solid #9D4EDD;
    }

    /* Buttons */
    .stButton>button {
        background: linear-gradient(90deg, #9D4EDD 0%, #00F5FF 100%);
        color: white;
        border: none;
        border-radius: 5px;
        padding: 10px 25px;
        font-weight: bold;
        text-transform: uppercase;
        transition: all 0.3s;
    }

    .stButton>button:hover {
        transform: scale(1.05);
        box-shadow: 0 0 20px #9D4EDD;
    }

    /* Selectbox */
    .stSelectbox [data-baseweb="select"] {
        background-color: #1a1d29;
        border: 1px solid #9D4EDD;
    }

    /* Data frames */
    .dataframe {
        background-color: #1a1d29 !important;
        color: #00F5FF !important;
    }

    /* Divider */
    hr {
        border-color: #9D4EDD;
        margin: 2rem 0;
    }

    /* Custom metric box */
    .metric-box {
        background: linear-gradient(135deg, #1a1d29 0%, #2d1b3d 100%);
        border: 2px solid #9D4EDD;
        border-radius: 10px;
        padding: 20px;
        text-align: center;
        box-shadow: 0 0 15px rgba(157, 78, 221, 0.3);
    }

    /* Insights box */
    .insight-box {
        background: linear-gradient(135deg, #1a1d29 0%, #1d2d3d 100%);
        border-left: 4px solid #00F5FF;
        padding: 15px;
        margin: 10px 0;
        border-radius: 5px;
    }
</style>
""", unsafe_allow_html=True)

# ========================================
# DATA LOADING
# ========================================

@st.cache_data
def load_data():
    """Load and cache the cleaned datasets"""
    data_path = 'C:/claude/archive/cleaned_data'

    players_df = pd.read_csv(f'{data_path}/players_clean.csv')
    matches_df = pd.read_csv(f'{data_path}/matches_clean.csv')

    return players_df, matches_df

# Load data
try:
    players_df, matches_df = load_data()
except Exception as e:
    st.error(f"Error loading data: {e}")
    st.stop()

# ========================================
# HEADER
# ========================================

st.markdown("<h1 style='text-align: center; font-size: 3rem;'>🎮 CS:GO ESPORTS ANALYTICS 🎮</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #00F5FF; font-size: 1.2rem;'>Elite Performance Intelligence Dashboard</p>", unsafe_allow_html=True)
st.markdown("---")

# ========================================
# SIDEBAR FILTERS
# ========================================

st.sidebar.markdown("<h2>🎯 FILTERS</h2>", unsafe_allow_html=True)

# Get unique teams and maps (filter out NaN values)
ct_teams = set(matches_df['ctTeam'].dropna().unique())
t_teams = set(matches_df['tTeam'].dropna().unique())
all_teams = sorted(list(ct_teams | t_teams))
all_maps = sorted(matches_df['mapName'].dropna().unique())

# Team filter
selected_teams = st.sidebar.multiselect(
    "Select Teams (affects: KPIs, Buy Type chart)",
    options=['All'] + all_teams,
    default=['All']
)

# Map filter
selected_maps = st.sidebar.multiselect(
    "Select Maps (affects: KPIs, Map Win Rate, Buy Type chart)",
    options=['All'] + all_maps,
    default=['All']
)

# ========================================
# APPLY FILTERS TO CREATE FILTERED DATASETS
# ========================================

# Start with base dataset
matches_filtered = matches_df.copy()

# Apply team filter
if 'All' not in selected_teams and len(selected_teams) > 0:
    matches_filtered = matches_filtered[
        matches_filtered['ctTeam'].isin(selected_teams) |
        matches_filtered['tTeam'].isin(selected_teams)
    ]

# Apply map filter
if 'All' not in selected_maps and len(selected_maps) > 0:
    matches_filtered = matches_filtered[matches_filtered['mapName'].isin(selected_maps)]

st.sidebar.markdown("---")
st.sidebar.markdown(f"<p style='color: #00F5FF;'>Filtered Rounds: <b>{len(matches_filtered):,}</b></p>", unsafe_allow_html=True)
st.sidebar.markdown("<p style='color: #9D4EDD; font-size: 0.9rem;'>💡 Player stats always show global data</p>", unsafe_allow_html=True)

# ========================================
# KPI METRICS (Uses filtered data)
# ========================================

st.markdown("<h2>📊 KEY PERFORMANCE INDICATORS</h2>", unsafe_allow_html=True)

col1, col2, col3, col4, col5, col6 = st.columns(6)

# Calculate KPIs from filtered data
total_rounds = len(matches_filtered)
ct_wins = len(matches_filtered[matches_filtered['winningSide'] == 'CT'])
t_wins = len(matches_filtered[matches_filtered['winningSide'] == 'T'])
ct_win_rate = (ct_wins / total_rounds * 100) if total_rounds > 0 else 0
t_win_rate = (t_wins / total_rounds * 100) if total_rounds > 0 else 0
avg_rating = players_df['rating'].mean()
top_player = players_df.nlargest(1, 'rating').iloc[0]
most_played_map = matches_filtered['mapName'].mode()[0] if len(matches_filtered) > 0 and len(matches_filtered['mapName'].mode()) > 0 else "N/A"

with col1:
    st.metric("Total Rounds", f"{total_rounds:,}")

with col2:
    st.metric("CT Win Rate", f"{ct_win_rate:.1f}%")

with col3:
    st.metric("T Win Rate", f"{t_win_rate:.1f}%")

with col4:
    st.metric("Avg Player Rating", f"{avg_rating:.2f}")

with col5:
    st.metric("Top Player", top_player['nickname'])

with col6:
    map_display = most_played_map.replace('de_', '').title() if isinstance(most_played_map, str) and most_played_map != "N/A" else most_played_map
    st.metric("Most Played Map", map_display)

st.markdown("---")

# ========================================
# CHARTS SECTION
# ========================================

st.markdown("<h2>📈 PERFORMANCE ANALYTICS</h2>", unsafe_allow_html=True)

# Chart colors
color_scheme = {
    'primary': '#9D4EDD',
    'secondary': '#00F5FF',
    'tertiary': '#FF6B35',
    'background': '#1a1d29'
}

# ========================================
# CHART 1: Win Rate by Map (GROUPED BAR - CT & T)
# ========================================

st.markdown("<h3>🗺️ Win Rate by Map (CT vs T)</h3>", unsafe_allow_html=True)

# Calculate map statistics from filtered data
map_stats = matches_filtered.groupby('mapName').agg({
    'winningSide': 'count'
}).rename(columns={'winningSide': 'total_rounds'})

map_ct_wins = matches_filtered[matches_filtered['winningSide'] == 'CT'].groupby('mapName').size()
map_t_wins = matches_filtered[matches_filtered['winningSide'] == 'T'].groupby('mapName').size()

map_stats['ct_wins'] = map_ct_wins
map_stats['t_wins'] = map_t_wins
map_stats['ct_win_rate'] = (map_stats['ct_wins'] / map_stats['total_rounds'] * 100).fillna(0)
map_stats['t_win_rate'] = (map_stats['t_wins'] / map_stats['total_rounds'] * 100).fillna(0)
map_stats = map_stats.reset_index()
map_stats['mapName_clean'] = map_stats['mapName'].str.replace('de_', '').str.title()
map_stats = map_stats.sort_values('ct_win_rate', ascending=True)

# Create grouped bar chart
fig1 = go.Figure(data=[
    go.Bar(
        name='CT Win Rate',
        y=map_stats['mapName_clean'],
        x=map_stats['ct_win_rate'],
        orientation='h',
        marker_color=color_scheme['secondary'],
        text=[f"{val:.1f}%" for val in map_stats['ct_win_rate']],
        textposition='auto',
    ),
    go.Bar(
        name='T Win Rate',
        y=map_stats['mapName_clean'],
        x=map_stats['t_win_rate'],
        orientation='h',
        marker_color=color_scheme['tertiary'],
        text=[f"{val:.1f}%" for val in map_stats['t_win_rate']],
        textposition='auto',
    )
])

fig1.update_layout(
    barmode='group',
    plot_bgcolor=color_scheme['background'],
    paper_bgcolor=color_scheme['background'],
    font_color='#FFFFFF',
    title='CT vs T Win Rates by Map',
    title_font_color=color_scheme['primary'],
    xaxis_title='Win Rate (%)',
    yaxis_title='Map',
    height=500,
    legend=dict(
        font=dict(color='#FFFFFF'),
        orientation='h',
        yanchor='bottom',
        y=1.02,
        xanchor='right',
        x=1
    )
)

st.plotly_chart(fig1, use_container_width=True)

# ========================================
# CHART 2: Buy Type Win Rate (Uses filtered data)
# ========================================

st.markdown("<h3>🛒 Buy Type Win Rate Analysis</h3>", unsafe_allow_html=True)

ct_buy_wins = matches_filtered[matches_filtered['winningSide'] == 'CT'].groupby('ctBuyType').size()
t_buy_wins = matches_filtered[matches_filtered['winningSide'] == 'T'].groupby('tBuyType').size()

buy_type_total_ct = matches_filtered.groupby('ctBuyType').size()
buy_type_total_t = matches_filtered.groupby('tBuyType').size()

ct_buy_wr = (ct_buy_wins / buy_type_total_ct * 100).fillna(0)
t_buy_wr = (t_buy_wins / buy_type_total_t * 100).fillna(0)

fig2 = go.Figure(data=[
    go.Bar(name='CT Buy Win Rate', x=ct_buy_wr.index, y=ct_buy_wr.values, marker_color=color_scheme['secondary']),
    go.Bar(name='T Buy Win Rate', x=t_buy_wr.index, y=t_buy_wr.values, marker_color=color_scheme['tertiary'])
])

fig2.update_layout(
    barmode='group',
    plot_bgcolor=color_scheme['background'],
    paper_bgcolor=color_scheme['background'],
    font_color='#FFFFFF',
    title='Win Rate by Buy Type',
    title_font_color=color_scheme['primary'],
    xaxis_title='Buy Type',
    yaxis_title='Win Rate (%)',
    height=400,
    legend=dict(font=dict(color='#FFFFFF'))
)

st.plotly_chart(fig2, use_container_width=True)

st.markdown("---")
st.markdown("<h2>🌟 PLAYER PERFORMANCE (GLOBAL DATA)</h2>", unsafe_allow_html=True)

# ========================================
# CHART 3: Top 10 Players Leaderboard (NO FILTER)
# ========================================

st.markdown("<h3>🏆 TOP 10 PLAYERS BY RATING</h3>", unsafe_allow_html=True)

top_players = players_df.nlargest(10, 'rating')[
    ['nickname', 'real_name', 'country', 'current_team', 'rating',
     'kills_per_round', 'headshot_percentage', 'maps_played']
].copy()

top_players['headshot_percentage'] = (top_players['headshot_percentage'] * 100).round(1)
top_players.columns = ['Nickname', 'Real Name', 'Country', 'Team', 'Rating',
                       'K/R', 'HS%', 'Maps']

# Color code the table
def color_rating(val):
    if val >= 1.25:
        return f'background-color: #00F5FF; color: black; font-weight: bold'
    elif val >= 1.15:
        return f'background-color: #9D4EDD; color: white'
    else:
        return f'background-color: #1a1d29; color: white'

styled_table = top_players.style.applymap(color_rating, subset=['Rating'])

st.dataframe(styled_table, use_container_width=True, height=400)

# ========================================
# CHART 4 & 5: Elite Performance + Opening Duels
# ========================================

col_a, col_b = st.columns(2)

with col_a:
    st.markdown("<h3>⚡ Elite Performance</h3>", unsafe_allow_html=True)

    # Calculate 4K+5K rounds for top 15 players
    top_15_elite = players_df.nlargest(15, 'rating').copy()
    top_15_elite['elite_rounds'] = top_15_elite['4_kill_rounds'] + top_15_elite['5_kill_rounds']

    fig_elite = px.scatter(
        top_15_elite,
        x='rating',
        y='elite_rounds',
        text='nickname',
        title='Player Rating vs Elite Multi-Kill Rounds (4K+5K)',
        labels={'rating': 'Player Rating', 'elite_rounds': '4K + 5K Rounds'},
        color='elite_rounds',
        color_continuous_scale=[color_scheme['tertiary'], color_scheme['primary'], color_scheme['secondary']],
        size='elite_rounds',
        size_max=20
    )

    fig_elite.update_traces(
        textposition='top center',
        textfont=dict(size=9, color='#FFFFFF')
    )

    fig_elite.update_layout(
        plot_bgcolor=color_scheme['background'],
        paper_bgcolor=color_scheme['background'],
        font_color='#FFFFFF',
        title_font_color=color_scheme['primary'],
        height=500,
        showlegend=False
    )

    st.plotly_chart(fig_elite, use_container_width=True)

with col_b:
    st.markdown("<h3>🎯 Opening Duel Success Rate</h3>", unsafe_allow_html=True)

    top_15_opening = players_df.nlargest(15, 'opening_kill_rating')[
        ['nickname', 'opening_kill_ratio', 'total_opening_kills', 'total_opening_deaths']
    ].copy()

    top_15_opening = top_15_opening.sort_values('opening_kill_ratio', ascending=True)

    fig_opening = px.bar(
        top_15_opening,
        y='nickname',
        x='opening_kill_ratio',
        orientation='h',
        title='Opening Kill Ratio (Top 15)',
        labels={'opening_kill_ratio': 'Opening K/D Ratio', 'nickname': 'Player'},
        color='opening_kill_ratio',
        color_continuous_scale=['#FF6B35', '#9D4EDD', '#00F5FF']
    )

    fig_opening.update_layout(
        plot_bgcolor=color_scheme['background'],
        paper_bgcolor=color_scheme['background'],
        font_color='#FFFFFF',
        title_font_color=color_scheme['primary'],
        height=500
    )

    st.plotly_chart(fig_opening, use_container_width=True)

# ========================================
# CHART 6: Weapon Kill Distribution (NO FILTER)
# ========================================

st.markdown("<h3>🔫 Weapon Kill Distribution</h3>", unsafe_allow_html=True)

weapon_totals = {
    'Rifle': players_df['rifle_kills'].sum(),
    'Sniper': players_df['sniper_kills'].sum(),
    'SMG': players_df['smg_kills'].sum(),
    'Pistol': players_df['pistol_kills'].sum(),
    'Grenade': players_df['grenade_kills'].sum(),
    'Other': players_df['other_kills'].sum()
}

fig_weapon = go.Figure(data=[go.Pie(
    labels=list(weapon_totals.keys()),
    values=list(weapon_totals.values()),
    marker=dict(colors=[color_scheme['primary'], color_scheme['secondary'],
                       color_scheme['tertiary'], '#FFD700', '#FF1493', '#00FF00']),
    hole=0.4
)])

fig_weapon.update_layout(
    plot_bgcolor=color_scheme['background'],
    paper_bgcolor=color_scheme['background'],
    font_color='#FFFFFF',
    title='Weapon Type Distribution (All Players)',
    title_font_color=color_scheme['primary'],
    height=500,
    showlegend=True,
    legend=dict(font=dict(color='#FFFFFF'))
)

st.plotly_chart(fig_weapon, use_container_width=True)

st.markdown("---")

# ========================================
# AI INSIGHTS SECTION
# ========================================

st.markdown("<h2>🤖 AI COACHING INSIGHTS</h2>", unsafe_allow_html=True)
st.markdown("<p style='color: #00F5FF;'>Generate strategic insights from your filtered data using AI analysis</p>", unsafe_allow_html=True)

if st.button("🔮 Generate Insights", use_container_width=False):
    try:
        # Prepare data summary for AI
        summary = f"""
        Analyze this CS:GO esports data and provide 5-6 actionable coaching insights:

        Dataset Summary:
        - Total Rounds: {total_rounds:,}
        - CT Win Rate: {ct_win_rate:.1f}%
        - T Win Rate: {t_win_rate:.1f}%
        - Most Played Map: {most_played_map}
        - Top Player: {top_player['nickname']} (Rating: {top_player['rating']:.2f})
        - Average Player Rating: {avg_rating:.2f}

        Map Win Rates:
        {map_stats[['mapName_clean', 'ct_win_rate', 't_win_rate']].to_string(index=False)}

        Top 5 Players by Rating:
        {players_df.nlargest(5, 'rating')[['nickname', 'rating', 'kills_per_round', 'headshot_percentage']].to_string(index=False)}

        Provide specific, actionable insights for teams and coaches.
        """

        # Initialize Google Gemini
        api_key = os.environ.get("GOOGLE_API_KEY")

        if not api_key:
            st.warning("⚠️ Please set your GOOGLE_API_KEY environment variable to use AI insights.")
            st.code("$env:GOOGLE_API_KEY='your-api-key'  # PowerShell", language="powershell")
            st.info("Or edit the .env file in the dashboard_folder with your Google API key")
        else:
            with st.spinner("🧠 Analyzing data with Gemini AI..."):
                # Configure Gemini
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel('gemini-3.1-flash-lite-preview')

                # Generate insights
                response = model.generate_content(summary)
                insights_text = response.text

                # Display insights
                st.markdown("<div class='insight-box'>", unsafe_allow_html=True)
                st.markdown(insights_text)
                st.markdown("</div>", unsafe_allow_html=True)

    except Exception as e:
        st.error(f"Error generating insights: {e}")
        st.info("Make sure you have the GOOGLE_API_KEY set as an environment variable or in the .env file.")

# ========================================
# FOOTER
# ========================================

st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #9D4EDD; padding: 20px;'>
    <p><b>CS:GO Esports Analytics Dashboard</b></p>
    <p style='color: #00F5FF;'>Powered by Streamlit, Plotly & Google Gemini AI</p>
    <p style='font-size: 0.8rem; color: #666;'>Data updated in real-time | Built for competitive CS:GO analysis</p>
</div>
""", unsafe_allow_html=True)
