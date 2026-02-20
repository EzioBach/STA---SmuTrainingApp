import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
import json
import smtplib
from datetime import date
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def get_db():
    conn = sqlite3.connect('users.db', check_same_thread=False)
    conn.execute("CREATE TABLE IF NOT EXISTS t (id TEXT PRIMARY KEY, data TEXT)")
    return conn

conn = get_db()

def load(uid):
    c = conn.cursor()
    c.execute("SELECT data FROM t WHERE id=?", (uid,))
    row = c.fetchone()
    return json.loads(row[0]) if row else {
        "progress": 0, "logs": [],
        "pretest": {}, "posttest": {},
        "homework": {}, "diary": []
    }

def save(uid, d):
    conn.execute("REPLACE INTO t VALUES (?, ?)", (uid, json.dumps(d)))
    conn.commit()

def send_email(user_id, data):
    try:
        sender = st.secrets["EMAIL_ADDRESS"]
        password = st.secrets["EMAIL_PASSWORD"]
        receiver = st.secrets["RECEIVER_EMAIL"]
        logs_df = pd.DataFrame(data["logs"]) if data["logs"] else pd.DataFrame()
        body = "SMU Training Report\n====================\n"
        body += "Participant: " + user_id + "\n"
        body += "Days Completed: " + str(data["progress"]) + "\n\n"
        body += "PRE-TEST:\n" + json.dumps(data.get("pretest", {}), indent=2) + "\n\n"
        body += "POST-TEST:\n" + json.dumps(data.get("posttest", {}), indent=2) + "\n\n"
        body += "USAGE LOGS:\n" + (logs_df.to_string() if not logs_df.empty else "None")
        body += "\n\nTRIGGER DIARY:\n" + json.dumps(data.get("diary", []), indent=2)
        msg = MIMEMultipart()
        msg["From"] = sender
        msg["To"] = receiver
        msg["Subject"] = "SMU Report - " + user_id
        msg.attach(MIMEText(body, "plain"))
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender, password)
            server.send_message(msg)
        return True
    except Exception as e:
        st.error(str(e))
        return False

st.set_page_config(page_title="SMU Training", layout="wide")
st.sidebar.title("SMU Training Program")
st.sidebar.caption("14-day evidence-based program")
user_id = st.sidebar.text_input("Your Participant ID")

DEFAULT = {"progress": 0, "logs": [], "pretest": {}, "posttest": {}, "homework": {}, "diary": []}
data = load(user_id) if user_id else DEFAULT

tab0, tab1, tab2, tab3, tab4 = st.tabs([
    "Pre-Assessment", "Day 1 - Awareness", "Day 2 - Strategies", "Day 3 - Maintenance", "Dashboard"
])

# ─── PRE-ASSESSMENT ────────────────────────────────────────────────────────────
with tab0:
    st.header("Pre-Training Assessment")
    st.write("Answer honestly before starting. This is your baseline.")
    if not user_id:
        st.warning("Enter your Participant ID in the sidebar first.")
    else:
        with st.form("pretest_form"):
            st.subheader("Your Current Social Media Use")
            q1 = st.slider("How many minutes/day do you spend on SM (non-work)?", 0, 600, 120)
            q2 = st.slider("How many times are you distracted by your phone daily?", 0, 50, 10)
            q3 = st.select_slider("How satisfied are you with your life?", options=[1,2,3,4,5,6,7,8,9,10], value=5)
            q4 = st.select_slider("How good is your sleep quality?", options=[1,2,3,4,5], value=3)
            q5 = st.selectbox("How do you deal with urges to use SM?", [
                "I always give in", "I sometimes resist", "I often resist", "I rarely feel urges"
            ])
            q6 = st.select_slider("Self-esteem (1=very low, 10=very high)", options=list(range(1,11)), value=5)
            q7 = st.slider("How much spare time do you have daily (hours)?", 0, 12, 4)
            submitted = st.form_submit_button("Save Pre-Assessment", use_container_width=True)
        if submitted:
            d = load(user_id)
            d["pretest"] = {
                "sm_minutes": q1, "distractions": q2, "life_satisfaction": q3,
                "sleep": q4, "urge_coping": q5, "self_esteem": q6, "spare_time": q7
            }
            save(user_id, d)
            data.update(d)
            st.success("Pre-assessment saved!
