import streamlit as st
import pandas as pd
import json
import time
import base64
from github import Github
from datetime import datetime, timedelta  # <--- CHANGED: Added timedelta
import os

# --- CONFIGURATION ---
POINTS = {
    "GOAL": 6, 
    "ASSIST": 3, 
    "STARTING": 2, 
    "SAVE": 3, 
    "MOM": 10, 
    "YELLOW": -2, 
    "RED": -5,
    "PENALTY_SAVE": 4,
    "PENALTY_MISS": -2,
    "OWN_GOAL": -2,
    "CLEAN_SHEET": 2
}

STAT_KEYS = [
    "starting", "goals", "assists", "saves", "mom", "yellow", "red", 
    "pen_save", "pen_miss", "own_goal", "clean_sheet"
]

MARKET_DEADLINE = datetime(2026, 2, 16, 17, 30, 0) 
ADMIN_USER = "ADMIN"
ADMIN_PASS = "s*CnGWRI"

# --- FULL PLAYER DATABASE ---
PLAYERS_DB = [
    { "name": "Amal", "price": 300, "pos": ["Defender", "Midfielder", "Forward"] }, 
    { "name": "Aromal", "price": 300, "pos": ["Defender", "Midfielder", "Forward"] },
    { "name": "Jerin", "price": 300, "pos": ["Defender", "Midfielder", "Forward"] }, 
    { "name": "Kiran", "price": 300, "pos": ["Defender", "Midfielder", "Forward"] },
    { "name": "Deepak", "price": 300, "pos": ["Defender", "Midfielder", "Forward"] },
    { "name": "Athil", "price": 300, "pos": ["Defender", "Midfielder", "Forward"] },
    { "name": "Jyothish", "price": 300, "pos": ["Defender", "Midfielder", "Forward"] }, 
    { "name": "Hari", "price": 300, "pos": ["Defender", "Midfielder", "Forward"] },
    { "name": "Aryan Ahalawat", "price": 300, "pos": ["Defender", "Midfielder", "Forward"] },
    { "name": "Francis Babu", "price": 300, "pos": ["Defender", "Midfielder"] },
    { "name": "Kushal Aradhya H V", "price": 300, "pos": ["Midfielder", "Forward"] },
    { "name": "Mecwin Levy TS", "price": 300, "pos": ["Defender", "Midfielder"] },
    { "name": "Nishkalan", "price": 300, "pos": ["Goalkeeper", "Defender", "Midfielder", "Forward"] },
    { "name": "Venkatakrishnan", "price": 300, "pos": ["Midfielder", "Forward"] },
    { "name": "Vishnu Ashok Kumar", "price": 300, "pos": ["Defender"] },
    { "name": "Yash Rana", "price": 300, "pos": ["Goalkeeper"] },
    { "name": "Navaroj", "price": 200, "pos": ["Goalkeeper"] },
    { "name": "Madhav", "price": 200, "pos": ["Goalkeeper"] },
    { "name": "James T Kurian", "price": 200, "pos": ["Defender"] },
    { "name": "Kaar Mugilan KA", "price": 200, "pos": ["Defender", "Midfielder", "Forward"] },
    { "name": "Prajwal Shreshta Grandhi", "price": 200, "pos": ["Midfielder", "Forward"] },
    { "name": "Snehith", "price": 200, "pos": ["Defender", "Midfielder", "Forward"] },
    { "name": "Aditya Kaundilya", "price": 200, "pos": ["Goalkeeper"] },
    { "name": "Liton Narjinari", "price": 200, "pos": ["Defender"] },
    { "name": "Sreyas S P", "price": 200, "pos": ["Defender", "Midfielder", "Forward"] },
    { "name": "Shivanand RP", "price": 200, "pos": ["Defender", "Forward"] },
    { "name": "Dolla Bhargav", "price": 200, "pos": ["Midfielder", "Forward"] },
    { "name": "Sreejith", "price": 200, "pos": ["Forward"] },
    { "name": "Abhay Prajapati", "price": 200, "pos": ["Defender"] },
    { "name": "Nilakamal", "price": 200, "pos": ["Forward"] },
    { "name": "Jeyaram", "price": 200, "pos": ["Defender", "Midfielder"] },
    { "name": "Abhijith", "price": 100, "pos": ["Defender", "Midfielder"] },
    { "name": "Roshan Kumar Bishoyi", "price": 100, "pos": ["Defender"] },
    { "name": "Pramodh", "price": 100, "pos": ["Defender", "Forward"] },
    { "name": "Akash Namasudra", "price": 100, "pos": ["Forward"] },
    { "name": "Rudraa Bhuvad", "price": 100, "pos": ["Defender", "Midfielder"] },
    { "name": "Aijaz", "price": 100, "pos": ["Defender", "Midfielder", "Forward"] },
    { "name": "Mainak", "price": 100, "pos": ["Forward"] },
    { "name": "Ruthish PS", "price": 100, "pos": ["Defender"] },
    { "name": "Khavin. J", "price": 100, "pos": ["Midfielder", "Forward"] },
    { "name": "Hariom Meena", "price": 100, "pos": ["Defender", "Forward"] },
    { "name": "Abhinav K", "price": 100, "pos": ["Midfielder"] },
    { "name": "Virendra Chaneja", "price": 100, "pos": ["Goalkeeper"] },
    { "name": "Abinav I V", "price": 100, "pos": ["Midfielder", "Forward"] },
    { "name": "Sreehari Vinod", "price": 50, "pos": ["Goalkeeper", "Defender"] },
    { "name": "Dishant Jain", "price": 50, "pos": ["Defender", "Midfielder"] },
    { "name": "Pushkal", "price": 50, "pos": ["Goalkeeper", "Defender"] },
    { "name": "Vishnu", "price": 50, "pos": ["Midfielder"] },
    { "name": "Aryan Singh", "price": 50, "pos": ["Defender", "Midfielder"] },
    { "name": "Ramkishore", "price": 50, "pos": ["Goalkeeper", "Midfielder"] },
    { "name": "Atul", "price": 50, "pos": ["Midfielder", "Forward"] },
    { "name": "Yash", "price": 50, "pos": ["Midfielder"] },
    { "name": "Abhay Sharma", "price": 50, "pos": ["Goalkeeper"] },
    { "name": "Sanjay Kumar S", "price": 50, "pos": ["Defender", "Midfielder"] },
    { "name": "Piyush Kumar Meena", "price": 50, "pos": ["Midfielder"] },
    { "name": "Souren Ghosh", "price": 50, "pos": ["Forward"] },
    { "name": "Vamsi", "price": 50, "pos": ["Defender"] },
    { "name": "Akash B", "price": 50, "pos": ["Midfielder"] },
    { "name": "Mohammed Owais P H", "price": 50, "pos": ["Midfielder", "Forward"] },
    { "name": "Vaibhav Rikhari", "price": 50, "pos": ["Goalkeeper", "Defender", "Midfielder"] },
    { "name": "Prakhar", "price": 50, "pos": ["Defender", "Midfielder"] }
]

# --- UTILS ---
def get_player_details(name):
    if not name: return None
    return next((x for x in PLAYERS_DB if x["name"] == name), None)

def clean_squad_list(player_list):
    if not player_list: return []
    return [p for p in player_list if get_player_details(p)]

def load_image_base64(repo, filename):
    """
    Fetches an image and converts it to base64.
    PRIORITY 1: Check Local File (Best for reliability if file exists).
    PRIORITY 2: Check GitHub Repo (Fallback).
    """
    # 1. Try Local File
    if os.path.exists(filename):
        try:
            with open(filename, "rb") as f:
                return base64.b64encode(f.read()).decode()
        except Exception:
            pass

    # 2. Try GitHub Repo
    try:
        contents = repo.get_contents(filename)
        return base64.b64encode(contents.decoded_content).decode()
    except Exception:
        return None

# --- GITHUB CONNECTION ---
def init_github():
    try:
        token = st.secrets["GITHUB_TOKEN"]
        repo_name = st.secrets["REPO_NAME"]
        g = Github(token)
        return g.get_repo(repo_name)
    except Exception as e:
        st.error(f"GitHub Error: {e}")
        return None

def load_data(repo):
    """Downloads the latest JSON and its SHA from GitHub"""
    try:
        contents = repo.get_contents("fantasy_data.json")
        data = json.loads(contents.decoded_content.decode())
        if "player_stats" not in data: data["player_stats"] = {}
        if "users" not in data: data["users"] = {}
        if "logs" not in data: data["logs"] = []
        return data, contents.sha
    except Exception as e:
        st.error(f"Load Error: {e}")
        return {"users": {}, "player_stats": {}, "logs": []}, None

def sync_update(repo, update_func, message):
    try:
        latest_data, latest_sha = load_data(repo)
        if not latest_data: return False
        
        # --- LOGGING ---
        if "logs" not in latest_data: latest_data["logs"] = []
        current_user = st.session_state.user if st.session_state.user else "Guest"
        log_entry = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "user": current_user,
            "action": message
        }
        latest_data["logs"].append(log_entry)
        
        update_func(latest_data)
        repo.update_file("fantasy_data.json", message, json.dumps(latest_data, indent=2), latest_sha)
        st.session_state.data = latest_data
        return True
    except Exception as e:
        st.error(f"Sync Failed: {e}")
        return False

# --- POINT CALCULATION ---
def calculate_single_player_points(p_name, is_captain, is_bench, stats_db):
    if not p_name: return 0
    s = stats_db.get(p_name, {})
    pts = (s.get('goals',0) * POINTS['GOAL']) + \
          (s.get('assists',0) * POINTS['ASSIST']) + \
          (s.get('saves',0) * POINTS['SAVE']) + \
          (s.get('mom',0) * POINTS['MOM']) + \
          (s.get('yellow',0) * POINTS['YELLOW']) + \
          (s.get('red',0) * POINTS['RED']) + \
          (s.get('pen_save',0) * POINTS['PENALTY_SAVE']) + \
          (s.get('pen_miss',0) * POINTS['PENALTY_MISS']) + \
          (s.get('own_goal',0) * POINTS['OWN_GOAL']) + \
          (s.get('clean_sheet',0) * POINTS['CLEAN_SHEET']) + \
          (s.get('starting',0) * POINTS['STARTING'])
          
    if is_bench: pts = pts * 0.5
    if is_captain: pts = pts * 2
    return pts

def calculate_user_points(user_squad, user_captain, stats_db):
    total = 0
    if not user_squad: return 0
    
    gk = [user_squad.get('GK')] if user_squad.get('GK') else []
    defs = user_squad.get('DEF', [])
    fwds = user_squad.get('FWD', [])
    bench = user_squad.get('Bench', [])

    all_players = [(p, False) for p in gk+defs+fwds] + [(p, True) for p in bench]

    for p_name, is_bench in all_players:
        if not p_name: continue
        is_cap = (p_name == user_captain)
        total += calculate_single_player_points(p_name, is_cap, is_bench, stats_db)
    return total

# --- APP START ---
st.set_page_config(page_title="IIST 5s Fantasy", layout="wide", page_icon="⚽")

# --- GLOBAL CSS FOR CENTRAL ALIGNMENT & MAROON THEME ---
st.markdown("""
<style>
:root { --primary-color: #800000; }
.stButton>button { 
    width: 100%; border-radius: 8px; border: 1px solid #800000;
    color: #800000; background-color: white; font-weight: bold; transition: 0.3s;
}
.stButton>button:hover { background-color: #800000; color: white; border-color: #800000; }
h1, h2, h3 { color: #800000; }
th, td { text-align: center !important; }
div[data-testid="stDataFrame"] div[data-testid="stTable"] div[role="columnheader"],
div[data-testid="stDataFrame"] div[data-testid="stTable"] div[role="gridcell"] {
    justify-content: center; text-align: center;
}
</style>
""", unsafe_allow_html=True)

repo = init_github()

# --- CUSTOM HEADER (White Bar, Maroon Text) ---
img1_b64 = load_image_base64(repo, "valiamala_front_logo.png")
img2_b64 = load_image_base64(repo, "AAAM_analytics.png")

# Use a plain DIV with white background and Maroon text. Logos updated to 100px.
st.markdown(f"""
<div style="background-color:white; padding:15px; border-radius:10px; display:flex; align-items:center; justify-content:space-between; margin-bottom:20px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); border: 1px solid #eee;">
    <div style="flex:1; display:flex; justify-content:flex-start;">
        <img src="data:image/png;base64,{img1_b64}" style="height:100px; max-width:100%; object-fit:contain;">
    </div>
    <div style="flex:4; text-align:center;">
        <div style="color: #800000 !important; margin:0; font-size:clamp(18px, 4vw, 32px); font-weight:bold; text-transform:uppercase; letter-spacing:1px; font-family: sans-serif;">⚽ IIST 5s Fantasy Football League</div>
    </div>
    <div style="flex:1; display:flex; justify-content:flex-end;">
        <img src="data:image/png;base64,{img2_b64}" style="height:100px; max-width:100%; object-fit:contain;">
    </div>
</div>
""", unsafe_allow_html=True)

# --- INSERT MARQUEE HERE ---
st.markdown("""
<div style="background-color: #a5adad; color: #f7050d; padding: 8px; border-radius: 5px; margin-bottom: 15px; font-weight: bold; border: 1px solid #800000;">
    <marquee direction="left" scrollamount="8">
        📣️ Points updated! Check leaderboard!!!
    </marquee>
</div>
""", unsafe_allow_html=True)

if 'data' not in st.session_state: st.session_state.data = None
if 'user' not in st.session_state: st.session_state.user = None

if st.session_state.data is None and repo:
    d, s = load_data(repo)
    st.session_state.data = d

# ================= AUTH =================
if not st.session_state.user:
    t1, t2, t3 = st.tabs(["Login", "Register", "Rules"])
    
    with t1:
        with st.form("log"):
            u = st.text_input("SC Code").upper().strip()
            p = st.text_input("Password", type="password").strip()
            if st.form_submit_button("Login"):
                d, s = load_data(repo)
                st.session_state.data = d
                if u == ADMIN_USER and p == ADMIN_PASS:
                    st.session_state.user = "ADMIN"
                    st.rerun()
                db = st.session_state.data.get("users", {})
                if u in db and db[u]["password"] == p:
                    st.session_state.user = u
                    st.success("Welcome!")
                    st.rerun()
                else: st.error("Invalid Creds")

    with t2:
        with st.form("reg"):
            sc = st.text_input("SC Code").upper().strip()
            nm = st.text_input("Name").strip()
            pw = st.text_input("Password", type="password").strip()
            if st.form_submit_button("Register"):
                db = st.session_state.data.get("users", {})
                if sc in db: st.error("Exists")
                elif not sc or not nm or not pw: st.error("Fill all")
                else:
                    def reg_logic(data):
                        data["users"][sc] = {"name": nm, "password": pw, "squad": {"GK":None,"DEF":[],"FWD":[],"Bench":[]}, "captain":None}
                    if sync_update(repo, reg_logic, f"Reg {sc}"):
                        st.success("Registered! Login now.")
                        
    with t3:
        st.subheader("📜 Rules & Regulations")
        
        st.markdown("""
        **(a)** A prospective team manager must register using a **valid IIST student/internship ID card number**, their full name and a password of their choice. **There are no registration fees.** **(b)** A complete valid squad consists of 7 players (1 GK, 2 DEF, 2FWD, 2 BENCH). **Click on the "Confirm Squad" button after selecting/editing all your players, else the changes won't be saved.** **(c)** Maximum credits available per manager is 1000. Keep the budget in mind while selecting players for your team. **Do not forget to make one of your players captain!** **(d)** The deadline for squad selection/editing is till **17.30 hours IST, 15th February, 2026**. Past the deadline, no player selection/editing will be possible.  
        **(e)** Points are awarded based on player performance in each match:
        """)
        
        # Create a clean table for points
        rule_data = [{"Action": k.replace('_', ' '), "Points": v} for k, v in POINTS.items()]
        
        # Hide the index column and render the static table
        df_rules = pd.DataFrame(rule_data)
        st.dataframe(df_rules, hide_index=True)
        
        st.markdown("""
        **Notes:**
        * **Captain:** Scores **2x** points.
        * **Bench:** Scores **0.5x** points.
        * **Starting:** Players in the starting lineup get +2 points automatically.
        * **Clean Sheet:** All players in the winning team get +2 points automatically.
        
        **(f)** All prospective managers are encouraged to register and select their teams well before the deadline in order to reduce last minute rush and potential server crashes.  
        **(g)** The player stats will be updated daily after the completion of all matches. There will be some time lag between the finish of a day's matches and the player stat updation (1-2 hours). Your points and leaderboard will be updated immediately after the player stats are updated.  
        **(h)** The manager who tops the leaderboard after the finals will be given the prize. **Prize is only for the first position.** **(i)** In the event of a tie, the following methods would be determined for identifying the first position: (I) The manager with lowest utilized budget will be proclaimed winner. (II) If criterion (I) also results in a tie, the manager with the most number of players in his/her team who played in the final would be proclaimed winner. (III) If criteria (I) and (II) do not result in a winner, then the winner will be chosen by drawing a lot.    
        **(j)** **A valid student/internship ID card must be produced at the time of prize distribution. Failing to produce the same will result in immediate disqualification, and the prize will go to the 2nd position.** **(k)** **The decision of the tournament management team is final and binding. No negotiations/unsporstsmanlike behaviour will be entertained.** """)

# ================= ADMIN =================
elif st.session_state.user == "ADMIN":
    # --- MOVED SIDEBAR ELEMENTS TO MAIN PAGE ---
    adm_c1, adm_c2 = st.columns([6, 1])
    with adm_c1:
        st.title("⚙️ Stats Manager")
    with adm_c2:
        if st.button("Logout"): st.session_state.user = None; st.rerun()
    # -------------------------------------------
    
    if st.button("🔄 Force Refresh"): 
        d, s = load_data(repo)
        st.session_state.data = d
        st.success("Refreshed")

    stats_db = st.session_state.data.get("player_stats", {})
    
    ed_data = []
    for p in PLAYERS_DB:
        p_stats = stats_db.get(p['name'], {})
        row = {"Player": p['name']}
        for k in STAT_KEYS:
            row[k] = p_stats.get(k, 0)
        ed_data.append(row)
        
    df_stats_admin = pd.DataFrame(ed_data)
    edited_df = st.data_editor(df_stats_admin, key="editor", height=500)
    
    c_save, c_dl = st.columns(2)
    with c_save:
        if st.button("💾 Save Stats"):
            new_stats = {}
            for i, row in edited_df.iterrows():
                new_stats[row['Player']] = {k: int(row[k]) for k in STAT_KEYS}
            def update_stats_logic(data):
                data["player_stats"] = new_stats
            if sync_update(repo, update_stats_logic, "Stats Update"):
                st.success("✅ Stats Saved")
                time.sleep(1)
                st.rerun()
    with c_dl:
        csv = edited_df.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Download Stats CSV", data=csv, file_name="player_stats.csv", mime="text/csv")

    st.markdown("---")
    st.subheader("Admin Tools")
    c_adm1, c_adm2 = st.columns(2)
    
    with c_adm1:
        # DOWNLOAD ALL SQUADS
        squad_data = []
        for uid, u in st.session_state.data.get("users", {}).items():
            sq = u.get("squad", {})
            row = {
                "Manager Name": u.get("name"),
                "User ID": uid,
                "Goalkeeper": sq.get("GK"),
                "Defenders": ", ".join(sq.get("DEF", [])),
                "Forwards": ", ".join(sq.get("FWD", [])),
                "Bench": ", ".join(sq.get("Bench", [])),
                "Captain": u.get("captain")
            }
            squad_data.append(row)
        
        if squad_data:
            df_squads = pd.DataFrame(squad_data)
            csv_squads = df_squads.to_csv(index=False).encode('utf-8')
            st.download_button("📥 Download All Squads", data=csv_squads, file_name="all_user_squads.csv", mime="text/csv")
        else:
            st.info("No users found.")

    with c_adm2:
        # DOWNLOAD ACTIVITY LOGS
        logs = st.session_state.data.get("logs", [])
        if logs:
            df_logs = pd.DataFrame(logs)
            csv_logs = df_logs.to_csv(index=False).encode('utf-8')
            st.download_button("📥 Download Activity Logs", data=csv_logs, file_name="activity_logs.csv", mime="text/csv")
        else:
            st.info("No activity logs found.")

# ================= USER =================
else:
    uid = st.session_state.user
    if uid not in st.session_state.data["users"]: st.session_state.user = None; st.rerun()
    
    udata = st.session_state.data["users"][uid]
    squad = udata["squad"]
    stats_db = st.session_state.data.get("player_stats", {})

    squad['DEF'] = clean_squad_list(squad.get('DEF', []))
    squad['FWD'] = clean_squad_list(squad.get('FWD', []))
    squad['Bench'] = clean_squad_list(squad.get('Bench', []))
    
    used = 0
    if squad.get('GK'): used += get_player_details(squad['GK'])['price']
    for p in squad['DEF']+squad['FWD']+squad['Bench']: used += get_player_details(p)['price']
    rem = 1000 - used
    pts = calculate_user_points(squad, udata.get('captain'), stats_db)

    # --- MOVED SIDEBAR ELEMENTS TO TOP OF MAIN PAGE ---
    c_dash1, c_dash2, c_dash3, c_dash4, c_dash5 = st.columns([2, 1.2, 1.2, 1.5, 1])
    
    with c_dash1:
        st.markdown(f"### {udata['name']}")
    with c_dash2:
        st.markdown(f"**Budget: {rem}**")
    with c_dash3:
        st.markdown(f"**Points: {pts}**")
    with c_dash4:
        if st.button("✅ Confirm Squad"):
            cnt = (1 if squad.get('GK') else 0) + len(squad['DEF']) + len(squad['FWD']) + len(squad['Bench'])
            if cnt < 7: st.error("Incomplete Squad")
            elif rem < 0: st.error("Over Budget")
            else: st.success("Squad Valid!"); st.balloons()
    with c_dash5:
        if st.button("Logout"): st.session_state.user = None; st.rerun()
    # --------------------------------------------------

    t1, t2, t3, t4, t5, t6 = st.tabs(["Squad", "Stats", "Schedule & Squads", "Tournament Statistics", "Leaderboard", "Rules"])

    with t1:
        # CHANGED: Explicitly checking against IST time (UTC+5.5) to fix server timezone mismatch
        open_mkt = (datetime.utcnow() + timedelta(hours=5, minutes=30)) < MARKET_DEADLINE
        
        if not open_mkt: st.warning("Market Closed")
        c1, c2 = st.columns([1, 1.2])
        
        with c1:
            # MOBILE LAYOUT FIX: Force side-by-side columns for V shape on small screens
            bg_css = """
            <style>
            @media (max-width: 640px) {
                div[data-testid="column"]:nth-of-type(1) [data-testid="stHorizontalBlock"],
                div[data-testid="stColumn"]:nth-of-type(1) [data-testid="stHorizontalBlock"] {
                    flex-direction: row !important;
                    flex-wrap: nowrap !important;
                }
                div[data-testid="column"]:nth-of-type(1) [data-testid="stHorizontalBlock"] [data-testid="column"],
                div[data-testid="stColumn"]:nth-of-type(1) [data-testid="stHorizontalBlock"] [data-testid="stColumn"] {
                    min-width: 0 !important;
                    width: auto !important;
                    flex: 1 1 auto !important;
                }
            }
            </style>
            """
            st.markdown(bg_css, unsafe_allow_html=True)

            st.subheader("Starting V")
            
            # --- INVERTED V LAYOUT: GK TOP -> DEF -> FWD ---
            def card(pid, role, idx=None, bench=False):
                p = get_player_details(pid)
                if p:
                    cap = (p['name'] == udata.get('captain'))
                    current_pts = calculate_single_player_points(pid, cap, bench, stats_db)
                    pos_str = p['pos'][0][:3].upper()
                    
                    st.markdown(f"""
                    <div style="background:{'#fff9c4' if cap else '#ffffff'}; border:2px solid {'#ffd700' if cap else '#333'}; border-radius:8px; padding:6px; text-align:center; margin-bottom:5px; box-shadow: 0 4px 6px rgba(0,0,0,0.3);">
                        {'🌟 ' if cap else ''}<b>{p['name']}</b><br>
                        <span style="font-size:0.8em; color:#333;">{pos_str} | <b>{current_pts} pts</b> | {p['price']}</span>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    if open_mkt:
                        b1, b2 = st.columns(2)
                        if b1.button("❌", key=f"d{pid}{role}{idx}"):
                            def remove_logic(data):
                                u_sq = data["users"][uid]["squad"]
                                if role=='GK': u_sq['GK']=None
                                elif role=='DEF': u_sq['DEF'].remove(pid)
                                elif role=='FWD': u_sq['FWD'].remove(pid)
                                elif role=='Bench': u_sq['Bench'].remove(pid)
                                if pid == data["users"][uid].get('captain'): data["users"][uid]['captain']=None
                            sync_update(repo, remove_logic, f"Rem {pid}")
                            st.rerun()
                        if not bench and b2.button("©", key=f"c{pid}{role}"):
                            def cap_logic(data):
                                data["users"][uid]['captain'] = pid
                            sync_update(repo, cap_logic, f"Cap {pid}")
                            st.rerun()
                else: 
                    st.markdown(f"""<div style="background:rgba(255,255,255,0.7); border:2px dashed #444; border-radius:8px; padding:15px; text-align:center; font-weight:bold; color:#222;">{role}</div>""", unsafe_allow_html=True)

            # 1. Goalkeeper (Top Center)
            gc1, gc2, gc3 = st.columns([1,1,1])
            with gc2: card(squad.get('GK'), 'GK')

            st.markdown("<br>", unsafe_allow_html=True) 

            # 2. Defenders (Middle)
            d = squad.get('DEF',[])
            dc1, dc2 = st.columns(2)
            with dc1: card(d[0] if len(d)>0 else None, 'DEF', 0)
            with dc2: card(d[1] if len(d)>1 else None, 'DEF', 1)

            st.markdown("<br>", unsafe_allow_html=True) 

            # 3. Forwards (Bottom)
            f = squad.get('FWD',[])
            fc1, fc2 = st.columns(2)
            with fc1: card(f[0] if len(f)>0 else None, 'FWD', 0)
            with fc2: card(f[1] if len(f)>1 else None, 'FWD', 1)
            
            st.markdown("---")
            st.markdown("<h6 style='color:black; text-shadow: 1px 1px 2px white;'>Bench</h6>", unsafe_allow_html=True)
            bc1, bc2 = st.columns(2)
            b = squad.get('Bench',[])
            with bc1: card(b[0] if len(b)>0 else None, 'Bench', 0, True)
            with bc2: card(b[1] if len(b)>1 else None, 'Bench', 1, True)

        with c2:
            st.subheader("Market")
            srch = st.text_input("Search")
            fil = st.selectbox("Pos", ["All","Goalkeeper","Defender","Midfielder","Forward"])
            res = [p for p in PLAYERS_DB if (srch.lower() in p['name'].lower()) and (fil=="All" or fil in p['pos'])]
            own = [squad.get('GK')] + squad.get('DEF',[]) + squad.get('FWD',[]) + squad.get('Bench',[])
            
            for p in res:
                # UPDATED: Name | Price | Positions
                label = f"{p['name']} | {p['price']} | {', '.join(p['pos'])}"
                with st.expander(label):
                    if p['name'] in own: st.info("Owned")
                    elif rem < p['price']: st.error("No Funds")
                    elif not open_mkt: st.warning("Closed")
                    else:
                        c_ops = st.columns(4)
                        def add_player(role, pname):
                            def logic(data):
                                u_sq = data["users"][uid]["squad"]
                                if role == "GK": u_sq["GK"] = pname
                                else: u_sq[role].append(pname)
                            sync_update(repo, logic, f"Add {pname}")
                            st.rerun()

                        if "Goalkeeper" in p['pos'] and c_ops[0].button("GK", key=f"bgk{p['name']}"):
                            if squad['GK']: st.error("Full")
                            else: add_player("GK", p['name'])
                            
                        if ("Defender" in p['pos'] or "Midfielder" in p['pos']) and c_ops[1].button("DEF", key=f"bdef{p['name']}"):
                            if len(squad['DEF'])>=2: st.error("Full")
                            else: add_player("DEF", p['name'])
                            
                        if "Forward" in p['pos'] and c_ops[2].button("FWD", key=f"bfwd{p['name']}"):
                            if len(clean_squad_list(squad['FWD']))>=2: st.error("Full")
                            else: add_player("FWD", p['name'])
                            
                        if c_ops[3].button("Bench", key=f"bbn{p['name']}"):
                            if len(clean_squad_list(squad['Bench']))>=2: st.error("Full")
                            else: add_player("Bench", p['name'])

    with t2:
        # Build User Stats Table explicitly ensuring all columns are shown
        stats_list = []
        for p in PLAYERS_DB:
            p_stats = stats_db.get(p['name'], {})
            row = {"Player": p['name']}
            for k in STAT_KEYS:
                row[k] = p_stats.get(k, 0)
            stats_list.append(row)
            
        df_stats = pd.DataFrame(stats_list)
        if not df_stats.empty:
            df_stats.insert(0, "No.", range(1, 1 + len(df_stats)))
            st.dataframe(df_stats, hide_index=True, use_container_width=True)
    
    with t3: 
        st.subheader("📅 Match Schedule and Squad list")
        try:
            # Display updated schedule images
            # Using use_container_width to ensure visibility on mobile
            st.image(["1.png", "2.png", "3.png","squad.png"], use_container_width=True)
        except Exception:
            st.info("Schedule images (1.png, 2.png, 3.png, squad.png) not found.")

    with t4:
        st.subheader("📊 Tournament Statistics")
        try:
            st.image("points_table.png", use_container_width=True)
        except Exception:
            st.info("Points table not found.")

    with t5:
        if st.button("Refresh"): 
            d, s = load_data(repo)
            st.session_state.data = d
            st.rerun()
        
        # Leaderboard with Rank (1-based) and User Details
        lb = []
        for u_id, u_data in st.session_state.data['users'].items():
            pts = calculate_user_points(u_data['squad'], u_data.get('captain'), stats_db)
            lb.append({
                "User ID": u_id,
                "Manager Name": u_data['name'],
                "Points": pts
            })
        
        if lb:
            df_lb = pd.DataFrame(lb).sort_values("Points", ascending=False)
            df_lb.insert(0, "Rank", range(1, 1 + len(df_lb)))
            st.dataframe(df_lb, hide_index=True, use_container_width=True)

    with t6:
        st.subheader("📜 Rules & Regulations")
        
        st.markdown("""
        **(a)** A prospective team manager must register using a **valid IIST student/internship ID card number**, their full name and a password of their choice. **There are no registration fees.** **(b)** A complete valid squad consists of 7 players (1 GK, 2 DEF, 2FWD, 2 BENCH). **Click on the "Confirm Squad" button after selecting/editing all your players, else the changes won't be saved.** **(c)** Maximum credits available per manager is 1000. Keep the budget in mind while selecting players for your team. **Do not forget to make one of your players captain!** **(d)** The deadline for squad selection/editing is till **17.30 hours IST, 15th February, 2026**. Past the deadline, no player selection/editing will be possible.  
        **(e)** Points are awarded based on player performance in each match:
        """)
        
        # Create a clean table for points
        rule_data = [{"Action": k.replace('_', ' '), "Points": v} for k, v in POINTS.items()]
        
        # Hide the index column and render the static table
        df_rules = pd.DataFrame(rule_data)
        st.dataframe(df_rules, hide_index=True)
        
        st.markdown("""
        **Notes:**
        * **Captain:** Scores **2x** points.
        * **Bench:** Scores **0.5x** points.
        * **Starting:** Players in the starting lineup get +2 points automatically.
        * **Clean Sheet:** All players in the winning team get +2 points automatically.
        
        **(f)** All prospective managers are encouraged to register and select their teams well before the deadline in order to reduce last minute rush and potential server crashes.  
        **(g)** The player stats will be updated daily after the completion of all matches. There will be some time lag between the finish of a day's matches and the player stat updation (1-2 hours). Your points and leaderboard will be updated immediately after the player stats are updated.  
        **(h)** The manager who tops the leaderboard after the finals will be given the prize. **Prize is only for the first position.** **(i)** In the event of a tie, the following methods would be determined for identifying the first position: (I) The manager with lowest utilized budget will be proclaimed winner. (II) If criterion (I) also results in a tie, the manager with the most number of players in his/her team who played in the final would be proclaimed winner. (III) If criteria (I) and (II) do not result in a winner, then the winner will be chosen by drawing a lot.    
        **(j)** **A valid student/internship ID card must be produced at the time of prize distribution. Failing to produce the same will result in immediate disqualification, and the prize will go to the 2nd position.** **(k)** **The decision of the tournament management team is final and binding. No negotiations/unsporstsmanlike behaviour will be entertained.** """)

# --- FOOTER ---
st.markdown("---")
c_f1, c_f2 = st.columns(2)
with c_f1:
    st.metric("Total Footballers", len(PLAYERS_DB))
with c_f2:
    st.metric("Registered Managers", len(st.session_state.data.get("users", {})))
