import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
import json
from datetime import date

st.set_page_config(layout="wide", page_icon="📱")

@st.cache_resource
def init_db():
    conn = sqlite3.connect('users.db')
    conn.execute("CREATE TABLE IF NOT EXISTS progress (id TEXT PRIMARY KEY, data TEXT)")
    return conn

# Navigation tabs
tab1, tab2, tab3, tab4 = st.tabs(["📊 Dashboard", "Day 1", "Day 2", "Day 3"])

user_id = st.sidebar.text_input("Your ID")

if user_id:
    conn = init_db()
    
    def get_data():
        c = conn.cursor()
        c.execute("SELECT data FROM progress WHERE id=?", (user_id,))
        row = c.fetchone()
        return json.loads(row[0]) if row else {"progress": 0, "logs": []}
    
    def save_data(data):
        conn.execute("REPLACE INTO progress VALUES (?, ?)", (user_id, json.dumps(data)))
        conn.commit()
    
    data = get_data()

with tab1:
    st.header("Dashboard")
    col1, col2, col3 = st.columns(3)
    col1.metric("Days", data["progress"])
    if data["logs"]:
        df = pd.DataFrame(data["logs"])
        col2.metric("Avg Usage", f"{df['duration'].mean():.0f} min")
        col3.metric("Progress", f"{data['progress']/3*100:.0f}%")
        
        fig = px.line(df, x="date", y="duration", title="Usage Trend")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Complete Day 1 to see charts")

with tab2:
    st.header("Day 1 - Awareness")
    st.write("Track your baseline usage")
    
    apps = st.multiselect("Platforms", ["Instagram", "TikTok", "Snapchat", "X"])
    duration = st.slider("Minutes used", 0, 600, 60)
    trigger = st.text_input("Main trigger")
    
    if st.button("Save Day 1"):
        new_data = data.copy()
        new_data["progress"] = 1
        new_data["logs"].append({"date": str(date.today()), "duration": duration, "apps": apps})
        save_data(new_data)
        st.success("Saved!")
        st.rerun()

with tab3:
    st.header("Day 2 - Strategies")
    st.write("Digital hygiene checklist")
    
    col1, col2, col3 = st.columns(3)
    t1 = col1.checkbox("App limits")
    t2 = col2.checkbox("Notifications off")
    t3 = col3.checkbox("Screen-free zone")
    
    if st.button("Complete Day 2") and data["progress"] >= 1 and sum([t1,t2,t3]) >= 2:
        new_data = data.copy()
        new_data["progress"] = 2
        save_data(new_data)
        st.success("Day 2 complete!")

with tab4:
    st.header("Day 3 - Maintenance")
    st.write("Your sustainability plan")
    
    rules = st.text_area("3 Personal Rules")
    if st.button("Finish Program") and data["progress"] >= 2:
        new_data = data.copy()
        new_data["progress"] = 3
        save_data(new_data)
        st.success("Program complete! Check dashboard.")
        st.balloons()
