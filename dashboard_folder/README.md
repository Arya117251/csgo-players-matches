# CS:GO Esports Analytics Dashboard

A professional esports-themed analytics dashboard for CS:GO competitive match analysis.

## Features

### 📊 Interactive Visualizations
1. **Win Rate by Map** - Horizontal bar chart showing CT win rates across all maps
2. **CT vs T Side Comparison** - Direct win rate comparison between sides
3. **Economy Efficiency** - Scatter plot analyzing spending vs round wins
4. **Buy Type Analysis** - Grouped bar chart of win rates by purchase type
5. **Top 10 Players Leaderboard** - Color-coded rating table
6. **Kill Distribution Heatmap** - 0K-5K round distribution for top players
7. **Opening Duel Success** - Bar chart of first kill ratios
8. **Weapon Kill Distribution** - Pie chart of weapon type usage

### 🎯 Key Performance Indicators
- Total Rounds Analyzed
- CT/T Win Rates
- Average Player Rating
- Top Player
- Most Played Map

### 🎨 Esports Theme
- Dark background (#0E1117)
- Neon purple headers (#9D4EDD)
- Cyan accents (#00F5FF)
- Orange highlights (#FF6B35)

### 🤖 AI Insights
- Claude AI-powered coaching insights
- Strategic recommendations based on data
- Actionable team advice

## Installation

1. Install required packages:
```bash
pip install -r requirements.txt
```

2. Set up your Anthropic API key (for AI insights):
```bash
# Windows (PowerShell)
$env:ANTHROPIC_API_KEY="your-api-key-here"

# Windows (CMD)
set ANTHROPIC_API_KEY=your-api-key-here

# Linux/Mac
export ANTHROPIC_API_KEY="your-api-key-here"
```

Get your API key from: https://console.anthropic.com/

## Running the Dashboard

```bash
streamlit run esports_dashboard.py
```

The dashboard will open in your browser at `http://localhost:8501`

## Data Requirements

The dashboard expects cleaned CSV files at:
- `C:\claude\archive\cleaned_data\players_clean.csv`
- `C:\claude\archive\cleaned_data\matches_clean.csv`

## Filters

- **Team Selector**: Filter matches by specific teams
- **Map Selector**: Filter matches by map
- Multi-select with "All" option for both

## Usage Tips

1. Use the sidebar filters to focus on specific teams or maps
2. Hover over charts for detailed tooltips
3. Click "Generate Insights" for AI-powered analysis
4. The leaderboard table is color-coded by rating tier
5. All charts are interactive and can be zoomed/panned

## Technology Stack

- **Streamlit**: Web framework
- **Plotly**: Interactive charts
- **Pandas**: Data processing
- **Anthropic Claude**: AI insights
- **NumPy**: Numerical operations

## Color Scheme

- Primary (Purple): `#9D4EDD`
- Secondary (Cyan): `#00F5FF`
- Tertiary (Orange): `#FF6B35`
- Background: `#0E1117`
- Card Background: `#1a1d29`

---

Built for competitive CS:GO analysis | Powered by Claude AI
