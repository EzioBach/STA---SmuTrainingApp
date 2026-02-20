import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
import json
from datetime import date
import streamlit.components.v1 as components

st.set_page_config(page_title="SMU Training", layout="wide", page_icon="🛡️")

@st.cache_resource
def get_db():
    conn = sqlite3.connect('progress.db')
    conn.execute('CREATE TABLE IF NOT EXISTS users (user_id TEXT PRIMARY KEY, data TEXT)')
    return conn

# GAMIFIED SIDEBAR
st.sidebar.markdown("""
# 🛡️ SMU Training Quest
**Level Up Your Digital Life!**
""")
user_id = st.sidebar.text_input("🆔 Your Hero ID")
st.sidebar.markdown("---")

if user_id:
    conn = get_db()
    
    def load_data(uid):
        c = conn.cursor()
        c.execute("SELECT data FROM users WHERE user_id=?", (uid,))
        row = c.fetchone()
        return json.loads(row[0]) if row else {'level':0, 'logs':[], 'badges':[]}
    
    def save_data(uid, data):
        conn.execute("REPLACE INTO users VALUES (?, ?)", (uid, json.dumps(data)))
        conn.commit()
    
    data = load_data(user_id)

# 🔥 DASHBOARD
if st.sidebar.button("🏠 Quest Hub", key="dash"):
    st.markdown("""
    # 🎮 Welcome, Digital Warrior!
    
    **14-Day SMU Quest: Conquer Scroll Addiction**
    
    """)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("🏆 Level", data['level'], delta="+1")
    with col2:
        df = pd.DataFrame(data['logs'])
        avg = df['duration'].mean() if not df.empty else 0
        st.metric("📉 SMU Reduced", f"{avg:.0f}min", delta="-30")
    with col3:
        prog = min(data['level']/3 *100, 100)
        st.metric("⚡ Progress", f"{prog:.0f}%")
    
    if data['logs']:
        fig = px.line(pd.DataFrame(data['logs']), x='date', y='duration', 
                     title="📊 Victory Chart - Watch SMU DROP!")
        st.plotly_chart(fig, use_container_width=True)
    
    st.balloons()

# 📚 DAY 1 - Awareness
if st.sidebar.button("📚 Level 1: Awareness", key="day1"):
    st.markdown("""
    # 📚 Level 1: **DOPAMINE TRAP UNLOCKED**
    
    **The Enemy**: Social media = slot machine (variable rewards → addiction)
    
    **Stats Attack**:
    • Teens: 4+ hrs/day 📱
    • Anxiety +33%, Sleep -2hrs 😴
    • FOMO destroys focus ⚡[file:3]
    
    **Boss Models**:
    - I-PACE: Person → Addiction cycle
    - Self-Regulation Fail (no willpower needed)
    """)
    
    with st.form("tracker1"):
        apps = st.multiselect("⚔️ Enemy Apps", ["Instagram", "TikTok", "Snap", "X"])
        mins = st.slider("⏱️ Battle Time (min)", 0, 600, 60)
        trigger = st.selectbox("🎭 Weakness", ["Boredom", "FOMO", "Escape"])
        st.form_submit_button("💥 Destroy Day 1", use_container_width=True)
    
    if st.session_state.get('day1_done'):
        data['level'] = 1
        data['logs'].append({'date':str(date.today()), 'duration':mins, 'apps':apps})
        data['badges'].append('Awareness Master')
        save_data(user_id, data)
        st.success("🏅 **LEVEL 1 CLEARED!**")

# 🎯 DAY 2 - Strategies  
if st.sidebar.button("🎯 Level 2: Battle Tactics", key="day2"):
    st.markdown("""
    # 🎯 Level 2: **URGE WARRIOR**
    
    **Urge Curve**: Rises 2min → Peaks 10min → Drops naturally
    
    **Power Moves**:
    • **Delay Tactic**: Wait 10min, ask "What happens after scroll?"
    • **Digital Fortress**: 
      - Delete home screen apps
      - Grey mode ON
      - Notifications → OFF
      - Phone-free zones (bed, meals)[file:1]
    """)
    
    if st.button("🔥 Master Day 2", use_container_width=True) and data['level'] >=1:
        data['level'] = 2
        data['badges'].append('Tactics Legend')
        save_data(user_id, data)
        st.balloons()

# 🔒 DAY 3 - Maintenance
if st.sidebar.button("🔒 Level 3: Eternal Guard", key="day3"):
    st.markdown("""
    # 🔒 Level 3: **RELAPSE DESTROYER**
    
    **Final Boss: Maintenance**
    • Lapse ≠ Game Over (self-compassion)
    • **Your Rules**: "SM = 30min evenings ONLY"
    • Warning Signs: Boredom creeping → Action!
    
    **Victory Metrics** 📊
    ✓ Screen time -50%
    ✓ Focus +200%
    ✓ Life satisfaction ↑[file:3]
    """)
    
    if st.button("👑 Quest Complete!", use_container_width=True) and data['level'] >=2:
        data['level'] = 3
        data['badges'].append('Digital Master')
        save_data(user_id, data)
        st.markdown("## 🎉 **LEGENDARY HERO!** 🎉")
        st.balloons()

st.markdown("---")
st.caption("Powered by Action Regulation Theory")[file:2]
