"""
IPLytics Interactive Dashboard
Run: streamlit run src/dashboard.py
"""
import os
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ============================================================
# PAGE CONFIG
# ============================================================
st.set_page_config(
    page_title="IPLytics: IPL Analytics Dashboard",
    page_icon="🏏",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================
# CUSTOM PREMIUM CSS STYLING
# ============================================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    .main > div {
        padding-top: 1rem;
    }
    
    /* Header Card */
    .hero-container {
        background: linear-gradient(135deg, rgba(20, 24, 40, 0.95), rgba(10, 14, 26, 0.95));
        border: 1px solid rgba(255, 215, 0, 0.25);
        border-radius: 16px;
        padding: 24px 30px;
        margin-bottom: 25px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
        display: flex;
        align-items: center;
        justify-content: space-between;
    }
    
    .hero-title {
        font-size: 2.2rem;
        font-weight: 800;
        background: linear-gradient(90deg, #FFD700, #FFA500, #FF6347);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0;
        padding: 0;
    }
    
    .hero-subtitle {
        color: #A0AEC0;
        font-size: 0.95rem;
        margin-top: 6px;
    }
    
    .hero-badges {
        display: flex;
        gap: 8px;
        margin-top: 10px;
        flex-wrap: wrap;
    }
    
    .badge {
        background: rgba(255, 255, 255, 0.08);
        border: 1px solid rgba(255, 255, 255, 0.15);
        border-radius: 20px;
        padding: 4px 12px;
        font-size: 0.78rem;
        font-weight: 600;
        color: #E2E8F0;
    }
    
    .badge-gold {
        background: rgba(255, 215, 0, 0.15);
        border-color: rgba(255, 215, 0, 0.4);
        color: #FFD700;
    }
    
    /* Metric Cards */
    [data-testid="stMetric"] {
        background: linear-gradient(145deg, #131826, #1a2236) !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        padding: 16px 20px !important;
        border-radius: 14px !important;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.2) !important;
        transition: transform 0.2s ease, border-color 0.2s ease;
    }
    
    [data-testid="stMetric"]:hover {
        transform: translateY(-2px);
        border-color: rgba(255, 215, 0, 0.35) !important;
    }
    
    [data-testid="stMetricLabel"] {
        font-size: 0.85rem !important;
        font-weight: 600 !important;
        color: #94A3B8 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.5px !important;
    }
    
    [data-testid="stMetricValue"] {
        font-size: 1.85rem !important;
        font-weight: 800 !important;
        color: #F8FAFC !important;
    }
    
    /* Highlight Award Cards */
    .award-card {
        background: linear-gradient(135deg, rgba(26, 32, 53, 0.9), rgba(15, 20, 35, 0.9));
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        padding: 14px 18px;
        margin-bottom: 15px;
        display: flex;
        align-items: center;
        gap: 14px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }
    
    .award-icon {
        font-size: 1.8rem;
        background: rgba(255, 255, 255, 0.06);
        border-radius: 10px;
        padding: 8px 12px;
    }
    
    .award-title {
        font-size: 0.78rem;
        text-transform: uppercase;
        color: #94A3B8;
        font-weight: 700;
        letter-spacing: 0.5px;
    }
    
    .award-name {
        font-size: 1.15rem;
        font-weight: 800;
        color: #F8FAFC;
    }
    
    .award-stat {
        font-size: 0.9rem;
        font-weight: 700;
        color: #10B981;
    }
    
    /* Tab Styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: rgba(15, 23, 42, 0.6);
        padding: 6px;
        border-radius: 12px;
        border: 1px solid rgba(255, 255, 255, 0.06);
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        padding: 8px 16px;
        font-weight: 600;
        color: #94A3B8;
        border: none;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: rgba(255, 215, 0, 0.15) !important;
        color: #FFD700 !important;
        font-weight: 700 !important;
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background-color: #0b0f19;
        border-right: 1px solid rgba(255, 255, 255, 0.08);
    }
</style>
""", unsafe_allow_html=True)

# ============================================================
# DATA LOADING
# ============================================================
@st.cache_data
def load_data():
    df = pd.read_csv('data/all_deliveries.csv')
    df['season'] = df['season'].astype(str).str[:4].astype(int)
    df = df[df['season'] >= 2008].copy()
    df['total_runs'] = df['runs_off_bat'] + df['extras']
    df['is_boundary'] = df['runs_off_bat'].isin([4, 6]).astype(int)
    df['is_four'] = (df['runs_off_bat'] == 4).astype(int)
    df['is_six'] = (df['runs_off_bat'] == 6).astype(int)
    df['is_dot'] = (df['total_runs'] == 0).astype(int)
    df['is_wicket'] = df['wicket_type'].notna().astype(int)
    df['is_legal'] = (~df['wides'].notna() & ~df['noballs'].notna()).astype(int)
    df['era'] = df['season'].apply(lambda x: 'Post-Impact Player (2023-25)' if x >= 2023 else 'Pre-Impact Player (2008-22)')
    return df

df = load_data()

# ============================================================
# SIDEBAR FILTERS & BRANDING
# ============================================================
logo_path = 'assets/ipl_logo.png' if os.path.exists('assets/ipl_logo.png') else "https://upload.wikimedia.org/wikipedia/en/thumb/8/84/Indian_Premier_League_Official_Logo.svg/500px-Indian_Premier_League_Official_Logo.svg.png"

with st.sidebar:
    st.image(logo_path, width=170)
    st.title("🏏 Filters & Controls")
    
    seasons = sorted(df['season'].unique())
    selected_seasons = st.slider(
        "📅 Season Range",
        min_value=int(min(seasons)),
        max_value=int(max(seasons)),
        value=(int(min(seasons)), int(max(seasons)))
    )
    
    teams = sorted(df['batting_team'].unique())
    selected_teams = st.multiselect(
        "🛡️ Filter Teams",
        teams,
        default=teams
    )
    
    st.markdown("---")
    st.markdown("""
    <div style='font-size: 0.8rem; color: #94A3B8; text-align: center;'>
        <b>IPLytics Platform</b><br>
        Ball-by-ball granularity data<br>
        Updated across all seasons
    </div>
    """, unsafe_allow_html=True)

# Apply filters
filtered = df[(df['season'] >= selected_seasons[0]) & (df['season'] <= selected_seasons[1]) &
              (df['batting_team'].isin(selected_teams))]

# ============================================================
# HERO HEADER BANNER
# ============================================================
st.markdown("""
<div class="hero-container">
    <div>
        <h1 class="hero-title">🏏 IPLytics: IPL Analytics Dashboard</h1>
        <div class="hero-subtitle">Enterprise-grade exploratory cricket analytics, efficiency metrics & tactical insights</div>
        <div class="hero-badges">
            <span class="badge badge-gold">🏆 Official Cricsheet Data</span>
            <span class="badge">⚡ Ball-by-Ball Granularity</span>
            <span class="badge">🔥 Impact Player Era Analysis</span>
            <span class="badge">📊 Plotly Dynamic Graphs</span>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# KPI Metrics Row
col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("🏆 Matches", f"{filtered['match_id'].nunique():,}")
col2.metric("⚡ Deliveries", f"{len(filtered):,}")
col3.metric("🏏 Batters", f"{filtered['striker'].nunique():,}")
col4.metric("🎯 Bowlers", f"{filtered['bowler'].nunique():,}")
col5.metric("📅 Seasons", f"{filtered['season'].nunique()}")

st.write("")

# ============================================================
# TABS
# ============================================================
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🏏 Batting Leaderboard",
    "🎳 Bowling Leaderboard",
    "🏆 Franchise Performance",
    "📈 Scoring Trends",
    "⚡ Impact Player Analysis"
])

# ============================================================
# TAB 1: BATTING
# ============================================================
with tab1:
    st.subheader("🏏 Batting Performance & Leaderboard")
    
    batting = filtered.groupby('striker').agg(
        total_runs=('runs_off_bat', 'sum'),
        balls_faced=('is_legal', 'sum'),
        fours=('is_four', 'sum'),
        sixes=('is_six', 'sum'),
        boundaries=('is_boundary', 'sum'),
        matches=('match_id', 'nunique')
    ).reset_index()
    
    batting = batting[batting['balls_faced'] >= 100].copy()
    batting['strike_rate'] = (batting['total_runs'] / batting['balls_faced'] * 100).round(2)
    batting['boundary_pct'] = (batting['boundaries'] / batting['balls_faced'] * 100).round(2)
    batting['avg_runs'] = (batting['total_runs'] / batting['matches']).round(2)
    batting = batting.sort_values('total_runs', ascending=False)

    if not batting.empty:
        # Highlights Cards
        top_scorer = batting.iloc[0]
        top_six_hitter = batting.sort_values('sixes', ascending=False).iloc[0]
        eligible_sr = batting[batting['balls_faced'] >= 250]
        top_sr = eligible_sr.sort_values('strike_rate', ascending=False).iloc[0] if not eligible_sr.empty else batting.iloc[0]

        h1, h2, h3 = st.columns(3)
        with h1:
            st.markdown(f"""
            <div class="award-card">
                <div class="award-icon">👑</div>
                <div>
                    <div class="award-title">Orange Cap Leader</div>
                    <div class="award-name">{top_scorer['striker']}</div>
                    <div class="award-stat">{top_scorer['total_runs']:,} Runs ({top_scorer['matches']} Matches)</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        with h2:
            st.markdown(f"""
            <div class="award-card">
                <div class="award-icon">🚀</div>
                <div>
                    <div class="award-title">Maximum Sixes King</div>
                    <div class="award-name">{top_six_hitter['striker']}</div>
                    <div class="award-stat">{top_six_hitter['sixes']} Sixes ({top_six_hitter['fours']} Fours)</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        with h3:
            st.markdown(f"""
            <div class="award-card">
                <div class="award-icon">⚡</div>
                <div>
                    <div class="award-title">Strike Rate Monster (250+ balls)</div>
                    <div class="award-name">{top_sr['striker']}</div>
                    <div class="award-stat">{top_sr['strike_rate']} SR ({top_sr['total_runs']} Runs)</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        top_n = st.slider("Select Top N Batters to Display", 5, 30, 10, key='bat_slider')
        top = batting.head(top_n).sort_values('total_runs')

        # DYNAMIC HEIGHT TO PREVENT ANY LABEL SKIPPING OR GLITCHES (e.g. Kohli / Rohit disappearing)
        chart_height = max(480, len(top) * 32 + 100)

        fig = px.bar(
            top,
            x='total_runs',
            y='striker',
            orientation='h',
            color='strike_rate',
            color_continuous_scale='Turbo',
            text='total_runs',
            labels={'striker': 'Batter', 'total_runs': 'Total Runs', 'strike_rate': 'Strike Rate'},
            template='plotly_dark'
        )
        fig.update_traces(textposition='outside', cliponaxis=False)
        fig.update_layout(
            height=chart_height,
            margin=dict(l=10, r=40, t=30, b=30),
            yaxis=dict(
                categoryorder='total ascending',
                tickmode='linear',
                dtick=1,
                automargin=True,
                title=''
            ),
            xaxis=dict(title='Total Runs Scored', showgrid=True, gridcolor='rgba(255,255,255,0.08)'),
            coloraxis_colorbar=dict(title="Strike Rate")
        )
        st.plotly_chart(fig, use_container_width=True)

        st.caption(f"Showing Top {min(top_n, len(batting))} Batters Summary Table")
        st.dataframe(
            batting.head(top_n).style.background_gradient(cmap='YlGn', subset=['total_runs', 'strike_rate']),
            use_container_width=True
        )
    else:
        st.info("No batting data matches the current filters.")

# ============================================================
# TAB 2: BOWLING
# ============================================================
with tab2:
    st.subheader("🎳 Bowling Performance & Leaderboard")
    
    bowling = filtered.groupby('bowler').agg(
        balls_bowled=('is_legal', 'sum'),
        runs_conceded=('total_runs', 'sum'),
        wickets=('is_wicket', 'sum'),
        dots=('is_dot', 'sum'),
        matches=('match_id', 'nunique')
    ).reset_index()
    
    bowling = bowling[bowling['balls_bowled'] >= 100].copy()
    bowling['overs'] = (bowling['balls_bowled'] / 6).round(1)
    bowling['economy'] = (bowling['runs_conceded'] / bowling['overs']).round(2)
    bowling['bowling_sr'] = (bowling['balls_bowled'] / bowling['wickets'].replace(0, np.nan)).round(2)
    bowling['dot_pct'] = (bowling['dots'] / bowling['balls_bowled'] * 100).round(2)
    bowling = bowling.sort_values('wickets', ascending=False)

    if not bowling.empty:
        # Highlights Cards
        top_wicket_taker = bowling.iloc[0]
        top_dot_bowler = bowling.sort_values('dots', ascending=False).iloc[0]
        eligible_econ = bowling[bowling['balls_bowled'] >= 300]
        best_economy = eligible_econ.sort_values('economy', ascending=True).iloc[0] if not eligible_econ.empty else bowling.iloc[0]

        b1, b2, b3 = st.columns(3)
        with b1:
            st.markdown(f"""
            <div class="award-card">
                <div class="award-icon">🟣</div>
                <div>
                    <div class="award-title">Purple Cap Leader</div>
                    <div class="award-name">{top_wicket_taker['bowler']}</div>
                    <div class="award-stat">{top_wicket_taker['wickets']} Wickets ({top_wicket_taker['matches']} Matches)</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        with b2:
            st.markdown(f"""
            <div class="award-card">
                <div class="award-icon">🎯</div>
                <div>
                    <div class="award-title">Dot Ball Master</div>
                    <div class="award-name">{top_dot_bowler['bowler']}</div>
                    <div class="award-stat">{top_dot_bowler['dots']:,} Dot Balls ({top_dot_bowler['dot_pct']}% Dots)</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        with b3:
            st.markdown(f"""
            <div class="award-card">
                <div class="award-icon">🛡️</div>
                <div>
                    <div class="award-title">Most Miserly (300+ balls)</div>
                    <div class="award-name">{best_economy['bowler']}</div>
                    <div class="award-stat">{best_economy['economy']} Econ ({best_economy['wickets']} Wickets)</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        top_n_b = st.slider("Select Top N Bowlers to Display", 5, 30, 10, key='bowl_slider')
        top_b = bowling.head(top_n_b).sort_values('wickets')

        # DYNAMIC HEIGHT TO PREVENT SKIPPING TICKS
        chart_height_b = max(480, len(top_b) * 32 + 100)

        fig = px.bar(
            top_b,
            x='wickets',
            y='bowler',
            orientation='h',
            color='economy',
            color_continuous_scale='RdYlGn_r',
            text='wickets',
            labels={'bowler': 'Bowler', 'wickets': 'Wickets', 'economy': 'Economy Rate'},
            template='plotly_dark'
        )
        fig.update_traces(textposition='outside', cliponaxis=False)
        fig.update_layout(
            height=chart_height_b,
            margin=dict(l=10, r=40, t=30, b=30),
            yaxis=dict(
                categoryorder='total ascending',
                tickmode='linear',
                dtick=1,
                automargin=True,
                title=''
            ),
            xaxis=dict(title='Wickets Taken', showgrid=True, gridcolor='rgba(255,255,255,0.08)'),
            coloraxis_colorbar=dict(title="Economy")
        )
        st.plotly_chart(fig, use_container_width=True)

        st.caption(f"Showing Top {min(top_n_b, len(bowling))} Bowlers Summary Table")
        st.dataframe(
            bowling.head(top_n_b).style.background_gradient(cmap='YlGn', subset=['wickets']),
            use_container_width=True
        )
    else:
        st.info("No bowling data matches the current filters.")

# ============================================================
# TAB 3: TEAMS
# ============================================================
with tab3:
    st.subheader("🏆 Franchise Performance & Win Rates")
    
    TEAM_COLORS = {
        'Chennai Super Kings': '#F9CD05',
        'Mumbai Indians': '#004BA0',
        'Royal Challengers Bangalore': '#EC1C24',
        'Royal Challengers Bengaluru': '#C8102E',
        'Kolkata Knight Riders': '#3A225D',
        'Sunrisers Hyderabad': '#F74400',
        'Delhi Capitals': '#0078BC',
        'Delhi Daredevils': '#17479E',
        'Rajasthan Royals': '#EA1A85',
        'Punjab Kings': '#ED1B24',
        'Kings XI Punjab': '#DD1F2D',
        'Gujarat Titans': '#1B2133',
        'Lucknow Super Giants': '#0057E7',
        'Deccan Chargers': '#4C7A9E',
        'Gujarat Lions': '#E04F16',
        'Rising Pune Supergiant': '#D11D9B',
        'Rising Pune Supergiants': '#D11D9B',
        'Pune Warriors': '#2F9BE3',
        'Kochi Tuskers Kerala': '#6C2D58'
    }
    
    @st.cache_data
    def get_all_match_results(_df):
        inn_totals = _df.groupby(['match_id', 'innings', 'batting_team']).agg(runs=('total_runs', 'sum')).reset_index()
        m_scores = inn_totals.pivot_table(index='match_id', columns='innings', values='runs', aggfunc='sum').reset_index()
        m_teams = inn_totals.groupby(['match_id', 'innings'])['batting_team'].first().unstack().reset_index()
        
        if 1 in m_scores.columns and 2 in m_scores.columns and 1 in m_teams.columns and 2 in m_teams.columns:
            m_scores = m_scores.rename(columns={1: 'inn1', 2: 'inn2'})
            m_teams = m_teams.rename(columns={1: 't1', 2: 't2'})
            res = m_scores[['match_id', 'inn1', 'inn2']].merge(m_teams[['match_id', 't1', 't2']], on='match_id').dropna()
            res['winner'] = res.apply(lambda r: r['t1'] if r['inn1'] > r['inn2'] else r['t2'] if r['inn2'] > r['inn1'] else 'Tie', axis=1)
            s_map = _df.groupby('match_id')['season'].first()
            res['season'] = res['match_id'].map(s_map)
            return res
        return pd.DataFrame()

    all_mr = get_all_match_results(df)
    
    if not all_mr.empty:
        filtered_mr = all_mr[(all_mr['season'] >= selected_seasons[0]) & (all_mr['season'] <= selected_seasons[1])]
        filtered_mr = filtered_mr[(filtered_mr['t1'].isin(selected_teams)) | (filtered_mr['t2'].isin(selected_teams))]
        
        all_t = pd.concat([filtered_mr['t1'], filtered_mr['t2']]).unique()
        selected_set = set(selected_teams)
        all_t = [t for t in all_t if t in selected_set]
        
        ts = []
        for t in all_t:
            p = len(filtered_mr[(filtered_mr['t1'] == t) | (filtered_mr['t2'] == t)])
            w = len(filtered_mr[filtered_mr['winner'] == t])
            if p >= 5:
                ts.append({'Team': t, 'Played': p, 'Won': w, 'Win%': round(w / p * 100, 2)})
        
        if ts:
            tdf = pd.DataFrame(ts).sort_values('Win%', ascending=False)
            
            # Map official team colors
            team_color_list = [TEAM_COLORS.get(tm, '#636EFA') for tm in tdf['Team']]
            
            fig = px.bar(
                tdf,
                x='Win%',
                y='Team',
                orientation='h',
                color='Team',
                color_discrete_map=TEAM_COLORS,
                text='Win%',
                template='plotly_dark'
            )
            fig.update_traces(texttemplate='%{text:.1f}%', textposition='outside', cliponaxis=False)
            fig.update_layout(
                height=max(480, len(tdf) * 32 + 100),
                showlegend=False,
                margin=dict(l=10, r=40, t=30, b=30),
                yaxis=dict(categoryorder='total ascending', tickmode='linear', dtick=1, automargin=True, title=''),
                xaxis=dict(title='Match Win Percentage (%)', showgrid=True, gridcolor='rgba(255,255,255,0.08)')
            )
            st.plotly_chart(fig, use_container_width=True)
            st.dataframe(tdf.style.background_gradient(cmap='RdYlGn', subset=['Win%']), use_container_width=True)
        else:
            st.warning("No teams found with at least 5 matches in the selected range.")
    else:
        st.error("Error processing match results. Check dataset integrity.")

# ============================================================
# TAB 4: TRENDS
# ============================================================
with tab4:
    st.subheader("📈 Tournament Scoring Dynamics Across Seasons")
    
    srpo = filtered.groupby('season').agg(tr=('total_runs', 'sum'), lb=('is_legal', 'sum')).reset_index()
    srpo['rpo'] = (srpo['tr'] / (srpo['lb'] / 6)).round(2)
    
    fig = px.line(
        srpo,
        x='season',
        y='rpo',
        markers=True,
        text='rpo',
        title='Average Runs Per Over (RPO) by Season',
        template='plotly_dark'
    )
    fig.update_traces(textposition='top center', line=dict(width=3, color='#FFD700'), marker=dict(size=8, color='#FFA500'))
    fig.update_layout(height=480, xaxis=dict(dtick=1, title='Season'), yaxis=dict(title='Runs Per Over'))
    st.plotly_chart(fig, use_container_width=True)

    sixes = filtered.groupby('season')['is_six'].sum().reset_index()
    sixes.columns = ['Season', 'Sixes']
    fig2 = px.bar(
        sixes,
        x='Season',
        y='Sixes',
        color='Sixes',
        color_continuous_scale='Plasma',
        text='Sixes',
        title='Total Sixes Hit Per Season',
        template='plotly_dark'
    )
    fig2.update_traces(textposition='outside', cliponaxis=False)
    fig2.update_layout(height=480, xaxis=dict(dtick=1, title='Season'), yaxis=dict(title='Total Sixes'))
    st.plotly_chart(fig2, use_container_width=True)

# ============================================================
# TAB 5: IMPACT PLAYER
# ============================================================
with tab5:
    st.subheader("⚡ Impact Player Rule Analysis (2023-Present)")
    st.markdown("""
    > The **Impact Player rule** was introduced in IPL 2023, allowing teams to substitute one active player mid-match.
    > This revolutionary rule provided deep batting security, transforming match strategies and scoring benchmarks.
    """)

    inn_total = df.groupby(['match_id', 'innings', 'batting_team']).agg(runs=('total_runs', 'sum')).reset_index()
    smap = df.groupby('match_id')['season'].first()
    fi = inn_total[inn_total['innings'] == 1].copy()
    fi['season'] = fi['match_id'].map(smap)
    fi['era'] = fi['season'].apply(lambda x: 'Post-Impact (2023+)' if x >= 2023 else 'Pre-Impact (2008-22)')
    era_avg = fi.groupby('era')['runs'].mean().round(1).reset_index()

    c1, c2 = st.columns(2)
    with c1:
        fig = px.bar(
            era_avg,
            x='era',
            y='runs',
            color='era',
            color_discrete_sequence=['#636EFA', '#FF4B4B'],
            text='runs',
            title='Avg 1st Innings Score: Pre vs Post Impact Era',
            template='plotly_dark'
        )
        fig.update_traces(textposition='outside', textfont_size=18, cliponaxis=False)
        fig.update_layout(height=420, showlegend=False, yaxis=dict(title='Average Runs'))
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        fig = px.histogram(
            fi,
            x='runs',
            color='era',
            barmode='overlay',
            nbins=40,
            opacity=0.75,
            title='1st Innings Score Distribution & 200+ Frequency',
            color_discrete_sequence=['#636EFA', '#FF4B4B'],
            template='plotly_dark'
        )
        fig.add_vline(x=200, line_dash="dash", line_color="#FFD700", annotation_text="200+ Run Mark", annotation_position="top right")
        fig.update_layout(height=420, xaxis=dict(title='Runs'), yaxis=dict(title='Match Count'))
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("#### 📊 Boundary & Dot Ball Frequency Shift")
    be = df.groupby('era').agg(
        bd=('is_boundary', 'sum'),
        bl=('is_legal', 'sum'),
        sx=('is_six', 'sum'),
        dt=('is_dot', 'sum')
    ).reset_index()
    be['Boundary%'] = (be['bd'] / be['bl'] * 100).round(2)
    be['Six%'] = (be['sx'] / be['bl'] * 100).round(2)
    be['Dot%'] = (be['dt'] / be['bl'] * 100).round(2)
    st.dataframe(be[['era', 'Boundary%', 'Six%', 'Dot%']].set_index('era'), use_container_width=True)

# ============================================================
# FOOTER
# ============================================================
st.divider()
st.markdown("""
<div style='text-align: center; color: #64748B; font-size: 0.85rem; padding: 10px 0;'>
    🏏 <b>IPLytics Sports Analytics Platform</b> | Built by <b>Aaryan Diwan</b> | Granular data sourced from <b>Cricsheet.org</b>
</div>
""", unsafe_allow_html=True)
