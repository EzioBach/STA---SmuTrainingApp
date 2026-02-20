import streamlit as st
import pandas as pd
import plotly.express as px
import json
import sqlite3

st.set_page_config(page_title="Dashboard", layout="wide")

@st.cache_resource
def get_db():
    conn = sqlite3.connect('data.db')
    conn.execute('CREATE TABLE IF NOT EXISTS users (id TEXT PRIMARY KEY, data TEXT)')
    return conn

user_id = st.text_input("Participant ID")
if user_id:
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT data FROM users WHERE id=?", (user_id,))
    row = c.fetchone()
    
    if row:
        data = json.loads(row[0])
        logs_df = pd.DataFrame(data['logs']) if data['logs'] else pd.DataFrame()
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Days Completed", data['progress'])
        col2.metric("Avg Usage", f"{logs_df['duration'].mean():.0f}min" if len(logs_df)>0 else "0")
        col3.metric("Progress", f"{data['progress']/3*100:.0f}%")
        
        if len(logs_df)>0:
            fig = px.line(logs_df, x='date', y='duration', title="Daily Usage Trend")
            st.plotly_chart(fig, use_container_width=True)
        
        st.download_button("Export Data", json.dumps(data), f"{user_id}_data.json")
    else:
        st.info("Start with Day 1")
