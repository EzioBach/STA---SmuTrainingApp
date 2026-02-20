import streamlit as st
import sqlite3
import json
from datetime import date

st.header("Day 1: Awareness & Baseline")

st.markdown("""
**Objectives**:
- Establish baseline usage
- Identify triggers & patterns[file:1]
""")

user_id = st.text_input("ID")
if user_id and st.button("Save Baseline", key="day1"):
    conn = sqlite3.connect('data.db')
    c = conn.cursor()
    c.execute("SELECT data FROM users WHERE id=?", (user_id,))
    row = c.fetchone()
    
    data = json.loads(row[0]) if row else {'progress':0, 'logs':[]}
    data['progress'] = 1
    data['logs'].append({
        'date': str(date.today()),
        'apps': st.session_state.get('apps', []),
        'duration': st.session_state.get('duration', 0),
        'trigger': st.session_state.get('trigger', '')
    })
    
    conn.execute("REPLACE INTO users VALUES (?, ?)", (user_id, json.dumps(data)))
    conn.commit()
    st.success("Day 1 Saved!")
    
apps = st.multiselect("Platforms", ["Instagram", "TikTok", "Snapchat", "X"], key="apps")
duration = st.slider("Total Usage (min)", 0, 720, 60, key="duration")
trigger = st.text_input("Primary Trigger", key="trigger")
