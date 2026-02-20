import streamlit as st
import sqlite3
import json

st.header("Day 2: Intervention Strategies")

st.markdown("""
**Implementation**:
- Remove apps from home screen
- Disable non-essential notifications
- Establish screen-free zones[file:1]
""")

user_id = st.text_input("ID")
checkboxes = st.columns(3)
task1 = checkboxes[0].checkbox("App limits set")
task2 = checkboxes[1].checkbox("Notifications off")
task3 = checkboxes[2].checkbox("Screen-free zone")

if st.button("Complete Day 2") and sum([task1,task2,task3]) >=2:
    conn = sqlite3.connect('data.db')
    c = conn.cursor()
    c.execute("UPDATE users SET progress=2 WHERE id=?", (user_id,))
    conn.commit()
    st.success("Day 2 Complete!")
