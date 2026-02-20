import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
import json
from datetime import date

st.set_page_config(page_title="SMU Training Program", layout="wide", page_icon="📊")

@st.cache_resource
def get_db():
    conn = sqlite3.connect('progress.db')
    conn.execute('CREATE TABLE IF NOT EXISTS users (user_id TEXT PRIMARY KEY, data TEXT)')
    return conn

# Professional Sidebar
st.sidebar.title("SMU Training Program")
st.sidebar.markdown("**Evidence-Based Digital Wellness**")
user_id = st.sidebar.text_input("Participant ID")
page = st.sidebar.radio("Session", ["📊 Dashboard", "Day 1: Awareness", "Day 2: Intervention", "Day 3: Maintenance"])

if user_id:
    conn = get_db()
    
    def load_data(uid):
        c = conn.cursor()
        c.execute("SELECT data FROM users WHERE user_id=?", (uid,))
        row = c.fetchone()
        return json.loads(row[0]) if row else {'progress':0, 'logs':[], 'assessments':[]}
    
    def save_data(uid, data):
        conn.execute("REPLACE INTO users VALUES (?, ?)", (uid, json.dumps(data)))
        conn.commit()
    
    data = load_data(user_id)

# 📊 DASHBOARD - Professional Metrics
if page == "📊 Dashboard":
    st.title("Social Media Usage Training")
    st.markdown("**14-Day Intervention Program** *Action Regulation Theory*")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1: st.metric("Days Completed", data['progress'])
    with col2:
        df = pd.DataFrame(data['logs'])
        avg_time = df['duration'].mean() if not df.empty else 0
        st.metric("Avg Daily Usage", f"{avg_time:.0f} min")
    with col3: st.metric("Progress", f"{data['progress']/3*100:.0f}%")
    with col4: st.metric("Sessions", len(data['logs']))
    
    if data['logs']:
        df = pd.DataFrame(data['logs'])
        fig = px.line(df, x='date', y='duration', title="Daily SMU Trend (Target: ↓ Trend)",
                     color_discrete_sequence=['#1f77b4'])
        st.plotly_chart(fig, use_container_width=True)[file:3]
    
    st.markdown("**Next Action**: Continue daily tracking")

# DAY 1: Awareness (Research Heavy)
elif page == "Day 1: Awareness":
    st.header("Day 1: Psychoeducation & Self-Monitoring")
    st.markdown("""
    **Session Objectives** (60-90 min):
    1. Understand SMU mechanisms (dopamine, variable rewards)
    2. Recognize personal patterns & consequences
    
    **Evidence**:
    - Daily usage: 240+ min teens (Pew 2024)[file:3]
    - Harms: Anxiety ↑33%, attention ↓, sleep disruption
    - Models: I-PACE, Self-Regulation Failure (Baumeister)[file:1]
    """)
    
    with st.form("day1_form"):
        col1, col2, col3 = st.columns(3)
        with col1: apps = st.multiselect("Primary Platforms", ["Instagram", "TikTok", "Snapchat", "X/Twitter"])
        with col2: duration = st.number_input("Daily Duration (min)", min_value=0, value=60)
        with col3: trigger = st.text_input("Primary Trigger")
        submitted = st.form_submit_button("Complete Day 1 Tracking", use_container_width=True)
    
    if submitted:
        data['progress'] += 1
        data['logs'].append({'date':str(date.today()), 'apps':apps, 'duration':duration, 'trigger':trigger})
        save_data(user_id, data)
        st.success("✅ Day 1 completed. Data saved to your profile.")
        st.rerun()

# DAY 2: Intervention Strategies
elif page == "Day 2: Intervention":
    st.header("Day 2: Behavioral & Environmental Strategies")
    st.markdown("""
    **Core Techniques**:
    - **Urge Surfing**: Peak passes naturally (10min delay)
    - **Implementation Intentions**: "IF bored, THEN walk 5min"
    - **Digital Hygiene**:
      • Remove apps from home screen
      • Notifications OFF (non-essential)
      • Screen-free zones (bedroom, meals)
      • 1hr daily phone-free periods[file:1]
    """)
    
    col1, col2 = st.columns(2)
    with col1:
        st.info("**Homework**: Implement 3 strategies today")
    with col2:
        if st.button("Mark Day 2 Complete", use_container_width=True) and data['progress'] >=1:
            data['progress'] += 1
            save_data(user_id, data)
            st.success("✅ Day 2 logged")

# DAY 3: Maintenance
elif page == "Day 3: Maintenance":
    st.header("Day 3: Relapse Prevention & Sustainability")
    st.markdown("""
    **Long-Term Systems**:
    - **Personal Usage Rules**: Specific, measurable (e.g., "30min evenings max")
    - **Early Warning Signs**: Boredom → Auto-scroll
    - **Lapse vs Relapse**: Single slip ≠ failure
    - **Social Support**: Share rules with accountability partner[file:1]
    
    **Expected Outcomes**:
    - Screen time ↓50%
    - Focus ↑, Procrastination ↓
    - Life satisfaction ↑[file:3]
    """)
    
    if st.button("Complete Program", use_container_width=True) and data['progress'] >=2:
        data['progress'] = 3
        save_data(user_id, data)
        st.success("🎯 **Program Complete!** Review your dashboard metrics.")

st.markdown("---")
with st.expander("Research Basis"):
    st.markdown("**Action Regulation Theory** - Goal-directed self-regulation cycles[file:2]")
