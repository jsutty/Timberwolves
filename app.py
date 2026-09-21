import streamlit as st
import pandas as pd
from datetime import datetime

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Timberwolves Hub | Fixtures, Roster & History",
    page_icon="🐺",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CUSTOM CSS (Authentic Minnesota Timberwolves Theme) ---
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
        padding: 24px;
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

    .season-summary-card {
        background: rgba(12, 35, 64, 0.85);
        border: 1px solid #236192;
        border-radius: 12px;
        padding: 18px;
        margin-bottom: 20px;
    }

    .fixture-card {
        background-color: #0d223f;
        border-radius: 14px;
        border: 1px solid #1a3c68;
        padding: 18px;
        margin-bottom: 16px;
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

    .player-card {
        background-color: #0a1b33;
        border: 1px solid #1a3c68;
        border-radius: 12px;
        padding: 16px;
        text-align: center;
        margin-bottom: 12px;
    }
</style>
""", unsafe_allow_html=True)


# --- DATA: SEASONS RECAP & FIXTURES ---
SEASONS_DATA = {
    "2026/2027 (Upcoming / Current)": {
        "status": "In Progress / Upcoming",
        "record": "0 - 0 (Preseason & Tip-Off)",
        "finish": "Aiming for 6th straight NBA Playoff appearance",
        "playoff_summary": "Season begins October 2026. Preseason action starts early October with key matchups versus Milwaukee, Denver, and Dallas.",
        "def_rtg": "Expected Top 3",
        "seed": "Projected #2–#4 West",
        "games": [
            {
                "status": "UPCOMING",
                "date": "Oct 05, 2026",
                "time": "7:00 PM CST",
                "opponent": "Milwaukee Bucks",
                "opp_logo": "🦌",
                "type": "AWAY",
                "location": "Fiserv Forum, Milwaukee, WI",
                "broadcast": "Bally Sports / NBA League Pass",
                "result": "-",
                "score": "vs",
                "top_performer": "Preseason Matchup 1"
            },
            {
                "status": "UPCOMING",
                "date": "Oct 08, 2026",
                "time": "7:00 PM CST",
                "opponent": "Denver Nuggets",
                "opp_logo": "🏔️",
                "type": "HOME",
                "location": "Target Center, Minneapolis, MN",
                "broadcast": "Bally Sports North",
                "result": "-",
                "score": "vs",
                "top_performer": "Preseason Home Opener"
            },
            {
                "status": "UPCOMING",
                "date": "Oct 21, 2026",
                "time": "6:30 PM CST",
                "opponent": "Miami Heat",
                "opp_logo": "🔥",
                "type": "AWAY",
                "location": "Kaseya Center, Miami, FL",
                "broadcast": "ESPN / FanDuel Sports",
                "result": "-",
                "score": "vs",
                "top_performer": "Regular Season Opening Night"
            },
            {
                "status": "UPCOMING",
                "date": "Oct 25, 2026",
                "time": "6:00 PM CST",
                "opponent": "Toronto Raptors",
                "opp_logo": "🦖",
                "type": "HOME",
                "location": "Target Center, Minneapolis, MN",
                "broadcast": "Bally Sports North",
                "result": "-",
                "score": "vs",
                "top_performer": "Regular Season Home Opener"
            },
            {
                "status": "UPCOMING",
                "date": "Oct 28, 2026",
                "time": "7:00 PM CST",
                "opponent": "Golden State Warriors",
                "opp_logo": "🌉",
                "type": "HOME",
                "location": "Target Center, Minneapolis, MN",
                "broadcast": "TNT / Max",
                "result": "-",
                "score": "vs",
                "top_performer": "Western Conference Primetime"
            },
            {
                "status": "UPCOMING",
                "date": "Oct 31, 2026",
                "time": "7:00 PM CST",
                "opponent": "San Antonio Spurs",
                "opp_logo": "🤠",
                "type": "AWAY",
                "location": "Frost Bank Center, San Antonio, TX",
                "broadcast": "NBA TV",
                "result": "-",
                "score": "vs",
                "top_performer": "2026 Semifinals Rematch"
            }
        ]
    },
    "2025/2026": {
        "status": "Completed",
        "record": "49 - 33 (.598)",
        "finish": "6th in Western Conference (3rd Northwest)",
        "playoff_summary": "🏆 Upset the #3 Denver Nuggets 4–2 in the Western Conference 1st Round. Lost 2–4 to the San Antonio Spurs in the Western Conference Semifinals.",
        "def_rtg": "113.5 (#8 NBA)",
        "seed": "Seed #6 (Western Conference)",
        "games": [
            {
                "status": "PAST",
                "date": "May 15, 2026",
                "time": "Final",
                "opponent": "San Antonio Spurs (Game 6 Semis)",
                "opp_logo": "🤠",
                "type": "HOME",
                "location": "Target Center, Minneapolis, MN",
                "broadcast": "Amazon Prime Video",
                "result": "LOSS",
                "score": "109 - 139",
                "top_performer": "A. Edwards (24 PTS, 7 REB)"
            },
            {
                "status": "PAST",
                "date": "May 10, 2026",
                "time": "Final",
                "opponent": "San Antonio Spurs (Game 4 Semis)",
                "opp_logo": "🤠",
                "type": "HOME",
                "location": "Target Center, Minneapolis, MN",
                "broadcast": "NBC / Peacock",
                "result": "WIN",
                "score": "114 - 109",
                "top_performer": "A. Edwards (36 PTS, 13 REB)"
            },
            {
                "status": "PAST",
                "date": "Apr 30, 2026",
                "time": "Final",
                "opponent": "Denver Nuggets (Game 6 1st Rnd)",
                "opp_logo": "🏔️",
                "type": "HOME",
                "location": "Target Center, Minneapolis, MN",
                "broadcast": "TNT",
                "result": "WIN",
                "score": "110 - 98",
                "top_performer": "J. McDaniels (32 PTS), Gobert (13 REB)"
            },
            {
                "status": "PAST",
                "date": "Apr 25, 2026",
                "time": "Final",
                "opponent": "Denver Nuggets (Game 4 1st Rnd)",
                "opp_logo": "🏔️",
                "type": "HOME",
                "location": "Target Center, Minneapolis, MN",
                "broadcast": "ESPN",
                "result": "WIN",
                "score": "112 - 96",
                "top_performer": "A. Dosunmu (43 PTS, 7 AST)"
            },
            {
                "status": "PAST",
                "date": "Apr 12, 2026",
                "time": "Final",
                "opponent": "New Orleans Pelicans",
                "opp_logo": "⚜️",
                "type": "HOME",
                "location": "Target Center, Minneapolis, MN",
                "broadcast": "FDSN",
                "result": "WIN",
                "score": "132 - 126",
                "top_performer": "Clinched 6th seed playoff berth"
            }
        ]
    },
    "2024/2025": {
        "status": "Completed",
        "record": "49 - 33 (.598)",
        "finish": "Finished 6th in the Western Conference",
        "playoff_summary": "Reached the postseason for the 4th consecutive year after reaching the Western Conference Finals in 2024.",
        "def_rtg": "110.2 (#4 NBA)",
        "seed": "Seed #6 (Western Conference)",
        "games": [
            {
                "status": "PAST",
                "date": "Apr 14, 2025",
                "time": "Final",
                "opponent": "Phoenix Suns",
                "opp_logo": "☀️",
                "type": "HOME",
                "location": "Target Center, Minneapolis, MN",
                "broadcast": "NBA League Pass",
                "result": "LOSS",
                "score": "106 - 125",
                "top_performer": "A. Edwards (22 PTS, 5 REB)"
            },
            {
                "status": "PAST",
                "date": "Apr 12, 2025",
                "time": "Final",
                "opponent": "Atlanta Hawks",
                "opp_logo": "🦅",
                "type": "HOME",
                "location": "Target Center, Minneapolis, MN",
                "broadcast": "Bally Sports North",
                "result": "WIN",
                "score": "109 - 106",
                "top_performer": "R. Gobert (25 PTS, 19 REB)"
            },
            {
                "status": "PAST",
                "date": "Apr 10, 2025",
                "time": "Final",
                "opponent": "Denver Nuggets",
                "opp_logo": "🏔️",
                "type": "AWAY",
                "location": "Ball Arena, Denver, CO",
                "broadcast": "ESPN",
                "result": "LOSS",
                "score": "107 - 116",
                "top_performer": "A. Edwards (25 PTS, 4 AST)"
            }
        ]
    }
}


# --- DATA: CURRENT ROSTER ---
ROSTER_DATA = [
    {"No": "5", "Name": "Anthony Edwards", "Pos": "SG / G", "Height": "6' 4\"", "Weight": "225 lbs", "Experience": "All-NBA / All-Star", "College/Country": "Georgia"},
    {"No": "27", "Name": "Rudy Gobert", "Pos": "C", "Height": "7' 1\"", "Weight": "258 lbs", "Experience": "4x DPOY", "College/Country": "France"},
    {"No": "3", "Name": "Jaden McDaniels", "Pos": "SF / PF", "Height": "6' 9\"", "Weight": "195 lbs", "Experience": "All-Defensive", "College/Country": "Washington"},
    {"No": "0", "Name": "Donte DiVincenzo", "Pos": "SG / G", "Height": "6' 4\"", "Weight": "203 lbs", "Experience": "7 Years", "College/Country": "Villanova"},
    {"No": "1", "Name": "LaMelo Ball", "Pos": "PG / G", "Height": "6' 7\"", "Weight": "180 lbs", "Experience": "All-Star", "College/Country": "SPIRE Academy"},
    {"No": "13", "Name": "Ayo Dosunmu", "Pos": "PG / SG", "Height": "6' 4\"", "Weight": "200 lbs", "Experience": "5 Years", "College/Country": "Illinois"},
    {"No": "24", "Name": "Jonathan Kuminga", "Pos": "PF / SF", "Height": "6' 7\"", "Weight": "225 lbs", "Experience": "5 Years", "College/Country": "Patrick School"},
    {"No": "41", "Name": "Trey Lyles", "Pos": "PF", "Height": "6' 9\"", "Weight": "234 lbs", "Experience": "10 Years", "College/Country": "Kentucky"},
    {"No": "4", "Name": "Terrence Shannon Jr.", "Pos": "SG / SF", "Height": "6' 6\"", "Weight": "215 lbs", "Experience": "2nd Year", "College/Country": "Illinois"},
    {"No": "8", "Name": "Bones Hyland", "Pos": "PG", "Height": "6' 2\"", "Weight": "170 lbs", "Experience": "5 Years", "College/Country": "VCU"},
    {"No": "7", "Name": "Jaylen Clark", "Pos": "SG", "Height": "6' 5\"", "Weight": "205 lbs", "Experience": "2nd Year", "College/Country": "UCLA"},
    {"No": "19", "Name": "Joan Beringer", "Pos": "C / PF", "Height": "6' 11\"", "Weight": "245 lbs", "Experience": "Rookie", "College/Country": "France"},
    {"No": "44", "Name": "Rocco Zikarsky", "Pos": "C", "Height": "7' 3\"", "Weight": "230 lbs", "Experience": "Rookie", "College/Country": "Australia"},
]


# --- DATA: STANDINGS ---
def get_standings():
    west_data = [
        {"Rank": 1, "Team": "Oklahoma City Thunder", "W": 64, "L": 18, "PCT": ".780", "GB": "-", "HOME": "34-8", "AWAY": "30-10", "L10": "8-2", "STRK": "W4"},
        {"Rank": 2, "Team": "San Antonio Spurs", "W": 62, "L": 20, "PCT": ".756", "GB": "2.0", "HOME": "33-8", "AWAY": "29-12", "L10": "8-2", "STRK": "W2"},
        {"Rank": 3, "Team": "Denver Nuggets", "W": 54, "L": 28, "PCT": ".659", "GB": "10.0", "HOME": "28-13", "AWAY": "26-15", "L10": "6-4", "STRK": "L1"},
        {"Rank": 4, "Team": "Los Angeles Lakers", "W": 53, "L": 29, "PCT": ".646", "GB": "11.0", "HOME": "30-11", "AWAY": "23-18", "L10": "7-3", "STRK": "W1"},
        {"Rank": 5, "Team": "Houston Rockets", "W": 52, "L": 30, "PCT": ".634", "GB": "12.0", "HOME": "29-12", "AWAY": "23-18", "L10": "6-4", "STRK": "W2"},
        {"Rank": 6, "Team": "Minnesota Timberwolves", "W": 49, "L": 33, "PCT": ".598", "GB": "15.0", "HOME": "26-15", "AWAY": "23-18", "L10": "6-4", "STRK": "W2"},
        {"Rank": 7, "Team": "Phoenix Suns", "W": 45, "L": 37, "PCT": ".549", "GB": "19.0", "HOME": "24-17", "AWAY": "21-20", "L10": "5-5", "STRK": "L2"},
        {"Rank": 8, "Team": "Portland Trail Blazers", "W": 42, "L": 40, "PCT": ".512", "GB": "22.0", "HOME": "24-17", "AWAY": "18-23", "L10": "5-5", "STRK": "L1"},
        {"Rank": 9, "Team": "Los Angeles Clippers", "W": 42, "L": 40, "PCT": ".512", "GB": "22.0", "HOME": "23-18", "AWAY": "19-22", "L10": "4-6", "STRK": "W1"},
        {"Rank": 10, "Team": "Golden State Warriors", "W": 37, "L": 45, "PCT": ".451", "GB": "27.0", "HOME": "20-21", "AWAY": "17-24", "L10": "4-6", "STRK": "L3"},
    ]
    return pd.DataFrame(west_data)


# --- TOP BANNER ---
st.markdown("""
<div class="twolves-header">
    <div style="display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 15px;">
        <div>
            <div class="hero-title">🐺 Minnesota Timberwolves</div>
            <div class="hero-subtitle">Official Fixtures, Season History & Roster Hub</div>
        </div>
        <div style="text-align: right; background: rgba(0,0,0,0.3); padding: 10px 18px; border-radius: 10px; border-left: 3px solid #78BE20;">
            <div style="font-size: 0.8rem; color: #94A3B8; text-transform: uppercase; font-weight: 700;">Home Arena</div>
            <div style="font-size: 1.35rem; font-weight: 800; color: #FFFFFF;">Target Center <span style="font-size: 0.9rem; color: #78BE20;">(Minneapolis)</span></div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)


# --- SIDEBAR: CONTROLS & SEASON SELECTION ---
with st.sidebar:
    st.image("https://cdn.nba.com/logos/nba/1610612750/global/L/logo.svg", width=100)
    st.markdown("### 🏆 **Season Selector**")
    
    selected_season = st.selectbox(
        "Select Season",
        options=list(SEASONS_DATA.keys()),
        index=0
    )
    
    st.markdown("---")
    st.markdown("### **Schedule Filters**")
    
    view_type = st.radio(
        "Game Status",
        ["All Games", "Upcoming Only", "Past Results Only"],
        index=0
    )
    
    venue_filter = st.selectbox(
        "Venue Location",
        ["All Venues", "Home (Target Center)", "Away"]
    )
    
    search_query = st.text_input("🔍 Search Opponent or Venue", "")
    
    st.markdown("---")
    st.caption("Timberwolves Digital Hub • Updated for 2026/2027 NBA Season")


# --- DATA FILTRATION ---
current_season_data = SEASONS_DATA[selected_season]
fixtures = current_season_data["games"]

if view_type == "Upcoming Only":
    fixtures = [f for f in fixtures if f["status"] == "UPCOMING"]
elif view_type == "Past Results Only":
    fixtures = [f for f in fixtures if f["status"] == "PAST"]

if venue_filter == "Home (Target Center)":
    fixtures = [f for f in fixtures if f["type"] == "HOME"]
elif venue_filter == "Away":
    fixtures = [f for f in fixtures if f["type"] == "AWAY"]

if search_query:
    q = search_query.lower()
    fixtures = [f for f in fixtures if q in f["opponent"].lower() or q in f["location"].lower()]


# --- MAIN NAVIGATION TABS ---
tab_fixtures, tab_playoffs, tab_roster, tab_standings = st.tabs([
    "📅 Fixtures & Results", 
    "🏆 Season Summary & Playoffs",
    "👥 Team Roster", 
    "📊 Western Standings"
])

# 1. TAB: FIXTURES & RESULTS
with tab_fixtures:
    col_m1, col_m2, col_m3 = st.columns(3)
    col_m1.metric("Selected Season", selected_season.split(" ")[0])
    col_m2.metric("Regular Season Record", current_season_data["record"])
    col_m3.metric("Final Seed / Status", current_season_data["seed"])
    
    st.markdown("<br>", unsafe_allow_html=True)
    st.subheader(f"Schedule for {selected_season} ({len(fixtures)} Games Found)")

    if not fixtures:
        st.info("No fixtures found matching your criteria.")
    else:
        for game in fixtures:
            if game["status"] == "PAST":
                badge_html = f'<span class="badge-win">WIN</span>' if game["result"] == "WIN" else f'<span class="badge-loss">LOSS</span>'
            else:
                badge_html = f'<span class="badge-upcoming">UPCOMING</span>'
                
            type_badge = f'<span class="badge-home">HOME</span>' if game["type"] == "HOME" else f'<span class="badge-away">AWAY</span>'
            
            st.markdown(f"""
            <div class="fixture-card">
                <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #1c3c66; padding-bottom: 10px; margin-bottom: 12px;">
                    <div>
                        <span style="font-weight: 700; color: #FFFFFF; font-size: 0.95rem;">{game["date"]}</span>
                        <span style="color: #64748B; margin: 0 8px;">•</span>
                        <span style="color: #94A3B8; font-size: 0.9rem;">{game["time"]}</span>
                    </div>
                    <div>
                        {type_badge} &nbsp; {badge_html}
                    </div>
                </div>
                <div style="display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap;">
                    <div style="display: flex; align-items: center; gap: 14px;">
                        <span style="font-size: 2rem;">🐺</span>
                        <div>
                            <div style="font-weight: 800; font-size: 1.2rem; color: #FFFFFF;">Minnesota Timberwolves</div>
                            <div style="color: #64748B; font-size: 0.85rem;">{game["location"]}</div>
                        </div>
                    </div>
                    <div style="text-align: center; padding: 0 20px;">
                        <div style="font-size: 1.6rem; font-weight: 900; color: {'#78BE20' if game['result'] == 'WIN' else '#FFFFFF'};">
                            {game["score"]}
                        </div>
                        <div style="font-size: 0.75rem; color: #94A3B8; text-transform: uppercase;">{game["broadcast"]}</div>
                    </div>
                    <div style="display: flex; align-items: center; gap: 14px;">
                        <div style="text-align: right;">
                            <div style="font-weight: 800; font-size: 1.2rem; color: #FFFFFF;">{game["opponent"]}</div>
                            <div style="color: #64748B; font-size: 0.85rem;">{game["top_performer"]}</div>
                        </div>
                        <span style="font-size: 2rem;">{game["opp_logo"]}</span>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

# 2. TAB: SEASON SUMMARY & PLAYOFFS
with tab_playoffs:
    st.subheader(f"End-of-Season & Playoff Recap ({selected_season})")
    
    st.markdown(f"""
    <div class="season-summary-card">
        <h3 style="color: #78BE20; margin-top: 0;">Season Highlights & Playoff Run</h3>
        <p style="font-size: 1.1rem; line-height: 1.6; color: #F1F5F9;">{current_season_data["playoff_summary"]}</p>
        <hr style="border: 0; border-top: 1px solid rgba(255,255,255,0.1); margin: 16px 0;">
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 16px;">
            <div>
                <span style="color: #94A3B8; font-size: 0.85rem;">FINAL REGULAR POSITION</span>
                <div style="font-size: 1.2rem; font-weight: bold; color: #FFFFFF;">{current_season_data["finish"]}</div>
            </div>
            <div>
                <span style="color: #94A3B8; font-size: 0.85rem;">OVERALL RECORD</span>
                <div style="font-size: 1.2rem; font-weight: bold; color: #78BE20;">{current_season_data["record"]}</div>
            </div>
            <div>
                <span style="color: #94A3B8; font-size: 0.85rem;">DEFENSIVE RATING</span>
                <div style="font-size: 1.2rem; font-weight: bold; color: #38BDF8;">{current_season_data["def_rtg"]}</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Historical playoff comparison table
    st.markdown("#### Historical Postseason Performance (Past 4 Seasons)")
    history_df = pd.DataFrame([
        {"Season": "2025/2026", "Record": "49 - 33", "West Seed": "#6", "Playoff Result": "Western Conference Semifinals (Lost 2-4 vs Spurs)", "Key Moment": "Upset #3 Nuggets in 6 games"},
        {"Season": "2024/2025", "Record": "49 - 33", "West Seed": "#6", "Playoff Result": "First Round", "Key Moment": "Edwards 28.8 PPG season"},
        {"Season": "2023/2024", "Record": "56 - 26", "West Seed": "#3", "Playoff Result": "Western Conference Finals (Lost 1-4 vs Mavericks)", "Key Moment": "Game 7 20-pt comeback @ Denver"},
        {"Season": "2022/2023", "Record": "42 - 40", "West Seed": "#8", "Playoff Result": "First Round (Lost 1-4 vs Denver)", "Key Moment": "Play-in victory vs OKC"}
    ])
    st.dataframe(history_df, use_container_width=True, hide_index=True)

# 3. TAB: TEAM ROSTER
with tab_roster:
    st.subheader("Minnesota Timberwolves Official Squad Roster")
    st.caption("Active Roster • Head Coach: Chris Finch • President of Basketball Ops: Tim Connelly")
    
    # Filter by position
    pos_filter = st.selectbox("Filter by Position", ["All Positions", "Guard", "Forward", "Center"])
    
    roster_filtered = ROSTER_DATA
    if pos_filter == "Guard":
        roster_filtered = [p for p in ROSTER_DATA if "G" in p["Pos"]]
    elif pos_filter == "Forward":
        roster_filtered = [p for p in ROSTER_DATA if "F" in p["Pos"]]
    elif pos_filter == "Center":
        roster_filtered = [p for p in ROSTER_DATA if "C" in p["Pos"]]
        
    df_roster = pd.DataFrame(roster_filtered)
    
    col_r1, col_r2 = st.columns([2, 1])
    with col_r1:
        st.dataframe(
            df_roster,
            use_container_width=True,
            hide_index=True,
            column_config={
                "No": st.column_config.TextColumn("#", width="small"),
                "Name": st.column_config.TextColumn("Player Name", width="medium"),
                "Pos": st.column_config.TextColumn("Pos"),
                "Height": st.column_config.TextColumn("Height"),
                "Weight": st.column_config.TextColumn("Weight"),
                "Experience": st.column_config.TextColumn("Status / Accolades"),
            }
        )
    with col_r2:
        st.markdown("""
        <div style="background: #0d223f; border: 1px solid #1a3c68; border-radius: 12px; padding: 18px;">
            <h4 style="color: #78BE20; margin-top: 0;">Coaching Staff</h4>
            <p><strong>Head Coach:</strong> Chris Finch</p>
            <p><strong>Lead Assistant:</strong> Micah Nori</p>
            <p><strong>Assistant Coach:</strong> Pablo Prigioni</p>
            <p><strong>Player Development:</strong> Kevin Hanson</p>
            <hr style="border: 0; border-top: 1px solid #1c3c66;">
            <h4 style="color: #78BE20; margin-top: 0;">Cap & Contract Notes</h4>
            <p style="font-size: 0.85rem; color: #94A3B8;">Anthony Edwards under maximum designated rookie extension through 2028-29. Rudy Gobert anchoring defensive frontcourt.</p>
        </div>
        """, unsafe_allow_html=True)

# 4. TAB: STANDINGS
with tab_standings:
    st.subheader("Western Conference Snapshot")
    west_df = get_standings()
    
    def highlight_twolves(row):
        if "Timberwolves" in row["Team"]:
            return ["background-color: rgba(120, 190, 32, 0.25); font-weight: bold; color: #FFFFFF"] * len(row)
        return [""] * len(row)

    styled_west = west_df.style.apply(highlight_twolves, axis=1)
    st.dataframe(styled_west, use_container_width=True, hide_index=True)
    st.caption("Top 6 clinch guaranteed playoff seeds. 7-10 enter the postseason Play-In Tournament.")
