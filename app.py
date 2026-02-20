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
    return json.loads(row[0]) if row else {"progress": 0, "logs": []}

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
        body += "Participant ID: " + user_id + "\n"
        body += "Days Completed: " + str(data["progress"]) + "\n"
        body += "Total Logs: " + str(len(data["logs"])) + "\n\n"
        body += "Log Details:\n"
        body += logs_df.to_string() if not logs_df.empty else "No logs yet"
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

user_id = st.sidebar.text_input("Your ID")
DEFAULT = {"progress": 0, "logs": []}
data = load(user_id) if user_id else DEFAULT

tab1, tab2, tab3, tab4 = st.tabs(["Dashboard", "Day 1", "Day 2", "Day 3"])

with tab1:
    st.header("Dashboard")
    if not user_id:
        st.warning("Enter your ID in the sidebar to start.")
    else:
        col1, col2, col3 = st.columns(3)
        col1.metric("Days Done", data["progress"])
        col2.metric("Progress", str(round(data["progress"] / 3 * 100)) + "%")
        if data["logs"]:
            df = pd.DataFrame(data["logs"])
            col3.metric("Avg Usage", str(round(df["duration"].mean())) + " min")
            fig = px.line(df, x="date", y="duration", title="Daily Usage Trend")
            st.plotly_chart(fig, use_container_width=True)
            st.subheader("All Your Logs")
            st.dataframe(df, use_container_width=True)
            if st.button("Send Report to Email"):
                if send_email(user_id, data):
                    st.success("Report sent!")
                else:
                    st.error("Email failed. Check Streamlit Secrets.")
        else:
            col3.metric("Avg Usage", "0 min")
            st.info("Complete Day 1 to see your data here.")

with tab2:
    st.header("Day 1 - Awareness")
    if not user_id:
        st.warning("Enter your ID first.")
    else:
        st.write("Understand your social media habits and their impact.")
        apps = st.multiselect("Platforms you use most", ["Instagram", "TikTok", "Snapchat", "X", "YouTube"])
        duration = st.slider("Daily usage in minutes", 0, 600, 120)
        trigger = st.text_input("What triggers you to open social media?")
        emotion = st.selectbox("How do you feel after using it?", ["Relaxed", "Anxious", "Empty", "Fine", "Distracted"])
        if st.button("Save Day 1", use_container_width=True):
            d = load(user_id)
            d["progress"] = max(d["progress"], 1)
            d["logs"].append({
                "date": str(date.today()),
                "duration": duration,
                "apps": str(apps),
                "trigger": trigger,
                "emotion": emotion
            })
            save(user_id, d)
            data.update(d)
            st.success("Day 1 saved! Check your Dashboard.")

with tab3:
    st.header("Day 2 - Strategies")
    if not user_id:
        st.warning("Enter your ID first.")
    elif data["progress"] < 1:
        st.warning("Complete Day 1 first.")
    else:
        st.write("Build your digital boundaries.")
        c1, c2 = st.columns(2)
        t1 = c1.checkbox("Set app time limits")
        t2 = c1.checkbox("Remove apps from home screen")
        t3 = c2.checkbox("Turn off notifications")
        t4 = c2.checkbox("Create one screen-free zone")
        duration2 = st.slider("Today's usage in minutes", 0, 600, 90)
        if st.button("Save Day 2", use_container_width=True):
            if sum([t1, t2, t3, t4]) >= 2:
                d = load(user_id)
                d["progress"] = max(d["progress"], 2)
                d["logs"].append({
                    "date": str(date.today()),
                    "duration": duration2,
                    "apps": "",
                    "trigger": "",
                    "emotion": ""
                })
                save(user_id, d)
                data.update(d)
                st.success("Day 2 saved!")
            else:
                st.error("Complete at least 2 tasks first.")

with tab4:
    st.header("Day 3 - Maintenance")
    if not user_id:
        st.warning("Enter your ID first.")
    elif data["progress"] < 2:
        st.warning("Complete Day 2 first.")
    else:
        st.write("Build long-term habits and prevent relapse.")
        rules = st.text_area("Write your 3 personal social media rules")
        warning_signs = st.text_input("Your early warning signs of relapse")
        duration3 = st.slider("Today's usage in minutes", 0, 600, 60)
        if st.button("Complete Program", use_container_width=True):
            if rules:
                d = load(user_id)
                d["progress"] = 3
                d["logs"].append({
                    "date": str(date.today()),
                    "duration": duration3,
                    "apps": "",
                    "trigger": warning_signs,
                    "emotion": ""
                })
                save(user_id, d)
                st.success("Program complete! Check your Dashboard.")
                st.balloons()
            else:
                st.error("Write your personal rules first.")
