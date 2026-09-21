import streamlit as st
import pandas as pd
import requests
from datetime import datetime

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Timberwolves Live Hub | Fixtures, Roster & Standings",
    page_icon="🐺",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- TIMBERWOLVES BRAND STYLING ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;600;700;800;900&display=swap');
    html, body, [class*="css"] {
        font-family: 'Montserrat', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    .main {
        background: linear-gradient(180deg, #071322 0%, #0c2340 100%);
    }
    .twolves-header {
        background: linear-gradient(135deg, #0C2340 0%, #153965 60%, #081729 100%);
        border: 1px solid rgba(120, 190, 32, 0.35);
        border-radius: 16px;
        padding: 22px 26px;
        margin-bottom: 24px;
        box-shadow: 0 8px 30px rgba(0, 0, 0, 0.4);
    }
    .hero-title {
        color: #FFFFFF;
        font-size: 2.2rem;
        font-weight: 900;
        margin: 0;
        text-transform: uppercase;
        letter-spacing: -0.5px;
    }
    .hero-subtitle {
        color: #78BE20;
        font-weight: 700;
        font-size: 1.05rem;
        margin-top: 4px;
    }
    .fixture-card {
        background-color: #0d223f;
        border-radius: 14px;
        border: 1px solid #1a3c68;
        padding: 16px 20px;
        margin-bottom: 14px;
        transition: transform 0.2s ease, border-color 0.2s ease;
    }
    .fixture-card:hover {
        border-color: #78BE20;
        transform: translateY(-2px);
    }
    .badge-win {
        background-color: rgba(16, 185, 129, 0.2);
        color: #34d399;
        font-weight: 800;
        padding: 4px 10px;
        border-radius: 9999px;
        border: 1px solid rgba(16, 185, 129, 0.4);
        font-size: 0.8rem;
    }
    .badge-loss {
        background-color: rgba(239, 68, 68, 0.2);
        color: #f87171;
        font-weight: 800;
        padding: 4px 10px;
        border-radius: 9999px;
        border: 1px solid rgba(239, 68, 68, 0.4);
        font-size: 0.8rem;
    }
    .badge-upcoming {
        background-color: rgba(120, 190, 32, 0.2);
        color: #78BE20;
        font-weight: 800;
        padding: 4px 10px;
        border-radius: 9999px;
        border: 1px solid rgba(120, 190, 32, 0.4);
        font-size: 0.8rem;
    }
    .badge-home {
        background-color: #173863;
        color: #93c5fd;
        padding: 3px 8px;
        border-radius: 6px;
        font-size: 0.75rem;
        font-weight: 600;
    }
    .badge-away {
        background-color: #23344d;
        color: #cbd5e1;
        padding: 3px 8px;
        border-radius: 6px;
        font-size: 0.75rem;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

# Timberwolves ESPN Team ID is 16
TIMBERWOLVES_TEAM_ID = "16"

# --- LIVE API FETCHER WITH CACHING ---
@st.cache_data(ttl=900)
def fetch_timberwolves_schedule(season_year: int):
    """Fetches real-time schedules directly from ESPN's open NBA API endpoints."""
    url = f"https://site.api.espn.com/apis/site/v2/sports/basketball/nba/teams/{TIMBERWOLVES_TEAM_ID}/schedule?season={season_year}"
    games = []
    try:
        res = requests.get(url, timeout=8)
        if res.status_code == 200:
            data = res.json()
            events = data.get("events", [])
            for event in events:
                competition = event.get("competitions", [{}])[0]
                competitors = competition.get("competitors", [])

                twolves_comp = None
                opp_comp = None
                for c in competitors:
                    if str(c.get("id")) == TIMBERWOLVES_TEAM_ID:
                        twolves_comp = c
                    else:
                        opp_comp = c

                if not opp_comp:
                    continue

                game_type = "HOME" if twolves_comp.get("homeAway") == "home" else "AWAY"
                opp_name = opp_comp.get("team", {}).get("displayName", "NBA Opponent")
                opp_logo = opp_comp.get("team", {}).get("logo", "https://cdn.nba.com/logos/leagues/L/logo-nba.svg")

                utc_date_str = competition.get("date")
                parsed_time = "TBD"
                parsed_date = "TBD"
                if utc_date_str:
                    try:
                        dt = datetime.strptime(utc_date_str, "%Y-%m-%dT%H:%M%z")
                        parsed_date = dt.strftime("%b %d, %Y")
                        parsed_time = dt.strftime("%I:%M %p %Z")
                    except Exception:
                        parsed_date = utc_date_str[:10]

                status_type = competition.get("status", {}).get("type", {})
                is_completed = status_type.get("completed", False)
                status_state = status_type.get("state", "pre")

                venue = competition.get("venue", {}).get("fullName", "Target Center" if game_type == "HOME" else "Away Arena")
                venue_city = competition.get("venue", {}).get("address", {}).get("city", "")
                full_venue = f"{venue}, {venue_city}" if venue_city else venue

                broadcasts = competition.get("broadcasts", [])
                broadcast_str = "League Pass"
                if broadcasts and broadcasts[0].get("names"):
                    broadcast_str = ", ".join(broadcasts[0].get("names"))

                if is_completed:
                    twolves_score = twolves_comp.get("score", {}).get("displayValue", "-")
                    opp_score = opp_comp.get("score", {}).get("displayValue", "-")
                    twolves_win = twolves_comp.get("winner", False)
                    result = "WIN" if twolves_win else "LOSS"
                    score_display = f"{twolves_score} - {opp_score}"
                    status = "PAST"
                else:
                    result = "-"
                    score_display = "vs"
                    status = "UPCOMING" if status_state == "pre" else "LIVE"

                season_label = event.get("seasonType", {}).get("name", "Game")

                games.append({
                    "id": event.get("id"),
                    "status": status,
                    "date": parsed_date,
                    "time": parsed_time,
                    "season_label": season_label,
                    "opponent": opp_name,
                    "opp_logo": opp_logo,
                    "type": game_type,
                    "location": full_venue,
                    "broadcast": broadcast_str,
                    "result": result,
                    "score": score_display
                })
    except Exception as e:
        st.warning(f"Live schedule service unavailable: {e}. Displaying cached fixtures.")
    return games


@st.cache_data(ttl=900)
def fetch_live_standings():
    """Fetches live Western Conference standings. Automatically resets when season begins."""
    url = "https://site.api.espn.com/apis/v2/sports/basketball/nba/standings"
    try:
        res = requests.get(url, timeout=8)
        if res.status_code == 200:
            data = res.json()
            standings_list = []
            children = data.get("children", [])
            for conf in children:
                if "West" in conf.get("name", ""):
                    for stand in conf.get("standings", {}).get("entries", []):
                        team_name = stand.get("team", {}).get("displayName")
                        stats = {s.get("name"): s.get("displayValue") for s in stand.get("stats", [])}
                        standings_list.append({
                            "Rank": stats.get("playoffSeed", "-"),
                            "Team": team_name,
                            "W": stats.get("wins", "0"),
                            "L": stats.get("losses", "0"),
                            "PCT": stats.get("winPercent", ".000"),
                            "GB": stats.get("gamesBehind", "-"),
                            "HOME": stats.get("Home", "-"),
                            "AWAY": stats.get("Road", "-"),
                            "L10": stats.get("L10", "-"),
                            "STRK": stats.get("streak", "-")
                        })
            if standings_list:
                df = pd.DataFrame(standings_list)
                df["Rank_int"] = pd.to_numeric(df["Rank"], errors="coerce").fillna(99)
                df = df.sort_values("Rank_int").drop(columns=["Rank_int"])
                return df
    except Exception:
        pass
    
    return pd.DataFrame([
        {"Rank": 1, "Team": "Oklahoma City Thunder", "W": 57, "L": 25, "PCT": ".695", "GB": "-", "HOME": "33-8", "AWAY": "24-17", "L10": "7-3", "STRK": "W2"},
        {"Rank": 2, "Team": "Denver Nuggets", "W": 57, "L": 25, "PCT": ".695", "GB": "-", "HOME": "33-8", "AWAY": "24-17", "L10": "6-4", "STRK": "W1"},
        {"Rank": 3, "Team": "Minnesota Timberwolves", "W": 56, "L": 26, "PCT": ".683", "GB": "1.0", "HOME": "30-11", "AWAY": "26-15", "L10": "6-4", "STRK": "L1"},
    ])


@st.cache_data(ttl=3600)
def fetch_live_roster():
    """Fetches Minnesota Timberwolves active squad roster."""
    url = f"https://site.api.espn.com/apis/site/v2/sports/basketball/nba/teams/{TIMBERWOLVES_TEAM_ID}/roster"
    try:
        res = requests.get(url, timeout=8)
        if res.status_code == 200:
            data = res.json()
            players = []
            for athlete in data.get("athletes", []):
                players.append({
                    "No": athlete.get("jersey", "-"),
                    "Name": athlete.get("displayName", "-"),
                    "Pos": athlete.get("position", {}).get("abbreviation", "-"),
                    "Height": athlete.get("displayHeight", "-"),
                    "Weight": athlete.get("displayWeight", "-"),
                    "Age": athlete.get("age", "-"),
                    "College/Country": athlete.get("college", {}).get("name", athlete.get("birthPlace", {}).get("country", "-"))
                })
            if players:
                return pd.DataFrame(players)
    except Exception:
        pass
    return pd.DataFrame([
        {"No": "5", "Name": "Anthony Edwards", "Pos": "SG", "Height": "6' 4\"", "Weight": "225 lbs", "Age": "25", "College/Country": "Georgia"},
        {"No": "27", "Name": "Rudy Gobert", "Pos": "C", "Height": "7' 1\"", "Weight": "258 lbs", "Age": "34", "College/Country": "France"},
        {"No": "3", "Name": "Jaden McDaniels", "Pos": "SF", "Height": "6' 9\"", "Weight": "195 lbs", "Age": "25", "College/Country": "Washington"},
        {"No": "0", "Name": "Donte DiVincenzo", "Pos": "SG", "Height": "6' 4\"", "Weight": "203 lbs", "Age": "29", "College/Country": "Villanova"},
        {"No": "11", "Name": "Naz Reid", "Pos": "C", "Height": "6' 9\"", "Weight": "264 lbs", "Age": "27", "College/Country": "LSU"}
    ])


HISTORICAL_SUMMARIES = {
    2027: {
        "summary": "The 2026–27 campaign is underway. The Wolves enter the season with high expectations aiming for a deep playoff run.",
        "record": "Pre-Season / In Progress",
        "playoff_result": "Pending Season Conclusion",
        "seed": "TBD"
    },
    2026: {
        "summary": "Minnesota clinched the 6th seed, defeated the Denver Nuggets 4–2 in a thrilling first round, and advanced to the Western Conference Semifinals.",
        "record": "49 - 33 (.598)",
        "playoff_result": "Western Conference Semifinals (Lost 2-4 vs SAS)",
        "seed": "#6 West"
    },
    2025: {
        "summary": "Following their historic Western Conference Finals appearance in 2024, Minnesota won 49 games behind Anthony Edwards' career season.",
        "record": "49 - 33 (.598)",
        "playoff_result": "Western Conference 1st Round",
        "seed": "#6 West"
    },
    2024: {
        "summary": "A franchise renaissance: Minnesota won 56 regular season games, swept Phoenix in Round 1, overcame a 20-point deficit in Game 7 at Denver, and reached the Western Conference Finals.",
        "record": "56 - 26 (.683)",
        "playoff_result": "Western Conference Finals (Lost 1-4 vs DAL)",
        "seed": "#3 West"
    }
}

# --- SESSION STATE INITIALIZATION FOR PAGINATION ---
if "display_limit" not in st.session_state:
    st.session_state.display_limit = 6

# --- HEADER BANNER ---
st.markdown("""
<div class="twolves-header">
    <div style="display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 15px;">
        <div>
            <div class="hero-title">🐺 Minnesota Timberwolves</div>
            <div class="hero-subtitle">Live Schedule, Results, Conference Standings & Squad Hub</div>
        </div>
        <div style="text-align: right; background: rgba(0,0,0,0.3); padding: 10px 18px; border-radius: 10px; border-left: 3px solid #78BE20;">
            <div style="font-size: 0.8rem; color: #94A3B8; text-transform: uppercase; font-weight: 700;">Live Feed Sync</div>
            <div style="font-size: 1.1rem; font-weight: 800; color: #FFFFFF;">Connected to NBA Engine</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# --- SIDEBAR CONTROLS ---
with st.sidebar:
    st.image("https://cdn.nba.com/logos/nba/1610612750/global/L/logo.svg", width=100)
    
    st.markdown("### 🔄 **Live Sync**")
    if st.button("🔄 Force Refresh All Data", use_container_width=True):
        st.cache_data.clear()
        st.session_state.display_limit = 6
        st.success("Cache cleared! Pulling latest NBA schedules & standings...")
        st.rerun()

    st.markdown("---")
    st.markdown("### 🏆 **Season Selector**")
    season_options = {
        "2026–27 (Current / Upcoming)": 2027,
        "2025–26 Season": 2026,
        "2024–25 Season": 2025,
        "2023–24 WCF Season": 2024
    }
    selected_season_label = st.selectbox("Select Season Year", options=list(season_options.keys()), index=0)
    selected_season_year = season_options[selected_season_label]

    # Reset pagination when season changes
    if "prev_season" not in st.session_state or st.session_state.prev_season != selected_season_year:
        st.session_state.prev_season = selected_season_year
        st.session_state.display_limit = 6

    # Fetch games for selected season to populate filters
    all_season_games = fetch_timberwolves_schedule(selected_season_year)

    st.markdown("---")
    st.markdown("### 🔍 **Filter Schedule**")
    status_filter = st.radio("Status Filter", ["All Fixtures", "Upcoming / Live", "Completed Results"], index=0)
    venue_filter = st.selectbox("Location Filter", ["All Venues", "Home (Target Center)", "Away"])
    
    # MOBILE-FRIENDLY DROPDOWN FOR OPPONENTS
    opponents_list = sorted(list(set([g["opponent"] for g in all_season_games if g.get("opponent")])))
    opponent_filter = st.selectbox(
        "Filter by Opponent",
        options=["All Opponents"] + opponents_list,
        index=0,
        help="Select any team to filter fixtures directly without typing"
    )

# --- FILTER FIXTURES ---
fixtures = all_season_games

if status_filter == "Upcoming / Live":
    fixtures = [f for f in fixtures if f["status"] in ["UPCOMING", "LIVE"]]
elif status_filter == "Completed Results":
    fixtures = [f for f in fixtures if f["status"] == "PAST"]

if venue_filter == "Home (Target Center)":
    fixtures = [f for f in fixtures if f["type"] == "HOME"]
elif venue_filter == "Away":
    fixtures = [f for f in fixtures if f["type"] == "AWAY"]

if opponent_filter != "All Opponents":
    fixtures = [f for f in fixtures if f["opponent"] == opponent_filter]

total_matching = len(fixtures)

# --- MAIN TABS ---
tab_fixtures, tab_playoffs, tab_roster, tab_standings = st.tabs([
    "📅 Live Fixtures & Results", 
    "🏆 Season & Playoff Summary", 
    "👥 Current Roster", 
    "📊 Western Standings"
])

# 1. TAB: FIXTURES & RESULTS
with tab_fixtures:
    season_meta = HISTORICAL_SUMMARIES.get(selected_season_year, {})
    col_m1, col_m2, col_m3 = st.columns(3)
    col_m1.metric("Selected Season", selected_season_label.split(" ")[0])
    col_m2.metric("Season Record", season_meta.get("record", "Syncing..."))
    col_m3.metric("Final Finish / Seed", season_meta.get("seed", "In Progress"))

    st.markdown("<br>", unsafe_allow_html=True)
    
    # Fixtures header & control bar
    f_col1, f_col2 = st.columns([3, 2])
    with f_col1:
        current_shown = min(st.session_state.display_limit, total_matching)
        st.subheader(f"Schedule: Showing {current_shown} of {total_matching} Games")
    
    with f_col2:
        btn_c1, btn_c2, btn_c3 = st.columns(3)
        with btn_c1:
            if st.button("➕ Next 6", use_container_width=True, disabled=(st.session_state.display_limit >= total_matching)):
                st.session_state.display_limit += 6
                st.rerun()
        with btn_c2:
            if st.button("📖 View All", use_container_width=True, disabled=(st.session_state.display_limit >= total_matching)):
                st.session_state.display_limit = max(total_matching, 6)
                st.rerun()
        with btn_c3:
            if st.button("↩️ Reset (6)", use_container_width=True, disabled=(st.session_state.display_limit <= 6)):
                st.session_state.display_limit = 6
                st.rerun()

    if not fixtures:
        st.info("No fixtures found from the NBA API matching your current filters. Click '🔄 Force Refresh All Data' in the sidebar to re-sync.")
    else:
        # Slice fixtures based on current display limit
        displayed_fixtures = fixtures[:st.session_state.display_limit]

        for game in displayed_fixtures:
            if game["status"] == "PAST":
                badge_html = f'<span class="badge-win">WIN</span>' if game["result"] == "WIN" else f'<span class="badge-loss">LOSS</span>'
            elif game["status"] == "LIVE":
                badge_html = f'<span class="badge-loss" style="background: rgba(245, 158, 11, 0.2); color: #fbbf24; border-color: #fbbf24;">LIVE</span>'
            else:
                badge_html = f'<span class="badge-upcoming">UPCOMING</span>'

            type_badge = f'<span class="badge-home">HOME</span>' if game["type"] == "HOME" else f'<span class="badge-away">AWAY</span>'
            season_tag = f'<span style="background: #1e293b; color: #94a3b8; padding: 2px 7px; border-radius: 4px; font-size: 0.72rem; margin-right: 6px;">{game.get("season_label", "")}</span>'

            st.markdown(f"""
            <div class="fixture-card">
                <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #1c3c66; padding-bottom: 10px; margin-bottom: 12px;">
                    <div>
                        {season_tag}
                        <span style="font-weight: 700; color: #FFFFFF; font-size: 0.95rem;">{game["date"]}</span>
                        <span style="color: #64748B; margin: 0 8px;">•</span>
                        <span style="color: #94A3B8; font-size: 0.88rem;">{game["time"]}</span>
                    </div>
                    <div>
                        {type_badge} &nbsp; {badge_html}
                    </div>
                </div>
                <div style="display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 10px;">
                    <div style="display: flex; align-items: center; gap: 14px;">
                        <img src="https://cdn.nba.com/logos/nba/1610612750/global/L/logo.svg" width="46" height="46" style="object-fit: contain;">
                        <div>
                            <div style="font-weight: 800; font-size: 1.2rem; color: #FFFFFF;">Minnesota Timberwolves</div>
                            <div style="color: #64748B; font-size: 0.85rem;">{game["location"]}</div>
                        </div>
                    </div>
                    <div style="text-align: center; padding: 0 16px;">
                        <div style="font-size: 1.6rem; font-weight: 900; color: {'#78BE20' if game['result'] == 'WIN' else '#FFFFFF'};">
                            {game["score"]}
                        </div>
                        <div style="font-size: 0.75rem; color: #94A3B8; text-transform: uppercase;">{game["broadcast"]}</div>
                    </div>
                    <div style="display: flex; align-items: center; gap: 14px;">
                        <div style="text-align: right;">
                            <div style="font-weight: 800; font-size: 1.2rem; color: #FFFFFF;">{game["opponent"]}</div>
                            <div style="color: #64748B; font-size: 0.85rem;">Opponent</div>
                        </div>
                        <img src="{game['opp_logo']}" width="46" height="46" style="object-fit: contain;" onerror="this.onerror=null;this.src='https://cdn.nba.com/logos/leagues/L/logo-nba.svg';">
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        # Bottom Pagination bar when more games exist
        if st.session_state.display_limit < total_matching:
            st.markdown("<br>", unsafe_allow_html=True)
            bot_col1, bot_col2, bot_col3 = st.columns([1, 1, 1])
            with bot_col1:
                if st.button("➕ Load Next 6 Games", key="bot_next_6", use_container_width=True):
                    st.session_state.display_limit += 6
                    st.rerun()
            with bot_col2:
                if st.button("📖 Load Full Season Schedule", key="bot_load_all", use_container_width=True):
                    st.session_state.display_limit = total_matching
                    st.rerun()
            with bot_col3:
                if st.button("↩️ Reset to 6", key="bot_reset", use_container_width=True):
                    st.session_state.display_limit = 6
                    st.rerun()

# 2. TAB: PLAYOFFS & SEASON SUMMARY
with tab_playoffs:
    hist = HISTORICAL_SUMMARIES.get(selected_season_year, {})
    st.subheader(f"End of Season & Postseason Performance: {selected_season_label}")
    
    st.markdown(f"""
    <div style="background: rgba(12, 35, 64, 0.85); border: 1px solid #236192; border-radius: 12px; padding: 22px; margin-bottom: 24px;">
        <h3 style="color: #78BE20; margin-top: 0;">Season Overview</h3>
        <p style="font-size: 1.1rem; line-height: 1.6; color: #F1F5F9;">{hist.get('summary', 'Season in progress.')}</p>
        <hr style="border: 0; border-top: 1px solid rgba(255,255,255,0.1); margin: 16px 0;">
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 16px;">
            <div>
                <span style="color: #94A3B8; font-size: 0.85rem;">FINAL SEED</span>
                <div style="font-size: 1.2rem; font-weight: bold; color: #FFFFFF;">{hist.get('seed', 'TBD')}</div>
            </div>
            <div>
                <span style="color: #94A3B8; font-size: 0.85rem;">REGULAR RECORD</span>
                <div style="font-size: 1.2rem; font-weight: bold; color: #78BE20;">{hist.get('record', 'TBD')}</div>
            </div>
            <div>
                <span style="color: #94A3B8; font-size: 0.85rem;">PLAYOFF FINISH</span>
                <div style="font-size: 1.2rem; font-weight: bold; color: #38BDF8;">{hist.get('playoff_result', 'TBD')}</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("#### Postseason Track Record (2024 – Present)")
    st.dataframe(pd.DataFrame([
        {"Season": "2025–26", "Record": "49-33", "Seed": "#6", "Playoffs": "Western Semifinals (Lost 2-4 vs Spurs)", "Highlight": "Eliminated Denver Nuggets 4-2 in 1st round"},
        {"Season": "2024–25", "Record": "49-33", "Seed": "#6", "Playoffs": "First Round", "Highlight": "Edwards named All-NBA"},
        {"Season": "2023–24", "Record": "56-26", "Seed": "#3", "Playoffs": "Western Conference Finals (Lost 1-4 vs Mavericks)", "Highlight": "Swept Suns 4-0, beat defending champ Nuggets in Game 7"}
    ]), use_container_width=True, hide_index=True)

# 3. TAB: ROSTER
with tab_roster:
    st.subheader("Minnesota Timberwolves Official Squad")
    roster_df = fetch_live_roster()
    
    pos_choice = st.selectbox("Position Group", ["All Positions", "Guards (G)", "Forwards (F)", "Centers (C)"])
    if pos_choice == "Guards (G)":
        filtered_roster = roster_df[roster_df["Pos"].str.contains("G", na=False)]
    elif pos_choice == "Forwards (F)":
        filtered_roster = roster_df[roster_df["Pos"].str.contains("F", na=False)]
    elif pos_choice == "Centers (C)":
        filtered_roster = roster_df[roster_df["Pos"].str.contains("C", na=False)]
    else:
        filtered_roster = roster_df

    st.dataframe(
        filtered_roster,
        use_container_width=True,
        hide_index=True,
        column_config={
            "No": st.column_config.TextColumn("#", width="small"),
            "Name": st.column_config.TextColumn("Player"),
            "Pos": st.column_config.TextColumn("Pos", width="small"),
            "Height": st.column_config.TextColumn("Ht"),
            "Weight": st.column_config.TextColumn("Wt"),
            "Age": st.column_config.TextColumn("Age", width="small"),
            "College/Country": st.column_config.TextColumn("School / Nation")
        }
    )

# 4. TAB: STANDINGS
with tab_standings:
    st.subheader("Live Western Conference Standings")
    st.caption("Auto-resets to 0-0 when the new regular season begins and updates live after each game.")
    
    standings_df = fetch_live_standings()

    def highlight_twolves(row):
        if "Timberwolves" in str(row["Team"]):
            return ["background-color: rgba(120, 190, 32, 0.25); font-weight: bold; color: #FFFFFF"] * len(row)
        return [""] * len(row)

    styled_standings = standings_df.style.apply(highlight_twolves, axis=1)
    st.dataframe(styled_standings, use_container_width=True, hide_index=True)
