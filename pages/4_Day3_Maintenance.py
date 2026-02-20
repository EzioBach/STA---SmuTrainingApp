import streamlit as st
import sqlite3

st.header("Day 3: Sustainability Plan")

st.markdown("""
**Create Your Rules**:
1. Define acceptable usage windows
2. Early warning signs
3. Accountability partner[file:1]
""")

user_id = st.text_input("ID")
rules = st.text_area("My 3 Personal Rules")
if st.button("Finalize Program"):
    conn = sqlite3.connect('data.db')
    c = conn.cursor()
    c.execute("UPDATE users SET progress=3 WHERE id=?", (user_id,))
    conn.commit()
    st.balloons()
    st.success("Program Complete!")
