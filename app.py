import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
import json
from datetime import date

st.set_page_config(page_title="🛡️ SMU Training", layout="wide")

@st.cache_resource
def init_db():
    conn = sqlite3.connect('progress.db')
    conn.execute('''CREATE TABLE IF NOT EXISTS users 
                    (user_id TEXT PRIMARY KEY, data TEXT)''')
    return conn

conn = init_db()

# Sidebar
st.sidebar.title("Training Progress")
user_id = st.sidebar.text_input("Your ID", key="user_id")
page = st.sidebar.selectbox("Day", ["🏠 Dashboard", "📚 Day 1", "🎯 Day 2", "🔒 Day 3"])

def load_user_data(user_id):
    cur = conn.cursor()
    cur.execute("SELECT data FROM users WHERE user_id=?", (user_id,))
    row = cur.fetchone()
    return json.loads(row[0]) if row else {'days':0, 'logs':[], 'quiz':{}}

def save_user_data(user_id, data):
    conn.execute("INSERT OR REPLACE INTO users (user_id, data) VALUES (?, ?)", 
                (user_id, json.dumps(data)))
    conn.commit()

if user_id:
    data = load_user_data(user_id)

# Pages
if page == "🏠 Dashboard":
    st.title("Social Media Usage Training")
    st.markdown("**14-day program for young adults/students** - Reduce problematic SMU through awareness & strategies.")[file:2]
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Days Done", data['days'])
    col2.metric("Avg SMU (min)", round(pd.DataFrame(data['logs'])['duration'].mean() if data['logs'] else 0))
    col3.metric("Goal Progress", f"{min(data['days']/3*100,100):.0f}%")
    
    if data['logs']:
        df = pd.DataFrame(data['logs'])
        fig = px.line(df, x='date', y='duration', title="Your SMU Trend ↓")
        st.plotly_chart(fig, use_container_width=True)[file:3]

elif page == "📚 Day 1":
    st.header("Day 1: Psychoeducation & Awareness")
    st.markdown("""
    **Objectives**: Understand SMU impact on mental health, productivity.
    
    **Key Facts**:
    - **Stats**: Teens avg 4+ hrs/day; linked to anxiety, sleep issues.[file:3]
    - **Why addictive?** Dopamine, variable rewards (like slots).
    - **Models**: I-PACE (Person-Affect-Cognition-Execution), Self-Regulation Failure.
    - **Harms**: Attention deficit, FOMO, low self-esteem.
    """)[file:1][file:3]
    
    # Tracker
    st.subheader("Homework: Track Usage")
    apps = st.multiselect("Top Apps", ["Instagram", "TikTok", "Snapchat", "X"], key="d1_apps")
    duration = st.slider("Duration (min)", 0, 600, 60, key="d1_dur")
    trigger = st.text_input("Triggers (boredom/FOMO)?", key="d1_trig")
    
    if st.button("✅ Complete Day 1", key="d1_complete"):
        data['days'] += 1
        data['logs'].append({'date':str(date.today()), 'apps':apps, 'duration':duration, 'trigger':trigger})
        save_user_data(user_id, data)
        st.balloons()
        st.success("Day 1 logged! Progress saved.")

elif page == "🎯 Day 2":
    st.header("Day 2: Triggers & Emotional Regulation")
    st.markdown("""
    **Objectives**: Identify triggers, build urge resistance.
    
    **Strategies**:
    - **Triggers**: Internal (boredom) vs External (notifications).
    - **Urge Surfing**: Delay 10 min, ask "What happens after scrolling?"
    - **Digital Hygiene**: App limits, no home screen, grey mode, screen-free zones.
    - **Homework**: 1hr phone-free daily, delete notifications.[file:1]
    """)
    
    if st.button("✅ Complete Day 2", key="d2_complete") and data['days'] >=1:
        data['days'] += 1
        save_user_data(user_id, data)
        st.success("Day 2 done!")

elif page == "🔒 Day 3":
    st.header("Day 3: Maintenance & Relapse Prevention")
    st.markdown("""
    **Objectives**: Sustain changes long-term.
    
    **Key Tools**:
    - **Lapse vs Relapse**: One slip ≠ failure.
    - **Personal Rules**: e.g., "SM only 30min evenings, purposeful use."
    - **Handle Pressure**: Self-compassion, values alignment.
    - **Warning Signs**: Track early relapse cues.[file:1]
    """)
    
    if st.button("✅ Finish Training", key="d3_complete") and data['days'] >=2:
        data['days'] = 3
        save_user_data(user_id, data)
        st.balloons()
        st.markdown("🎉 **Training Complete!** Review Dashboard.")

st.markdown("---")
st.caption("Based on Action Regulation Theory")[file:2]
