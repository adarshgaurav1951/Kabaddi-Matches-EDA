import os
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# ---------------------------------------------------------
# Page Configuration & Power BI-Style Dark Theme
# ---------------------------------------------------------
st.set_page_config(
    page_title="Kabaddi Analytics Hub | Power BI Dashboard",
    page_icon="🤼",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Power BI Dashboard Aesthetic
st.markdown("""
<style>
    /* Main Background & Fonts */
    .stApp {
        background-color: #0d1117;
        color: #e6edf3;
        font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, Roboto, sans-serif;
    }
    
    /* KPI Metric Cards (Power BI Card Style) */
    .kpi-container {
        display: flex;
        flex-direction: column;
        justify-content: center;
        background: linear-gradient(135deg, #161b22 0%, #1c2128 100%);
        border: 1px solid #30363d;
        border-radius: 10px;
        padding: 16px 20px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.4);
        margin-bottom: 12px;
        transition: transform 0.2s ease, border-color 0.2s ease;
    }
    .kpi-container:hover {
        transform: translateY(-2px);
        border-color: #58a6ff;
    }
    .kpi-title {
        font-size: 0.85rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.8px;
        color: #8b949e;
        margin-bottom: 6px;
    }
    .kpi-value {
        font-size: 1.85rem;
        font-weight: 700;
        color: #58a6ff;
        line-height: 1.2;
    }
    .kpi-sub {
        font-size: 0.75rem;
        color: #3fb950;
        margin-top: 4px;
        font-weight: 500;
    }
    
    /* Headers & Subheaders */
    h1, h2, h3 {
        color: #f0f6fc;
        font-weight: 600;
    }
    .dashboard-title {
        font-size: 2.1rem;
        font-weight: 800;
        background: linear-gradient(90deg, #ff7b00, #ffb703, #00e5ff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 2px;
    }
    .dashboard-subtitle {
        color: #8b949e;
        font-size: 1.0rem;
        margin-bottom: 20px;
    }
    
    /* Streamlit Tabs Styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        border-bottom: 2px solid #21262d;
    }
    .stTabs [data-baseweb="tab"] {
        height: 48px;
        white-space: pre-wrap;
        border-radius: 6px 6px 0px 0px;
        background-color: #161b22;
        color: #8b949e;
        font-weight: 600;
        border: 1px solid #30363d;
        border-bottom: none;
        padding: 8px 16px;
    }
    .stTabs [aria-selected="true"] {
        background-color: #1f6feb !important;
        color: #ffffff !important;
        border-color: #1f6feb !important;
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# Helper Caching Data Loaders
# ---------------------------------------------------------
@st.cache_data
def load_cleaned_data():
    base_dir = "data/cleaned"
    matches = pd.read_csv(os.path.join(base_dir, "cleaned_matches.csv"))
    teams = pd.read_csv(os.path.join(base_dir, "cleaned_teams.csv"))
    players = pd.read_csv(os.path.join(base_dir, "cleaned_players.csv"))
    matches['date'] = pd.to_datetime(matches['date'], errors='coerce')
    return matches, teams, players

@st.cache_data
def load_events_sample():
    path = "data/cleaned/cleaned_events.csv"
    if os.path.exists(path):
        return pd.read_csv(path, low_memory=False)
    return None

# Load Base Datasets
try:
    df_matches, df_teams, df_players = load_cleaned_data()
    data_loaded = True
except Exception as e:
    data_loaded = False
    df_matches, df_teams, df_players = None, None, None

# ---------------------------------------------------------
# Sidebar Controls & Power BI Slicers
# ---------------------------------------------------------
st.sidebar.markdown("## 🤼 Kabaddi Control Center")

data_mode = st.sidebar.radio(
    "Data Source Mode",
    ["📊 Built-in Dataset (PKL Seasons)", "📂 Upload Custom Kabaddi CSV"],
    index=0
)

uploaded_file = None
if data_mode == "📂 Upload Custom Kabaddi CSV":
    uploaded_file = st.sidebar.file_uploader(
        "Upload ANY Kabaddi CSV (Matches, Teams, Players, Events)",
        type=["csv"]
    )

# ---------------------------------------------------------
# Custom CSV Upload Handling
# ---------------------------------------------------------
if uploaded_file is not None:
    st.markdown('<div class="dashboard-title">⚡ Custom CSV Instant Power BI Analyzer</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="dashboard-subtitle">Analyzing uploaded file: <code>{uploaded_file.name}</code></div>', unsafe_allow_html=True)
    
    try:
        df_custom = pd.read_csv(uploaded_file)
        
        # Detect table nature
        cols = [c.lower() for c in df_custom.columns]
        table_type = "Generic Kabaddi Table"
        if any('raid' in c for c in cols) and any('event' in c for c in cols):
            table_type = "Event-Level Play-by-Play Dataset"
        elif any('player' in c for c in cols) and any('point' in c for c in cols):
            table_type = "Player Box Score Dataset"
        elif any('team' in c for c in cols) and any('score' in c for c in cols):
            table_type = "Team Match Summary Dataset"
        elif any('venue' in c for c in cols) or any('toss' in c for c in cols):
            table_type = "Match Schedule & Metadata"
            
        st.success(f"✅ File loaded successfully! Detected Entity Type: **{table_type}** ({len(df_custom):,} rows × {len(df_custom.columns)} columns)")
        
        # High level KPI cards for custom data
        k1, k2, k3, k4 = st.columns(4)
        with k1:
            st.markdown(f"""
            <div class="kpi-container">
                <div class="kpi-title">Total Records</div>
                <div class="kpi-value">{len(df_custom):,}</div>
                <div class="kpi-sub">Rows in dataset</div>
            </div>""", unsafe_allow_html=True)
        with k2:
            st.markdown(f"""
            <div class="kpi-container">
                <div class="kpi-title">Columns Analyzed</div>
                <div class="kpi-value">{len(df_custom.columns)}</div>
                <div class="kpi-sub">Attributes present</div>
            </div>""", unsafe_allow_html=True)
        with k3:
            numeric_cols = df_custom.select_dtypes(include=[np.number]).columns.tolist()
            st.markdown(f"""
            <div class="kpi-container">
                <div class="kpi-title">Numeric Metrics</div>
                <div class="kpi-value">{len(numeric_cols)}</div>
                <div class="kpi-sub">Quantitative dimensions</div>
            </div>""", unsafe_allow_html=True)
        with k4:
            missing_rate = (df_custom.isnull().sum().sum() / (df_custom.size)) * 100
            st.markdown(f"""
            <div class="kpi-container">
                <div class="kpi-title">Data Completeness</div>
                <div class="kpi-value">{100 - missing_rate:.1f}%</div>
                <div class="kpi-sub">{missing_rate:.1f}% missingness</div>
            </div>""", unsafe_allow_html=True)
            
        st.markdown("---")
        
        # Interactive Custom Chart Builder
        st.subheader("📊 Interactive Visual Slicer & Chart Builder")
        c1, c2, c3 = st.columns(3)
        with c1:
            x_col = st.selectbox("Select X-Axis", df_custom.columns, index=0)
        with c2:
            num_opts = [c for c in numeric_cols if c != x_col]
            y_col = st.selectbox("Select Y-Axis (Metric)", num_opts if num_opts else df_custom.columns, index=0)
        with c3:
            chart_type = st.selectbox("Chart Type", ["Bar Chart", "Scatter Plot", "Histogram / Distribution", "Line Trend", "Box Plot"])
            
        if chart_type == "Bar Chart":
            # Aggregation for cleaner bar charts
            agg_df = df_custom.groupby(x_col)[y_col].mean().reset_index().sort_values(by=y_col, ascending=False).head(20)
            fig = px.bar(agg_df, x=x_col, y=y_col, title=f"Top 20 {x_col} by Mean {y_col}",
                         color=y_col, color_continuous_scale="Viridis", template="plotly_dark")
            st.plotly_chart(fig, use_container_width=True)
        elif chart_type == "Scatter Plot":
            fig = px.scatter(df_custom.head(2000), x=x_col, y=y_col, title=f"{y_col} vs. {x_col}",
                             color=y_col, color_continuous_scale="Plasma", template="plotly_dark",
                             trendline="ols" if len(df_custom) > 10 else None)
            st.plotly_chart(fig, use_container_width=True)
        elif chart_type == "Histogram / Distribution":
            fig = px.histogram(df_custom, x=y_col, nbins=30, title=f"Distribution of {y_col}",
                               color_discrete_sequence=["#00e5ff"], template="plotly_dark")
            st.plotly_chart(fig, use_container_width=True)
        elif chart_type == "Line Trend":
            fig = px.line(df_custom.head(500), x=x_col, y=y_col, title=f"{y_col} along {x_col}",
                          template="plotly_dark", color_discrete_sequence=["#ff7b00"])
            st.plotly_chart(fig, use_container_width=True)
        elif chart_type == "Box Plot":
            fig = px.box(df_custom.head(1000), x=x_col, y=y_col, title=f"Spread of {y_col} by {x_col}",
                         template="plotly_dark", color_discrete_sequence=["#58a6ff"])
            st.plotly_chart(fig, use_container_width=True)
            
        with st.expander("🔍 Preview Raw Cleaned Records & Data Types"):
            st.dataframe(df_custom.head(100), use_container_width=True)
            
    except Exception as ex:
        st.error(f"Error parsing uploaded file: {ex}")

# ---------------------------------------------------------
# Primary Pre-Loaded Power BI Dashboard
# ---------------------------------------------------------
else:
    # Title Section
    st.markdown('<div class="dashboard-title">🤼 Pro Kabaddi League Analytics Hub</div>', unsafe_allow_html=True)
    st.markdown('<div class="dashboard-subtitle">Event-Level Performance Intelligence, Tactical Matchups & Player Profiling</div>', unsafe_allow_html=True)

    # Sidebar Slicers
    st.sidebar.markdown("### 🎯 Global Slicers & Filters")
    
    # 1. Season Slicer
    all_series = ["All Tournaments"] + sorted(list(df_matches['series_name'].dropna().unique()))
    selected_series = st.sidebar.selectbox("Filter by Season / Tournament", all_series)
    
    # Apply series filter
    if selected_series != "All Tournaments":
        filtered_matches = df_matches[df_matches['series_name'] == selected_series]
        match_ids = filtered_matches['match_id'].unique()
        filtered_teams = df_teams[df_teams['match_id'].isin(match_ids)]
        filtered_players = df_players[df_players['match_id'].isin(match_ids)]
    else:
        filtered_matches = df_matches
        filtered_teams = df_teams
        filtered_players = df_players

    # 2. Team Slicer
    all_teams = ["All Franchises"] + sorted(list(filtered_teams['team_name'].dropna().unique()))
    selected_team = st.sidebar.selectbox("Filter by Franchise", all_teams)
    
    if selected_team != "All Franchises":
        filtered_teams = filtered_teams[filtered_teams['team_name'] == selected_team]
        team_match_ids = filtered_teams['match_id'].unique()
        filtered_matches = filtered_matches[filtered_matches['match_id'].isin(team_match_ids)]
        filtered_players = filtered_players[filtered_players['match_id'].isin(team_match_ids)]

    # ---------------------------------------------------------
    # TOP KPI SCORECARD ROW (Power BI Style)
    # ---------------------------------------------------------
    tot_matches = len(filtered_matches)
    tot_points = filtered_teams['score'].sum() if len(filtered_teams) > 0 else 0
    tot_raids = filtered_teams['total_raids'].sum() if len(filtered_teams) > 0 else 1
    tot_succ_raids = filtered_teams['successful_raids'].sum() if len(filtered_teams) > 0 else 0
    raid_succ_pct = (tot_succ_raids / tot_raids * 100) if tot_raids > 0 else 0

    tot_tackles = filtered_teams['total_tackles'].sum() if len(filtered_teams) > 0 else 1
    tot_succ_tackles = filtered_teams['successful_tackles'].sum() if len(filtered_teams) > 0 else 0
    tackle_succ_pct = (tot_succ_tackles / tot_tackles * 100) if tot_tackles > 0 else 0

    tot_all_outs = filtered_teams['all_outs_inflicted'].sum() if len(filtered_teams) > 0 else 0
    tot_super_raids = filtered_teams['super_raids'].sum() if len(filtered_teams) > 0 else 0

    k1, k2, k3, k4, k5, k6 = st.columns(6)
    with k1:
        st.markdown(f"""
        <div class="kpi-container">
            <div class="kpi-title">Matches</div>
            <div class="kpi-value">{tot_matches:,}</div>
            <div class="kpi-sub">Total Contests</div>
        </div>""", unsafe_allow_html=True)
    with k2:
        st.markdown(f"""
        <div class="kpi-container">
            <div class="kpi-title">Total Points</div>
            <div class="kpi-value">{tot_points:,}</div>
            <div class="kpi-sub">{tot_points/(tot_matches*2 if tot_matches else 1):.1f} pts / team</div>
        </div>""", unsafe_allow_html=True)
    with k3:
        st.markdown(f"""
        <div class="kpi-container">
            <div class="kpi-title">Raid Strike Rate</div>
            <div class="kpi-value">{raid_succ_pct:.1f}%</div>
            <div class="kpi-sub">{tot_succ_raids:,} of {tot_raids:,} raids</div>
        </div>""", unsafe_allow_html=True)
    with k4:
        st.markdown(f"""
        <div class="kpi-container">
            <div class="kpi-title">Tackle Success</div>
            <div class="kpi-value">{tackle_succ_pct:.1f}%</div>
            <div class="kpi-sub">{tot_succ_tackles:,} captures</div>
        </div>""", unsafe_allow_html=True)
    with k5:
        st.markdown(f"""
        <div class="kpi-container">
            <div class="kpi-title">All-Outs Inflicted</div>
            <div class="kpi-value">{tot_all_outs:,}</div>
            <div class="kpi-sub">{tot_all_outs/(tot_matches if tot_matches else 1):.2f} / match</div>
        </div>""", unsafe_allow_html=True)
    with k6:
        st.markdown(f"""
        <div class="kpi-container">
            <div class="kpi-title">Super Raids</div>
            <div class="kpi-value">{tot_super_raids:,}</div>
            <div class="kpi-sub">3+ Point Raids</div>
        </div>""", unsafe_allow_html=True)

    # ---------------------------------------------------------
    # Power BI Analytical Tabs
    # ---------------------------------------------------------
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🏆 Team Standings & Attack vs Defense",
        "⚡ Raider Efficiency & Strike Rates",
        "🛡️ Defender Wall & Super Tackles",
        "⏱️ Match Momentum & Close Finishes",
        "📋 Data Explorer & Export"
    ])

    # ---------------------------------------------------------
    # TAB 1: Team Standings & Attack vs Defense Matrix
    # ---------------------------------------------------------
    with tab1:
        st.markdown("### 🏆 Franchise Performance Matrix")
        
        c1, c2 = st.columns([1, 1])
        with c1:
            # Average Points per Match by Team
            team_perf = filtered_teams.groupby('team_name').agg({
                'score': 'mean',
                'raid_points_total': 'mean',
                'tackle_points_total': 'mean',
                'all_outs_inflicted': 'sum',
                'super_raids': 'sum',
                'super_tackles': 'sum',
                'match_id': 'count'
            }).reset_index().rename(columns={'match_id': 'matches_played'})
            
            # Filter teams with at least 5 matches
            team_perf = team_perf[team_perf['matches_played'] >= 5].sort_values(by='score', ascending=True)
            
            fig_teams = px.bar(
                team_perf,
                y='team_name',
                x='score',
                orientation='h',
                title="Average Points Scored Per Match by Franchise",
                color='score',
                color_continuous_scale="Blues",
                template="plotly_dark",
                labels={'score': 'Avg Points', 'team_name': 'Franchise'}
            )
            fig_teams.update_layout(height=450, coloraxis_showscale=False)
            st.plotly_chart(fig_teams, use_container_width=True)
            
        with c2:
            # Attack vs Defense Quadrant Matrix
            fig_scatter = px.scatter(
                team_perf,
                x='raid_points_total',
                y='tackle_points_total',
                text='team_name',
                size='all_outs_inflicted',
                color='score',
                color_continuous_scale="Turbo",
                title="Tactical Matrix: Raid Power vs. Defensive Wall (Avg / Match)",
                labels={
                    'raid_points_total': 'Average Raid Points / Match',
                    'tackle_points_total': 'Average Tackle Points / Match',
                    'all_outs_inflicted': 'All-Outs Inflicted'
                },
                template="plotly_dark"
            )
            fig_scatter.update_traces(textposition='top center')
            fig_scatter.update_layout(height=450)
            st.plotly_chart(fig_scatter, use_container_width=True)

        st.markdown("---")
        # Head-to-Head & Win Margin Factors
        c3, c4 = st.columns(2)
        with c3:
            # Super Raids vs Super Tackles by Franchise
            fig_supers = go.Figure()
            fig_supers.add_trace(go.Bar(
                name='Super Raids',
                x=team_perf['team_name'],
                y=team_perf['super_raids'],
                marker_color='#ff7b00'
            ))
            fig_supers.add_trace(go.Bar(
                name='Super Tackles',
                x=team_perf['team_name'],
                y=team_perf['super_tackles'],
                marker_color='#00e5ff'
            ))
            fig_supers.update_layout(
                barmode='group',
                title="Super Raids vs. Super Tackles Produced",
                template="plotly_dark",
                height=380,
                xaxis_tickangle=-45
            )
            st.plotly_chart(fig_supers, use_container_width=True)
            
        with c4:
            # Toss Decision Impact
            toss_summary = filtered_matches['toss_selection'].value_counts().reset_index()
            toss_summary.columns = ['Selection', 'Count']
            fig_toss = px.pie(
                toss_summary,
                names='Selection',
                values='Count',
                title="Toss Winner Preference (Court vs. Raid)",
                hole=0.45,
                color_discrete_sequence=['#1f6feb', '#ffb703', '#3fb950', '#a371f7'],
                template="plotly_dark"
            )
            fig_toss.update_layout(height=380)
            st.plotly_chart(fig_toss, use_container_width=True)

    # ---------------------------------------------------------
    # TAB 2: Raider Analytics & Strike Rates
    # ---------------------------------------------------------
    with tab2:
        st.markdown("### ⚡ Elite Raider Leaderboards & Efficiency")
        
        # Aggregate player raid statistics
        raider_agg = filtered_players.groupby(['player_id', 'player_name', 'player_category']).agg({
            'player_raid_points_total': 'sum',
            'player_raid_points_touch': 'sum',
            'player_raid_points_raid_bonus': 'sum',
            'player_raids_total': 'sum',
            'player_raids_successful': 'sum',
            'player_raids_Empty': 'sum',
            'player_raids_unsuccessful': 'sum',
            'match_id': 'count'
        }).reset_index().rename(columns={'match_id': 'matches_played'})

        # Filter raiders with significant attempts
        raiders_qualified = raider_agg[raider_agg['player_raids_total'] >= 50].copy()
        raiders_qualified['raid_strike_rate'] = (raiders_qualified['player_raids_successful'] / raiders_qualified['player_raids_total']) * 100
        raiders_qualified['points_per_raid'] = (raiders_qualified['player_raid_points_total'] / raiders_qualified['player_raids_total'])
        
        r1, r2 = st.columns([1, 1])
        with r1:
            top_raiders_volume = raiders_qualified.sort_values(by='player_raid_points_total', ascending=False).head(12)
            fig_raiders = px.bar(
                top_raiders_volume,
                x='player_raid_points_total',
                y='player_name',
                orientation='h',
                title="Top 12 Raiders by Career Raid Points",
                color='points_per_raid',
                color_continuous_scale="YlOrRd",
                template="plotly_dark",
                labels={'player_raid_points_total': 'Raid Points', 'player_name': 'Player'}
            )
            fig_raiders.update_layout(yaxis={'categoryorder': 'total ascending'}, height=440)
            st.plotly_chart(fig_raiders, use_container_width=True)

        with r2:
            fig_eff = px.scatter(
                raiders_qualified.head(60),
                x='raid_strike_rate',
                y='points_per_raid',
                size='player_raid_points_total',
                text='player_name',
                color='player_category',
                title="Efficiency Landscape: Strike Rate % vs. Points Per Raid (PPR)",
                labels={'raid_strike_rate': 'Raid Success Rate (%)', 'points_per_raid': 'Points / Raid'},
                template="plotly_dark"
            )
            fig_eff.update_traces(textposition='top center')
            fig_eff.update_layout(height=440)
            st.plotly_chart(fig_eff, use_container_width=True)

        # Touch vs Bonus Point composition
        st.markdown("#### 🎯 Raid Points Breakdown: Physical Touch vs. Bonus Crossing")
        top_split = top_raiders_volume.sort_values(by='player_raid_points_total', ascending=False)
        fig_split = go.Figure()
        fig_split.add_trace(go.Bar(
            name='Touch Points',
            x=top_split['player_name'],
            y=top_split['player_raid_points_touch'],
            marker_color='#ff7b00'
        ))
        fig_split.add_trace(go.Bar(
            name='Bonus Points',
            x=top_split['player_name'],
            y=top_split['player_raid_points_raid_bonus'],
            marker_color='#00e5ff'
        ))
        fig_split.update_layout(
            barmode='stack',
            title="Touch vs. Bonus Distribution for Top Raiders",
            template="plotly_dark",
            height=380,
            xaxis_tickangle=-30
        )
        st.plotly_chart(fig_split, use_container_width=True)

    # ---------------------------------------------------------
    # TAB 3: Defender Dominance & Super Tackles
    # ---------------------------------------------------------
    with tab3:
        st.markdown("### 🛡️ Defensive Fortresses & Tackle Mastery")
        
        # Aggregate player tackle statistics
        def_agg = filtered_players.groupby(['player_id', 'player_name', 'player_category']).agg({
            'player_tackle_points_total': 'sum',
            'player_tackles_total': 'sum',
            'player_tackles_successful': 'sum',
            'player_tackles_unsuccessful': 'sum',
            'player_green_card': 'sum',
            'player_yellow_card': 'sum',
            'player_red_card': 'sum',
            'match_id': 'count'
        }).reset_index().rename(columns={'match_id': 'matches_played'})

        defenders_qualified = def_agg[def_agg['player_tackles_total'] >= 30].copy()
        defenders_qualified['tackle_success_rate'] = (defenders_qualified['player_tackles_successful'] / defenders_qualified['player_tackles_total']) * 100
        
        d1, d2 = st.columns(2)
        with d1:
            top_defenders = defenders_qualified.sort_values(by='player_tackle_points_total', ascending=False).head(12)
            fig_def = px.bar(
                top_defenders,
                x='player_tackle_points_total',
                y='player_name',
                orientation='h',
                title="Top 12 Defenders by Total Tackle Points",
                color='tackle_success_rate',
                color_continuous_scale="Tealgrn",
                template="plotly_dark",
                labels={'player_tackle_points_total': 'Tackle Points', 'player_name': 'Defender'}
            )
            fig_def.update_layout(yaxis={'categoryorder': 'total ascending'}, height=440)
            st.plotly_chart(fig_def, use_container_width=True)
            
        with d2:
            top_efficiency_def = defenders_qualified.sort_values(by='tackle_success_rate', ascending=False).head(12)
            fig_eff_def = px.bar(
                top_efficiency_def,
                x='tackle_success_rate',
                y='player_name',
                orientation='h',
                title="Top 12 Defenders by Tackle Conversion Rate % (Min 30 Tackles)",
                color='player_tackle_points_total',
                color_continuous_scale="Purples",
                template="plotly_dark",
                labels={'tackle_success_rate': 'Tackle Success Rate (%)', 'player_name': 'Defender'}
            )
            fig_eff_def.update_layout(yaxis={'categoryorder': 'total ascending'}, height=440)
            st.plotly_chart(fig_eff_def, use_container_width=True)

        # Discipline & Cards
        st.markdown("#### 🟨 Disciplinary Cards Conceded (Top Active Defenders)")
        fig_cards = go.Figure()
        fig_cards.add_trace(go.Bar(name='Green Cards (Warnings)', x=top_defenders['player_name'], y=top_defenders['player_green_card'], marker_color='#2ea043'))
        fig_cards.add_trace(go.Bar(name='Yellow Cards (2-Min Suspensions)', x=top_defenders['player_name'], y=top_defenders['player_yellow_card'], marker_color='#d29922'))
        fig_cards.add_trace(go.Bar(name='Red Cards (Expulsions)', x=top_defenders['player_name'], y=top_defenders['player_red_card'], marker_color='#f85149'))
        fig_cards.update_layout(barmode='stack', title="Card Penalties across Top Defenders", template="plotly_dark", height=350)
        st.plotly_chart(fig_cards, use_container_width=True)

    # ---------------------------------------------------------
    # TAB 4: Match Dynamics, Close Finishes & Events
    # ---------------------------------------------------------
    with tab4:
        st.markdown("### ⏱️ Match Pace, Clutch Margins & All-Out Impact")
        
        m1, m2 = st.columns(2)
        with m1:
            # Score Margin Distribution (Close Match Detection)
            # Compute match win margins from teams table
            team_margins = filtered_teams.groupby('match_id')['score'].agg(lambda s: abs(s.iloc[0] - s.iloc[1]) if len(s) == 2 else 0).reset_index()
            team_margins.columns = ['match_id', 'margin']
            team_margins['is_close_match'] = team_margins['margin'] <= 5
            
            close_count = team_margins['is_close_match'].sum()
            close_pct = (close_count / len(team_margins) * 100) if len(team_margins) > 0 else 0
            
            fig_hist = px.histogram(
                team_margins,
                x='margin',
                nbins=25,
                title=f"Victory Margin Distribution ({close_pct:.1f}% Clutches decided by ≤ 5 pts)",
                color='is_close_match',
                color_discrete_map={True: '#ff7b00', False: '#58a6ff'},
                labels={'margin': 'Final Score Margin', 'is_close_match': 'Clutch Match (≤5 pts)'},
                template="plotly_dark"
            )
            fig_hist.update_layout(height=420)
            st.plotly_chart(fig_hist, use_container_width=True)

        with m2:
            # Impact of All-Outs on Winning
            # Compare points scored when inflicting all outs
            fig_allout = px.box(
                filtered_teams,
                x='all_outs_inflicted',
                y='score',
                color='all_outs_inflicted',
                title="Team Score Escalation by All-Outs Inflicted",
                labels={'all_outs_inflicted': 'All-Outs Inflicted in Match', 'score': 'Team Final Score'},
                template="plotly_dark"
            )
            fig_allout.update_layout(height=420, showlegend=False)
            st.plotly_chart(fig_allout, use_container_width=True)

        # Match Timeline Explorer
        st.markdown("#### 🔍 Select a Match to Examine Head-to-Head Stats")
        match_options = filtered_matches[['match_id', 'result', 'date']].dropna().head(50)
        selected_match_id = st.selectbox(
            "Select Match for Deep Dive",
            match_options['match_id'].tolist(),
            format_func=lambda mid: f"Match ID #{mid} - {filtered_matches.loc[filtered_matches['match_id']==mid, 'result'].values[0]}"
        )
        
        match_teams_data = filtered_teams[filtered_teams['match_id'] == selected_match_id]
        if len(match_teams_data) >= 2:
            t1, t2 = match_teams_data.iloc[0], match_teams_data.iloc[1]
            sc1, sc2 = st.columns(2)
            with sc1:
                st.markdown(f"""
                <div class="kpi-container" style="border-left: 5px solid #ff7b00;">
                    <div class="kpi-title">{t1['team_name']}</div>
                    <div class="kpi-value">{t1['score']} PTS</div>
                    <div class="kpi-sub">Raid: {t1['raid_points_total']} | Tackle: {t1['tackle_points_total']} | All-Outs: {t1['all_outs_inflicted']}</div>
                </div>""", unsafe_allow_html=True)
            with sc2:
                st.markdown(f"""
                <div class="kpi-container" style="border-left: 5px solid #00e5ff;">
                    <div class="kpi-title">{t2['team_name']}</div>
                    <div class="kpi-value">{t2['score']} PTS</div>
                    <div class="kpi-sub">Raid: {t2['raid_points_total']} | Tackle: {t2['tackle_points_total']} | All-Outs: {t2['all_outs_inflicted']}</div>
                </div>""", unsafe_allow_html=True)

    # ---------------------------------------------------------
    # TAB 5: Data Explorer & CSV Export
    # ---------------------------------------------------------
    with tab5:
        st.markdown("### 📋 Filtered Data Explorer & Instant CSV Download")
        table_view = st.radio("Choose Table to Inspect", ["Matches Table", "Teams Summary Table", "Players Box Score Table"], horizontal=True)
        
        if table_view == "Matches Table":
            st.dataframe(filtered_matches.head(100), use_container_width=True)
            csv = filtered_matches.to_csv(index=False).encode('utf-8')
            st.download_button("📥 Download Filtered Matches CSV", csv, "filtered_matches.csv", "text/csv")
        elif table_view == "Teams Summary Table":
            st.dataframe(filtered_teams.head(100), use_container_width=True)
            csv = filtered_teams.to_csv(index=False).encode('utf-8')
            st.download_button("📥 Download Filtered Teams CSV", csv, "filtered_teams.csv", "text/csv")
        else:
            st.dataframe(filtered_players.head(100), use_container_width=True)
            csv = filtered_players.to_csv(index=False).encode('utf-8')
            st.download_button("📥 Download Filtered Players CSV", csv, "filtered_players.csv", "text/csv")

st.markdown("---")
st.markdown("<div style='text-align: center; color: #8b949e; font-size: 0.85rem;'>Kabaddi Matches Exploratory Data Analysis Hub | Built with Streamlit & Plotly</div>", unsafe_allow_html=True)
