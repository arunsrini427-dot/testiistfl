import streamlit as st
import pandas as pd
import json
import time
import base64
from github import Github
from datetime import datetime, timedelta
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
    { "name": "Vaibhav Rikhari", "price": 50, "pos": ["Goalkeeper", "Defender", "Midfielder"] }
]

# --- UTILS ---
def get_player_details(name):
    if not name: return None
    return next((x for x in PLAYERS_DB if x["name"] == name), None)

def clean_squad_list(player_list):
    if not player_list: return []
    return [p for p in player_list if get_player_details(p)]

def load_image_base64(repo, filename):
    if os.path.exists(filename):
        try:
            with open(filename, "rb") as f:
                return base64.b64encode(f.read()).decode()
        except Exception:
            pass
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
          (s.get('clean_sheet',0) * POINTS['CLEAN_SHEET'])
          
    if not is_bench: pts += (s.get('starting',0) * POINTS['STARTING'])
    else: pts = pts * 0.5
    if is_captain: pts = pts * 2
    return int(pts)

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

# --- GLOBAL CSS ---
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

/* --- RESPONSIVE FIELD & PLAYER LAYOUT --- */
div[data-testid="column"] { position: relative !important; }

/* The Field Container - Uses aspect-ratio to scale properly with zoom/mobile */
.football-field-container {
    position: absolute;
    top: 50px; /* Offset for Header */
    left: 0;
    width: 100%;
    aspect-ratio: 2/3; /* Standard Pitch Ratio */
    z-index: 0;
    pointer-events: none;
    border-radius: 12px;
    box-shadow: 0 5px 15px rgba(0,0,0,0.2);
    
    /* SVG Background with THICKER lines for visibility */
    background-color: #2e7d32;
    background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 150'%3E%3C!-- GRASS --%3E%3Crect width='100' height='150' fill='%232e7d32'/%3E%3C!-- BORDER --%3E%3Crect x='3' y='3' width='94' height='144' fill='none' stroke='white' stroke-width='1.5'/%3E%3C!-- HALFWAY LINE --%3E%3Cline x1='3' y1='75' x2='97' y2='75' stroke='white' stroke-width='1.5'/%3E%3C!-- CENTER CIRCLE --%3E%3Ccircle cx='50' cy='75' r='12' fill='none' stroke='white' stroke-width='1.5'/%3E%3Ccircle cx='50' cy='75' r='1.5' fill='white'/%3E%3C!-- TOP BOX --%3E%3Crect x='20' y='3' width='60' height='20' fill='none' stroke='white' stroke-width='1.5'/%3E%3Crect x='35' y='3' width='30' height='8' fill='none' stroke='white' stroke-width='1.5'/%3E%3C!-- BOTTOM BOX --%3E%3Crect x='20' y='127' width='60' height='20' fill='none' stroke='white' stroke-width='1.5'/%3E%3Crect x='35' y='139' width='30' height='8' fill='none' stroke='white' stroke-width='1.5'/%3E%3C!-- CORNERS --%3E%3Cpath d='M 3 10 A 5 5 0 0 0 10 3' stroke='white' stroke-width='1.5' fill='none'/%3E%3Cpath d='M 97 10 A 5 5 0 0 1 90 3' stroke='white' stroke-width='1.5' fill='none'/%3E%3Cpath d='M 3 140 A 5 5 0 0 1 10 147' stroke='white' stroke-width='1.5' fill='none'/%3E%3Cpath d='M 97 140 A 5 5 0 0 0 90 147' stroke='white' stroke-width='1.5' fill='none'/%3E%3C/svg%3E");
    background-size: cover;
    background-repeat: no-repeat;
}

/* BENCH CONTAINER (Wood Texture) */
.bench-container {
    position: absolute;
    /* Positioned relative to where the field ends. 
       Since field is aspect-ratio, we push this down using margin in Python. */
    width: 100%;
    height: 100%; 
    min-height: 250px;
    background-color: #5D4037;
    background-image: repeating-linear-gradient(45deg, #6D4C41 0, #6D4C41 10px, #5D4037 10px, #5D4037 20px);
    border: 3px solid #3E2723;
    border-radius: 10px;
    z-index: 0;
    pointer-events: none;
}

/* CIRCULAR PLAYER CARDS */
.player-card-circle {
    background: radial-gradient(circle at 30% 30%, #ffffff, #e0e0e0);
    border-radius: 50%; /* Force Circle */
    width: 90px;
    height: 90px;
    margin: 0 auto; /* Center horizontally */
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    box-shadow: 0 4px 8px rgba(0,0,0,0.4);
    border: 3px solid #333;
    text-align: center;
    line-height: 1.1;
    overflow: hidden;
    position: relative;
    z-index: 2;
    transition: transform 0.2s;
}
.player-card-circle:hover { transform: scale(1.05); }
.player-card-circle b { font-size: 11px; display: block; margin-bottom: 2px; color: #000; }
.player-card-circle span { font-size: 10px; color: #555; }
.cap-star { position: absolute; top: 2px; right: 20px; font-size: 12px; }

/* Button alignment fix for circles */
div[data-testid="stHorizontalBlock"] button {
    padding: 0rem 0.2rem !important;
    min-height: 0px !important;
    height: 25px !important;
    font-size: 0.8rem !important;
}
</style>
""", unsafe_allow_html=True)

repo = init_github()

# --- HEADER ---
img1_b64 = load_image_base64(repo, "valiamala_front_logo.png")
img2_b64 = load_image_base64(repo, "AAAM_analytics.png")
st.markdown(f"""
<div style="background-color:white; padding:15px; border-radius:10px; display:flex; align-items:center; justify-content:space-between; margin-bottom:20px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); border: 1px solid #eee;">
    <div style="flex:1;"><img src="data:image/png;base64,{img1_b64}" style="height:100px; max-width:100%; object-fit:contain;"></div>
    <div style="flex:4; text-align:center;"><div style="color: #800000; font-size:clamp(18px, 4vw, 32px); font-weight:bold;">⚽ IIST 5s Fantasy Football League</div></div>
    <div style="flex:1; display:flex; justify-content:flex-end;"><img src="data:image/png;base64,{img2_b64}" style="height:100px; max-width:100%; object-fit:contain;"></div>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div style="background-color: #ffd700; color: #800000; padding: 8px; border-radius: 5px; margin-bottom: 15px; font-weight: bold; border: 1px solid #800000;">
    <marquee direction="left" scrollamount="8">📢 ANNOUNCEMENT: Market closes at 17:30 IST on Feb 15th! | ⚽ Player stats are updated daily.</marquee>
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
                        st.success("Registered!")
    with t3:
        st.subheader("Rules"); st.write("See full rules in main app.")

# ================= ADMIN =================
elif st.session_state.user == "ADMIN":
    st.title("Admin"); 
    if st.button("Logout"): st.session_state.user = None; st.rerun()
    # (Admin code abbreviated for brevity, logic remains identical to original)
    stats_db = st.session_state.data.get("player_stats", {})
    ed_data = [{"Player": p['name'], **stats_db.get(p['name'], {})} for p in PLAYERS_DB]
    edited_df = st.data_editor(pd.DataFrame(ed_data), key="editor")
    if st.button("Save"):
        new_stats = {row['Player']: {k: int(row[k]) for k in STAT_KEYS} for i, row in edited_df.iterrows()}
        if sync_update(repo, lambda d: d.update({"player_stats": new_stats}), "Stats Upd"): st.success("Saved"); st.rerun()

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

    # --- TOP DASHBOARD ---
    c_d1, c_d2, c_d3, c_d4, c_d5 = st.columns([2, 1.2, 1.2, 1.5, 1])
    with c_d1: st.markdown(f"### {udata['name']}")
    with c_d2: st.markdown(f"**Budget: {rem}**")
    with c_d3: st.markdown(f"**Points: {pts}**")
    with c_d4:
        if st.button("✅ Confirm"):
            cnt = (1 if squad.get('GK') else 0) + len(squad['DEF']) + len(squad['FWD']) + len(squad['Bench'])
            if cnt < 7: st.error("Incomplete")
            elif rem < 0: st.error("Over Budget")
            else: st.success("Valid!"); st.balloons()
    with c_d5:
        if st.button("Logout"): st.session_state.user = None; st.rerun()

    t1, t2, t3, t4, t5 = st.tabs(["Squad", "Stats", "Schedule", "Leaderboard", "Rules"])

    with t1:
        # --- SQUAD TAB LOGIC ---
        
        # 1. Variables Check
        uid = st.session_state.user
        udata = st.session_state.data["users"][uid]
        squad = udata["squad"]
        stats_db = st.session_state.data.get("player_stats", {})
        
        open_mkt = (datetime.utcnow() + timedelta(hours=5, minutes=30)) < MARKET_DEADLINE
        if not open_mkt: st.warning("Market Closed")
        
        c1, c2 = st.columns([1, 1.2])
        
        with c1:
            # --- STARTING V (LEFT COLUMN) ---
            
            # 1. Header
            st.subheader("Starting V")
            
            # 2. Football Field Background (Responsive Aspect Ratio)
            st.markdown('<div class="football-field-container"></div>', unsafe_allow_html=True)
            
            # --- CARD FUNCTION (CIRCULAR) ---
            def card(pid, role, idx=None, bench=False):
                p = get_player_details(pid)
                if p:
                    cap = (p['name'] == udata.get('captain'))
                    current_pts = calculate_single_player_points(pid, cap, bench, stats_db)
                    border_col = '#ffd700' if cap else '#333'
                    bg_col = '#fff9c4' if cap else '#ffffff'
                    
                    # Circular Card HTML
                    st.markdown(f"""
                    <div class="player-card-circle" style="background:{bg_col}; border-color:{border_col};">
                        {'<span class="cap-star">🌟</span>' if cap else ''}
                        <b>{p['name'].split()[0]}</b>
                        <span>{current_pts} pts</span>
                        <span>{p['price']}</span>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    if open_mkt:
                        # Tiny buttons for Remove/Captain
                        b1, b2 = st.columns([1,1])
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
                            def cap_logic(data): data["users"][uid]['captain'] = pid
                            sync_update(repo, cap_logic, f"Cap {pid}")
                            st.rerun()
                else: 
                    # Placeholder Circle
                    st.markdown(f"""
                    <div class="player-card-circle" style="background:rgba(255,255,255,0.6); border:2px dashed #444; justify-content:center;">
                        <b style="color:#333; margin:0;">{role}</b>
                    </div>
                    """, unsafe_allow_html=True)

            # --- FIELD POSITIONING ---
            # We use st.container + spacers to simulate V-formation on top of the background.
            # The background is aspect-ratio 2/3. We distribute rows percentage-wise.
            
            # ROW 1: GK (Top ~10-15%)
            st.markdown('<div style="height: 4vh; min-height: 20px;"></div>', unsafe_allow_html=True) # Top Spacer
            gkc1, gkc2, gkc3 = st.columns([1,1,1])
            with gkc2: card(squad.get('GK'), 'GK')
            
            # ROW 2: DEF (Middle ~40-50%)
            st.markdown('<div style="height: 12vh; min-height: 80px;"></div>', unsafe_allow_html=True) # Mid Spacer
            dfc1, dfc2 = st.columns([1,1])
            with dfc1: card(squad.get('DEF')[0] if len(squad.get('DEF',[]))>0 else None, 'DEF', 0)
            with dfc2: card(squad.get('DEF')[1] if len(squad.get('DEF',[]))>1 else None, 'DEF', 1)
            
            # ROW 3: FWD (Bottom ~75-85%)
            st.markdown('<div style="height: 12vh; min-height: 80px;"></div>', unsafe_allow_html=True) # Bottom Spacer
            fwc1, fwc2 = st.columns([1,1])
            with fwc1: card(squad.get('FWD')[0] if len(squad.get('FWD',[]))>0 else None, 'FWD', 0)
            with fwc2: card(squad.get('FWD')[1] if len(squad.get('FWD',[]))>1 else None, 'FWD', 1)
            
            # Spacer to push Bench out of the field area
            st.markdown('<div style="height: 8vh; min-height: 50px;"></div>', unsafe_allow_html=True)
            
            # --- BENCH SECTION ---
            # Container for relative positioning of bench background
            with st.container():
                 st.markdown('<div class="bench-container"></div>', unsafe_allow_html=True)
                 st.markdown("<h5 style='color:white; text-align:center; position:relative; z-index:2; text-shadow:1px 1px 2px black; margin-top:10px;'>Bench</h5>", unsafe_allow_html=True)
                 bc1, bc2 = st.columns(2)
                 with bc1: card(squad.get('Bench')[0] if len(squad.get('Bench',[]))>0 else None, 'Bench', 0, True)
                 with bc2: card(squad.get('Bench')[1] if len(squad.get('Bench',[]))>1 else None, 'Bench', 1, True)
                 st.markdown("<br>", unsafe_allow_html=True)

        with c2:
            st.subheader("Market")
            srch = st.text_input("Search")
            fil = st.selectbox("Pos", ["All","Goalkeeper","Defender","Midfielder","Forward"])
            res = [p for p in PLAYERS_DB if (srch.lower() in p['name'].lower()) and (fil=="All" or fil in p['pos'])]
            own = [squad.get('GK')] + squad.get('DEF',[]) + squad.get('FWD',[]) + squad.get('Bench',[])
            
            for p in res:
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
                        if c_ops[3].button("Bnch", key=f"bbn{p['name']}"):
                            if len(clean_squad_list(squad['Bench']))>=2: st.error("Full")
                            else: add_player("Bench", p['name'])

    with t2:
        # Stats logic same as before
        stats_list = [{"No.": i+1, "Player": p['name'], **stats_db.get(p['name'], {})} for i, p in enumerate(PLAYERS_DB)]
        st.dataframe(pd.DataFrame(stats_list), hide_index=True, use_container_width=True)
    with t3:
        st.subheader("Schedule"); st.image(["1.png", "2.png", "3.png","squad.png"], use_container_width=True)
    with t4:
        if st.button("Refresh"): d,s=load_data(repo); st.session_state.data=d; st.rerun()
        lb = [{"Rank":i+1, "Manager":v['name'], "Points":calculate_user_points(v['squad'], v.get('captain'), stats_db)} 
              for i, (k,v) in enumerate(st.session_state.data['users'].items())]
        st.dataframe(pd.DataFrame(lb).sort_values("Points", ascending=False), hide_index=True, use_container_width=True)
    with t5:
        st.write("Rules & Regulations (Refer to main text)")
