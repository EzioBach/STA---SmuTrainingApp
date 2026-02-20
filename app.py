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
    return json.loads(row[0]) if row else {"progress": 0, "logs": [], "pretest": {}, "day2_logs": [], "day3": {}}

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
        if data.get("pretest"):
            body += "PRE-TEST ANSWERS:\n"
            for k, v in data["pretest"].items():
                body += k + ": " + str(v) + "\n"
            body += "\n"
        body += "USAGE LOGS:\n"
        body += logs_df.to_string() if not logs_df.empty else "No logs"
        if data.get("day3"):
            body += "\n\nDAY 3 PERSONAL RULES:\n" + str(data["day3"].get("rules", ""))
            body += "\nWARNING SIGNS: " + str(data["day3"].get("warning_signs", ""))
            body += "\nRECOVERY PLAN: " + str(data["day3"].get("recovery_plan", ""))
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
st.sidebar.caption(f"Course: {COURSE_NAME}")
st.sidebar.caption("Facilitators: " + ", ".join(FACILITATORS))
st.sidebar.caption("14-day evidence-based digital wellness program")
user_id = st.sidebar.text_input("Participant ID")
DEFAULT = {"progress": 0, "logs": [], "pretest": {}, "day2_logs": [], "day3": {}}
data = load(user_id) if user_id else DEFAULT
COURSE_NAME = "YOUR COURSE NAME HERE"
MODULE_NAME = "Social Media Usage Training"
AFFILIATION = "Your university / program (optional)"
FACILITATORS = [
    "Name 1",
    "Name 2",
    "Name 3",
    "Name 4",
]


tab0, tab1, tab2, tab3, tab4 = st.tabs(["Overview", "Dashboard", "Day 1", "Day 2", "Day 3"])

# ── OVERVIEW ──────────────────────────────────────────
with tab0:
    st.header("Social Media Usage Training")
    st.subheader(MODULE_NAME)
    st.caption(f"Course: {COURSE_NAME}")
    if AFFILIATION.strip():
        st.caption(f"Affiliation: {AFFILIATION}")
        
    st.markdown("**Facilitators**")
    st.write(", ".join(FACILITATORS))
    st.markdown("---")

    st.markdown("**Target:** Young adults and students with problematic social media use")
    st.markdown("**Duration:** 14 days — 3 online sessions + individual work")
    st.markdown("**Theory:** Action Regulation Theory — moving from automatic to intentional behavior")

    st.subheader("Why This Matters")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.error("Emotional Impact")
        st.write("Anxiety, stress, emotional exhaustion, low well-being")
    with col2:
        st.warning("Cognitive Impact")
        st.write("Attention deficit, FOMO, cognitive decline, memory issues")
    with col3:
        st.info("Behavioral Impact")
        st.write("Sleep disruption, procrastination, diminished performance")

    st.subheader("Program Goal")
    st.success("Move from uncontrolled, excessive SMU → intentional, reduced, disciplined usage")

    st.subheader("What You Will Achieve")
    goals = [
        "Screen time reduced to 1-2 hrs/day leisure",
        "Fewer distractions during daily tasks",
        "Better sleep quality",
        "Stronger ability to resist urges",
        "Higher life satisfaction",
        "Better self-esteem and emotional coping"
    ]
    for g in goals:
        st.markdown("- " + g)

# ── DASHBOARD ─────────────────────────────────────────
with tab1:
    st.header("Dashboard")
    if not user_id:
        st.warning("Enter your Participant ID in the sidebar.")
    else:
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Days Done", data["progress"])
        col2.metric("Progress", str(round(data["progress"] / 3 * 100)) + "%")
        if data["logs"]:
            df = pd.DataFrame(data["logs"])
            col3.metric("Avg Usage", str(round(df["duration"].mean())) + " min")
            col4.metric("Sessions Logged", len(data["logs"]))
            fig = px.line(df, x="date", y="duration", title="Daily SMU Trend — Target: Decreasing")
            st.plotly_chart(fig, use_container_width=True)
            st.subheader("Full Log")
            df["apps"] = df["apps"].apply(lambda x: ", ".join(x) if isinstance(x, list) else str(x))
            st.dataframe(df, use_container_width=True)
            st.download_button("Download CSV", df.to_csv(index=False), "smu_data.csv")
            if st.button("Send Full Report to Email"):
                if send_email(user_id, data):
                    st.success("Report sent!")
                else:
                    st.error("Check Streamlit Secrets settings.")
        else:
            col3.metric("Avg Usage", "0 min")
            col4.metric("Sessions Logged", 0)
            st.info("Complete Day 1 to see your data here.")

# ── DAY 1 ─────────────────────────────────────────────
with tab2:
    st.header("Day 1 — Psychoeducation & Awareness")
    st.caption("Session duration: 60-90 min")
    if not user_id:
        st.warning("Enter your ID first.")
    else:
        with st.expander("What is SMU and PSMU?", expanded=False):
            st.markdown("""
**SMU** = Social Media Usage. **PSMU** = Problematic SMU — a self-regulation issue, NOT a willpower problem.

**Why is social media addictive?**
- Dopamine release + variable rewards (like a slot machine)
- Every like, comment, notification = unpredictable reward

**Key Models explaining PSMU:**
- **I-PACE Model** — Interaction of Person, Affect, Cognition, Execution
- **Self-Regulation Failure** (Baumeister) — goal pursuit breaks down under stress
- **Dual-Process Model** (Kahneman) — automatic (fast) vs deliberate (slow) thinking
- **Action Regulation Theory** (Hacker) — behavior regulated by goal-setting and monitoring
- **Classical & Operant Conditioning** — habitual triggers reinforced over time

**Harms:** Attention deficit, sleep disruption, anxiety, low self-esteem, FOMO, body image concerns
            """)

        st.subheader("Pre-Test Assessment")
        st.caption("Baseline — to compare with your results after Day 3")
        pre_col1, pre_col2 = st.columns(2)
        with pre_col1:
            pre_screen = st.number_input("Daily SM time (leisure, min)", 0, 1440, 120, key="pre_screen")
            pre_distract = st.number_input("Times distracted by phone today", 0, 100, 10, key="pre_distract")
            pre_sleep = st.slider("Sleep quality (1=poor, 10=great)", 1, 10, 5, key="pre_sleep")
            pre_life = st.slider("Life satisfaction (1=low, 10=high)", 1, 10, 5, key="pre_life")
        with pre_col2:
            pre_focus = st.selectbox("Can you resist SM urges?", ["Never", "Rarely", "Sometimes", "Often", "Always"], key="pre_focus")
            pre_cope = st.text_input("How do you deal with urges to use SM?", key="pre_cope")
            pre_spare = st.number_input("Spare time per day (min)", 0, 1440, 120, key="pre_spare")
            pre_goal = st.number_input("Desired SM time per day (min)", 0, 600, 60, key="pre_goal")

        st.subheader("Usage Tracker — Homework")
        apps = st.multiselect("Platforms used most", ["Instagram", "TikTok", "Snapchat", "X", "YouTube", "Reddit", "LinkedIn"])
        duration = st.slider("Total daily usage (min)", 0, 600, 120)
        reasons = st.multiselect("Why do you use SM?", ["Boredom", "FOMO", "Relaxation", "Validation/Likes", "Social connection", "Habit", "Work/Study"])
        trigger = st.text_input("Main trigger (when/where do you use it most?)")
        emotion_before = st.selectbox("How do you feel BEFORE opening SM?", ["Bored", "Anxious", "Lonely", "Fine", "Stressed", "Curious"])
        emotion_after = st.selectbox("How do you feel AFTER using SM?", ["Relaxed", "Anxious", "Empty", "Fine", "Distracted", "Guilty"])
        consequences = st.multiselect("Consequences you notice personally", ["Less sleep", "Less focus", "Anxiety", "Wasted time", "Comparison", "Procrastination"])

        st.subheader("Trigger Diary")
        trigger_when = st.text_input("When did you use SM today? (situation)")
        trigger_why = st.text_input("Why did you open it?")
        trigger_felt = st.text_area("How did it feel during and after?")

        if st.button("Save Day 1", use_container_width=True):
            d = load(user_id)
            d["progress"] = max(d["progress"], 1)
            d["pretest"] = {
                "daily_sm_min": pre_screen, "distractions": pre_distract,
                "sleep": pre_sleep, "life_satisfaction": pre_life,
                "focus": pre_focus, "coping": pre_cope,
                "spare_time": pre_spare, "goal_time": pre_goal
            }
            d["logs"].append({
                "date": str(date.today()), "duration": duration,
                "apps": str(apps), "trigger": trigger,
                "emotion_before": emotion_before, "emotion_after": emotion_after,
                "reasons": str(reasons), "consequences": str(consequences),
                "trigger_when": trigger_when, "trigger_why": trigger_why,
                "trigger_felt": trigger_felt
            })
            save(user_id, d)
            data.update(d)
            st.success("Day 1 saved! Well done — you took the first step.")

# ── DAY 2 ─────────────────────────────────────────────
with tab3:
    st.header("Day 2 — Triggers, Urges & Strategies")
    st.caption("Session duration: 60-90 min")
    if not user_id:
        st.warning("Enter your ID first.")
    elif data["progress"] < 1:
        st.warning("Complete Day 1 first.")
    else:
        with st.expander("Key Concepts", expanded=False):
            st.markdown("""
**Triggers:**
- Internal: Boredom, FOMO, anxiety, need for validation
- External: Notifications, seeing others on phones, environmental cues

**Urge Curve:**
Urges rise quickly, peak around 10 min, then naturally drop — you don't have to act on them.

**Delay-and-Decide Principle:** Wait 10 minutes before opening SM. Ask yourself:
- "What do I expect from opening this app?"
- "What usually happens after 10 minutes of scrolling?"

**Intentional vs Automatic Use:**
- Automatic = habit-driven, no conscious choice
- Intentional = deliberate, time-limited, purpose-driven

**Emotional Regulation Tools:**
- Emotional tolerance — sit with discomfort without reacting
- If-Then plans — "IF I feel bored, THEN I will go for a walk"
- Cognitive reappraisal — reframe the urge
            """)

        st.subheader("Your If-Then Plan")
        col1, col2 = st.columns(2)
        with col1:
            if_trigger = st.text_input("IF I feel / experience...")
        with col2:
            then_action = st.text_input("THEN I will instead...")

        st.subheader("Socratic Reflection")
        expect = st.text_input("What do I expect from opening this app?")
        after10 = st.text_input("What usually happens after 10 minutes of scrolling?")

        st.subheader("Digital Hygiene Checklist")
        c1, c2 = st.columns(2)
        t1 = c1.checkbox("Set daily time limits on SM apps")
        t2 = c1.checkbox("Remove SM apps from home screen")
        t3 = c1.checkbox("Turn off all non-essential notifications")
        t4 = c2.checkbox("Created a screen-free zone (bedroom/dining)")
        t5 = c2.checkbox("1 hour phone-free before bed")
        t6 = c2.checkbox("Tried grey mode on phone")

        st.subheader("Today's Usage Log")
        duration2 = st.slider("Today's SM usage (min)", 0, 600, 90)
        trigger2 = st.text_input("Main trigger today")
        what_helped = st.text_area("What strategy helped most today?")

        if st.button("Save Day 2", use_container_width=True):
            if sum([t1, t2, t3, t4, t5, t6]) >= 2:
                d = load(user_id)
                d["progress"] = max(d["progress"], 2)
                d["logs"].append({
                    "date": str(date.today()), "duration": duration2,
                    "apps": "", "trigger": trigger2,
                    "emotion_before": "", "emotion_after": "",
                    "reasons": "", "consequences": "",
                    "trigger_when": if_trigger, "trigger_why": then_action,
                    "trigger_felt": what_helped
                })
                save(user_id, d)
                data.update(d)
                st.success("Day 2 saved! Great work applying these strategies.")
            else:
                st.error("Complete at least 2 digital hygiene tasks to proceed.")

# ── DAY 3 ─────────────────────────────────────────────
with tab4:
    st.header("Day 3 — Maintenance & Relapse Prevention")
    st.caption("Session duration: 60-90 min")
    if not user_id:
        st.warning("Enter your ID first.")
    elif data["progress"] < 2:
        st.warning("Complete Day 2 first.")
    else:
        with st.expander("Key Concepts", expanded=False):
            st.markdown("""
**Lapse vs Relapse:**
- Lapse = one slip (normal, expected)
- Relapse = return to old patterns (preventable)
- One bad day does NOT mean failure — self-compassion is key

**Identity & Values Alignment:**
Maintenance is not just behavioral — it's motivational.
Ask: "Who do I want to be? Does this SM habit serve that person?"

**Handling Challenges:**
- Social pressure: It's okay to be present without your phone
- Boredom in social contexts: Reconnect with face-to-face interaction
- Work/study: Define what counts as necessary SM use

**Personal SMU Rules (be specific):**
Define: WHEN, HOW LONG, FOR WHAT PURPOSE
Example: "I use Instagram only after 7pm, max 20 min, to message friends — not to scroll."
            """)

        st.subheader("Reflection")
        what_changed = st.text_area("What changed during this training?")
        what_worked = st.text_area("What worked best for you?")
        what_hardest = st.text_area("What was the hardest part?")

        st.subheader("Your Personal SMU Rules (write 3-5)")
        rules = st.text_area("My rules for social media use (be specific: when, how long, for what purpose)")

        st.subheader("Relapse Prevention Plan")
        warning_signs = st.text_input("3 early warning signs I'm slipping back")
        recovery_plan = st.text_area("If I relapse, I will...")
        support = st.text_input("My accountability partner (name)")

        st.subheader("Post-Test Assessment")
        st.caption("Compare with your Day 1 baseline")
        post_col1, post_col2 = st.columns(2)
        with post_col1:
            post_screen = st.number_input("Daily SM time now (leisure, min)", 0, 1440, 60, key="post_screen")
            post_distract = st.number_input("Times distracted by phone today", 0, 100, 5, key="post_distract")
            post_sleep = st.slider("Sleep quality now (1-10)", 1, 10, 7, key="post_sleep")
            post_life = st.slider("Life satisfaction now (1-10)", 1, 10, 7, key="post_life")
        with post_col2:
            post_focus = st.selectbox("Can you resist SM urges now?", ["Never", "Rarely", "Sometimes", "Often", "Always"], key="post_focus")
            post_cope = st.text_input("How do you deal with urges now?", key="post_cope")
            more_time = st.selectbox("Do you feel you have more time?", ["No", "A little", "Yes", "Definitely"], key="more_time")

        if st.button("Complete Program", use_container_width=True):
            if rules and warning_signs:
                d = load(user_id)
                d["progress"] = 3
                d["day3"] = {
                    "rules": rules, "warning_signs": warning_signs,
                    "recovery_plan": recovery_plan, "support": support,
                    "what_changed": what_changed, "what_worked": what_worked,
                    "what_hardest": what_hardest,
                    "posttest": {
                        "daily_sm_min": post_screen, "distractions": post_distract,
                        "sleep": post_sleep, "life_satisfaction": post_life,
                        "focus": post_focus, "coping": post_cope, "more_time": more_time
                    }
                }
                d["logs"].append({
                    "date": str(date.today()), "duration": post_screen,
                    "apps": "", "trigger": warning_signs,
                    "emotion_before": "", "emotion_after": "",
                    "reasons": "", "consequences": "",
                    "trigger_when": "", "trigger_why": "",
                    "trigger_felt": recovery_plan
                })
                save(user_id, d)
                st.success("Program complete! Review your Dashboard to see your full journey.")
                st.balloons()

                if data.get("pretest"):
                    st.subheader("Your Progress (Pre vs Post)")
                    pre = data["pretest"]
                    metrics = {
                        "SM Usage (min)": [pre.get("daily_sm_min", 0), post_screen],
                        "Distractions": [pre.get("distractions", 0), post_distract],
                        "Sleep Quality": [pre.get("sleep", 0), post_sleep],
                        "Life Satisfaction": [pre.get("life_satisfaction", 0), post_life]
                    }
                    comp_df = pd.DataFrame(metrics, index=["Before", "After"]).T.reset_index()
                    comp_df.columns = ["Metric", "Before", "After"]
                    fig2 = px.bar(comp_df, x="Metric", y=["Before", "After"],
                                 barmode="group", title="Pre vs Post Training Comparison")
                    st.plotly_chart(fig2, use_container_width=True)
            else:
                st.error("Write your personal rules and warning signs to complete.")
