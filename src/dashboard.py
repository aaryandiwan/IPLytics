"""
IPLytics Interactive Dashboard
Run: streamlit run src/dashboard.py
"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ============================================================
# PAGE CONFIG
# ============================================================
st.set_page_config(page_title="IPLytics Dashboard", page_icon="🏏", layout="wide")

st.markdown("""
<style>
    .main > div { padding-top: 1rem; }
    .stMetric { background: linear-gradient(135deg, #1a1a2e, #16213e); padding: 15px; border-radius: 10px; }
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
# SIDEBAR FILTERS
# ============================================================
st.sidebar.image("https://upload.wikimedia.org/wikipedia/en/thumb/8/84/Indian_Premier_League_Official_Logo.svg/200px-Indian_Premier_League_Official_Logo.svg.png", width=150)
st.sidebar.title("🏏 IPLytics Filters")

seasons = sorted(df['season'].unique())
selected_seasons = st.sidebar.slider("Season Range", min_value=int(min(seasons)), max_value=int(max(seasons)),
                                      value=(int(min(seasons)), int(max(seasons))))

teams = sorted(df['batting_team'].unique())
selected_teams = st.sidebar.multiselect("Filter Teams", teams, default=teams)

# Apply filters
filtered = df[(df['season'] >= selected_seasons[0]) & (df['season'] <= selected_seasons[1]) &
              (df['batting_team'].isin(selected_teams))]

# ============================================================
# HEADER
# ============================================================
st.title("🏏 IPLytics: IPL Analytics Dashboard (2008-2025)")
st.markdown("*Powered by Cricsheet.org ball-by-ball data*")

# KPI Cards
col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("📊 Matches", f"{filtered['match_id'].nunique():,}")
col2.metric("🏃 Deliveries", f"{len(filtered):,}")
col3.metric("🏏 Batters", f"{filtered['striker'].nunique()}")
col4.metric("🎳 Bowlers", f"{filtered['bowler'].nunique()}")
col5.metric("📅 Seasons", f"{filtered['season'].nunique()}")

st.divider()

# ============================================================
# TABS
# ============================================================
tab1, tab2, tab3, tab4, tab5 = st.tabs(["🏏 Batting", "🎳 Bowling", "🏆 Teams", "📈 Trends", "⚡ Impact Player"])

# TAB 1: BATTING
with tab1:
    st.subheader("Batting Leaderboard")
    batting = filtered.groupby('striker').agg(
        total_runs=('runs_off_bat', 'sum'), balls_faced=('is_legal', 'sum'),
        fours=('is_four', 'sum'), sixes=('is_six', 'sum'),
        boundaries=('is_boundary', 'sum'), matches=('match_id', 'nunique')
    ).reset_index()
    batting = batting[batting['balls_faced'] >= 200].copy()
    batting['strike_rate'] = (batting['total_runs'] / batting['balls_faced'] * 100).round(2)
    batting['boundary_pct'] = (batting['boundaries'] / batting['balls_faced'] * 100).round(2)
    batting['avg_runs'] = (batting['total_runs'] / batting['matches']).round(2)
    batting = batting.sort_values('total_runs', ascending=False)

    top_n = st.slider("Show Top N Batters", 5, 30, 10, key='bat_slider')
    top = batting.head(top_n).sort_values('total_runs')

    fig = px.bar(top, x='total_runs', y='striker', orientation='h',
                 color='strike_rate', color_continuous_scale='RdYlGn', text='total_runs',
                 labels={'striker': 'Batter', 'total_runs': 'Total Runs', 'strike_rate': 'SR'})
    fig.update_traces(textposition='outside')
    fig.update_layout(height=500, yaxis={'categoryorder': 'total ascending'})
    st.plotly_chart(fig, use_container_width=True)

    st.dataframe(batting.head(30).style.background_gradient(cmap='YlGn', subset=['total_runs', 'strike_rate']),
                 use_container_width=True)

# TAB 2: BOWLING
with tab2:
    st.subheader("Bowling Leaderboard")
    bowling = filtered.groupby('bowler').agg(
        balls_bowled=('is_legal', 'sum'), runs_conceded=('total_runs', 'sum'),
        wickets=('is_wicket', 'sum'), dots=('is_dot', 'sum'),
        matches=('match_id', 'nunique')
    ).reset_index()
    bowling = bowling[bowling['balls_bowled'] >= 200].copy()
    bowling['overs'] = (bowling['balls_bowled'] / 6).round(1)
    bowling['economy'] = (bowling['runs_conceded'] / bowling['overs']).round(2)
    bowling['bowling_sr'] = (bowling['balls_bowled'] / bowling['wickets'].replace(0, np.nan)).round(2)
    bowling['dot_pct'] = (bowling['dots'] / bowling['balls_bowled'] * 100).round(2)
    bowling = bowling.sort_values('wickets', ascending=False)

    top_n_b = st.slider("Show Top N Bowlers", 5, 30, 10, key='bowl_slider')
    top_b = bowling.head(top_n_b).sort_values('wickets')

    fig = px.bar(top_b, x='wickets', y='bowler', orientation='h',
                 color='economy', color_continuous_scale='RdYlGn_r', text='wickets',
                 labels={'bowler': 'Bowler', 'wickets': 'Wickets', 'economy': 'Economy'})
    fig.update_traces(textposition='outside')
    fig.update_layout(height=500)
    st.plotly_chart(fig, use_container_width=True)

    st.dataframe(bowling.head(30).style.background_gradient(cmap='YlGn', subset=['wickets']),
                 use_container_width=True)

# TAB 3: TEAMS
with tab3:
    st.subheader("Franchise Performance")
    
    # NEW ROBUST LOGIC: Calculate winners from full dataset first
    @st.cache_data
    def get_all_match_results(_df):
        inn_totals = _df.groupby(['match_id', 'innings', 'batting_team']).agg(runs=('total_runs', 'sum')).reset_index()
        # Pivot manually to ensure we handle all innings
        m_scores = inn_totals.pivot_table(index='match_id', columns='innings', values='runs', aggfunc='sum').reset_index()
        m_teams = inn_totals.groupby(['match_id', 'innings'])['batting_team'].first().unstack().reset_index()
        
        if 1 in m_scores.columns and 2 in m_scores.columns and 1 in m_teams.columns and 2 in m_teams.columns:
            m_scores = m_scores.rename(columns={1: 'inn1', 2: 'inn2'})
            m_teams = m_teams.rename(columns={1: 't1', 2: 't2'})
            res = m_scores[['match_id', 'inn1', 'inn2']].merge(m_teams[['match_id', 't1', 't2']], on='match_id').dropna()
            res['winner'] = res.apply(lambda r: r['t1'] if r['inn1'] > r['inn2'] else r['t2'] if r['inn2'] > r['inn1'] else 'Tie', axis=1)
            # Add season back for filtering
            s_map = _df.groupby('match_id')['season'].first()
            res['season'] = res['match_id'].map(s_map)
            return res
        return pd.DataFrame()

    all_mr = get_all_match_results(df)
    
    if not all_mr.empty:
        # Filter the results by selected seasons and teams
        filtered_mr = all_mr[(all_mr['season'] >= selected_seasons[0]) & (all_mr['season'] <= selected_seasons[1])]
        filtered_mr = filtered_mr[(filtered_mr['t1'].isin(selected_teams)) | (filtered_mr['t2'].isin(selected_teams))]
        
        all_t = pd.concat([filtered_mr['t1'], filtered_mr['t2']]).unique()
        # Only keep teams that the user actually selected in sidebar
        selected_set = set(selected_teams)
        all_t = [t for t in all_t if t in selected_set]
        
        ts = []
        for t in all_t:
            p = len(filtered_mr[(filtered_mr['t1'] == t) | (filtered_mr['t2'] == t)])
            w = len(filtered_mr[filtered_mr['winner'] == t])
            if p >= 5: # Lowered threshold to 5 for better visibility
                ts.append({'Team': t, 'Played': p, 'Won': w, 'Win%': round(w / p * 100, 2)})
        
        if ts:
            tdf = pd.DataFrame(ts).sort_values('Win%', ascending=False)
            fig = px.bar(tdf, x='Win%', y='Team', orientation='h', color='Win%',
                         color_continuous_scale='RdYlGn', text='Win%')
            fig.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
            fig.update_layout(height=600, yaxis={'categoryorder': 'total ascending'})
            st.plotly_chart(fig, use_container_width=True)
            st.dataframe(tdf.style.background_gradient(cmap='RdYlGn', subset=['Win%']), use_container_width=True)
        else:
            st.warning("No teams found with at least 5 matches in the selected range.")
    else:
        st.error("Error processing match results. Check dataset integrity.")

# TAB 4: TRENDS
with tab4:
    st.subheader("Season Scoring Trends")
    srpo = filtered.groupby('season').agg(tr=('total_runs', 'sum'), lb=('is_legal', 'sum')).reset_index()
    srpo['rpo'] = (srpo['tr'] / (srpo['lb'] / 6)).round(2)
    fig = px.line(srpo, x='season', y='rpo', markers=True, text='rpo',
                  title='Runs Per Over by Season')
    fig.update_traces(textposition='top center', line=dict(width=3, color='#FFD700'))
    fig.update_layout(height=500, xaxis=dict(dtick=1))
    st.plotly_chart(fig, use_container_width=True)

    sixes = filtered.groupby('season')['is_six'].sum().reset_index()
    sixes.columns = ['Season', 'Sixes']
    fig2 = px.bar(sixes, x='Season', y='Sixes', color='Sixes',
                  color_continuous_scale='plasma', text='Sixes', title='Sixes Per Season')
    fig2.update_traces(textposition='outside')
    fig2.update_layout(height=500, xaxis=dict(dtick=1))
    st.plotly_chart(fig2, use_container_width=True)

# TAB 5: IMPACT PLAYER
with tab5:
    st.subheader("⚡ Impact Player Rule Analysis (2023-2025)")
    st.markdown("""
    > The **Impact Player rule** was introduced in IPL 2023, allowing teams to substitute one player mid-match.
    > This section compares key metrics before and after the rule's introduction.
    """)

    inn_total = df.groupby(['match_id', 'innings', 'batting_team']).agg(runs=('total_runs', 'sum')).reset_index()
    smap = df.groupby('match_id')['season'].first()
    fi = inn_total[inn_total['innings'] == 1].copy()
    fi['season'] = fi['match_id'].map(smap)
    fi['era'] = fi['season'].apply(lambda x: 'Post (2023-25)' if x >= 2023 else 'Pre (2008-22)')
    era_avg = fi.groupby('era')['runs'].mean().round(1).reset_index()

    c1, c2 = st.columns(2)
    with c1:
        fig = px.bar(era_avg, x='era', y='runs', color='era',
                     color_discrete_sequence=['#636EFA', '#EF553B'], text='runs',
                     title='Avg 1st Innings Score')
        fig.update_traces(textposition='outside', textfont_size=18)
        fig.update_layout(height=400, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        fig = px.histogram(fi, x='runs', color='era', barmode='overlay', nbins=40, opacity=0.7,
                           title='Score Distribution', color_discrete_sequence=['#636EFA', '#EF553B'])
        fig.add_vline(x=200, line_dash="dash", line_color="yellow")
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)

    be = df.groupby('era').agg(
        bd=('is_boundary', 'sum'), bl=('is_legal', 'sum'),
        sx=('is_six', 'sum'), dt=('is_dot', 'sum')
    ).reset_index()
    be['Boundary%'] = (be['bd'] / be['bl'] * 100).round(2)
    be['Six%'] = (be['sx'] / be['bl'] * 100).round(2)
    be['Dot%'] = (be['dt'] / be['bl'] * 100).round(2)
    st.dataframe(be[['era', 'Boundary%', 'Six%', 'Dot%']].set_index('era'), use_container_width=True)

# FOOTER
st.divider()
st.markdown("*Built by Aaryan Diwan | Data sourced from Cricsheet.org*")
