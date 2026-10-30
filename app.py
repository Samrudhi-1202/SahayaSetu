import sqlite3
from datetime import datetime
from pathlib import Path

import streamlit as st

st.set_page_config(page_title="SahayaSetu | ಸಹಾಯಸೇತು", page_icon="🤝", layout="wide")
DB_PATH = Path(__file__).with_name("sahayasetu.db")

PHRASES = {
    "Hospital / ಆಸ್ಪತ್ರೆ": [
        ("I need a doctor.", "ನನಗೆ ವೈದ್ಯರು ಬೇಕು."),
        ("Where is the hospital?", "ಆಸ್ಪತ್ರೆ ಎಲ್ಲಿದೆ?"),
        ("I need help.", "ನನಗೆ ಸಹಾಯ ಬೇಕು."),
    ],
    "Transport / ಸಾರಿಗೆ": [
        ("Where is the bus stop?", "ಬಸ್ ನಿಲ್ದಾಣ ಎಲ್ಲಿದೆ?"),
        ("How much is the ticket?", "ಟಿಕೆಟ್ ದರ ಎಷ್ಟು?"),
        ("Does this bus go to Mysuru?", "ಈ ಬಸ್ ಮೈಸೂರಿಗೆ ಹೋಗುತ್ತದೆಯೇ?"),
    ],
    "Shopping / ಖರೀದಿ": [
        ("How much does this cost?", "ಇದರ ಬೆಲೆ ಎಷ್ಟು?"),
        ("Please give me a bill.", "ದಯವಿಟ್ಟು ಬಿಲ್ ಕೊಡಿ."),
        ("Do you have drinking water?", "ಕುಡಿಯುವ ನೀರು ಇದೆಯೇ?"),
    ],
    "Education / ಶಿಕ್ಷಣ": [
        ("Where is the classroom?", "ತರಗತಿ ಕೊಠಡಿ ಎಲ್ಲಿದೆ?"),
        ("Please explain once more.", "ದಯವಿಟ್ಟು ಮತ್ತೊಮ್ಮೆ ವಿವರಿಸಿ."),
        ("When is the exam?", "ಪರೀಕ್ಷೆ ಯಾವಾಗ?"),
    ],
    "Workplace / ಕೆಲಸದ ಸ್ಥಳ": [
        ("When does the meeting start?", "ಸಭೆ ಯಾವಾಗ ಪ್ರಾರಂಭವಾಗುತ್ತದೆ?"),
        ("I have a question.", "ನನಗೆ ಒಂದು ಪ್ರಶ್ನೆ ಇದೆ."),
        ("Thank you for your help.", "ನಿಮ್ಮ ಸಹಾಯಕ್ಕೆ ಧನ್ಯವಾದಗಳು."),
    ],
}

TRANSLATIONS = {
    "English": {
        "home": "Home", "learn": "Learn Kannada", "request": "Request Help",
        "volunteer": "Volunteer", "board": "Help Board", "welcome": "Connecting Kannada learning with community support",
    },
    "ಕನ್ನಡ": {
        "home": "ಮುಖಪುಟ", "learn": "ಕನ್ನಡ ಕಲಿಯಿರಿ", "request": "ಸಹಾಯ ಕೇಳಿ",
        "volunteer": "ಸ್ವಯಂಸೇವಕರು", "board": "ಸಹಾಯ ಪಟ್ಟಿ", "welcome": "ಕನ್ನಡ ಕಲಿಕೆ ಮತ್ತು ಸಮುದಾಯ ಸಹಾಯವನ್ನು ಸಂಪರ್ಕಿಸುವ ವೇದಿಕೆ",
    },
}


def connect():
    return sqlite3.connect(DB_PATH, timeout=10)


def init_db():
    with connect() as conn:
        conn.execute("""CREATE TABLE IF NOT EXISTS requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL, area TEXT NOT NULL, category TEXT NOT NULL,
            details TEXT NOT NULL, status TEXT NOT NULL DEFAULT 'Open',
            created_at TEXT NOT NULL)""")
        conn.execute("""CREATE TABLE IF NOT EXISTS volunteers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL, area TEXT NOT NULL, skills TEXT NOT NULL,
            created_at TEXT NOT NULL)""")


def get_count(table):
    with connect() as conn:
        return conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]



def get_requests():
    with connect() as conn:
        cursor = conn.execute(
    "SELECT id, area, category, details, status, created_at "
    "FROM requests ORDER BY id DESC"
)
        columns = [item[0] for item in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]


def count_matching_volunteers(request):
    area_text = request["area"].strip().casefold()
    category_text = request["category"].split("/")[0].strip().casefold()

    skill_map = {
        "language help": "kannada conversation",
        "government services": "forms and public services",
        "transport": "transport guidance",
        "education": "education",
        "other": None,
    }

    required_skill = skill_map.get(category_text)

    with connect() as conn:
        volunteers = conn.execute(
            "SELECT area, skills FROM volunteers"
        ).fetchall()

    matches = 0

    for volunteer_area, volunteer_skills in volunteers:
        same_area = volunteer_area.strip().casefold() == area_text

        skills = [
            skill.strip().casefold()
            for skill in volunteer_skills.split(",")
        ]

        skill_matches = (
            required_skill is None
            or required_skill in skills
        )

        if same_area and skill_matches:
            matches += 1

    return matches


init_db()


st.markdown("""<style>
.block-container {padding-top: 1.7rem; max-width: 1100px;}
.hero {background: linear-gradient(110deg,#153b50,#216b78); padding: 28px 32px;
 border-radius: 20px; color: white; margin-bottom: 20px;}
.hero h1 {color:white; margin:0; font-size:2.3rem;}
.hero p {color:#e6f5f6; font-size:1.06rem; margin-bottom:0;}
.note {background:#f1f7f8; border-left:4px solid #237889; padding:14px;
 border-radius:8px; color:#1b3440;}
</style>""", unsafe_allow_html=True)

language = st.sidebar.selectbox("Language / ಭಾಷೆ", ["English", "ಕನ್ನಡ"])
t = TRANSLATIONS[language]
page_keys = ["home", "learn", "request", "volunteer", "board"]
page = st.sidebar.radio("Navigation / ನ್ಯಾವಿಗೇಶನ್", page_keys, format_func=lambda k: t[k])
st.sidebar.caption("Hackathon prototype • Data stored locally")

st.markdown(f'<div class="hero"><h1>🤝 SahayaSetu | ಸಹಾಯಸೇತು</h1><p>{t["welcome"]}</p></div>', unsafe_allow_html=True)

if page == "home":
    st.subheader("A bridge for everyday Kannada / ದೈನಂದಿನ ಕನ್ನಡಕ್ಕೆ ಸೇತು")
    a, b, c = st.columns(3)
    a.metric("Kannada phrases", sum(len(v) for v in PHRASES.values()))
    b.metric("Help requests", get_count("requests"))
    c.metric("Registered volunteers", get_count("volunteers"))
    st.markdown("""<div class="note">Learn useful Kannada for hospitals, buses, shops, schools and workplaces.
    When language alone is not enough, request community assistance.</div>""", unsafe_allow_html=True)
    st.write("### How it works")
    st.write("**1. Learn** a useful phrase → **2. Request** help if needed → **3. Connect** with a volunteer.")
    st.info("Demo application: Volunteer identities are not verified. Do not post sensitive personal information or rely on this service for emergencies.")

elif page == "learn":
    st.subheader("Everyday Kannada / ದೈನಂದಿನ ಕನ್ನಡ")
    category = st.selectbox("Choose a situation / ಸಂದರ್ಭ ಆಯ್ಕೆಮಾಡಿ", list(PHRASES))
    for english, kannada in PHRASES[category]:
        with st.container(border=True):
            st.markdown(f"### {kannada}")
            st.write(english)
    st.caption("Practice these phrases aloud. Audio pronunciation can be added in a future version.")

elif page == "request":
    st.subheader("Request assistance / ಸಹಾಯಕ್ಕಾಗಿ ವಿನಂತಿ")
    with st.form("request_form", clear_on_submit=True):
        name = st.text_input("Name / ಹೆಸರು", max_chars=60)
        area = st.text_input("Area (not full address) / ಪ್ರದೇಶ", max_chars=80)
        category = st.selectbox("Help category / ಸಹಾಯದ ಪ್ರಕಾರ", [
            "Language help / ಭಾಷಾ ಸಹಾಯ", "Government services / ಸರ್ಕಾರಿ ಸೇವೆಗಳು",
            "Transport / ಸಾರಿಗೆ", "Education / ಶಿಕ್ಷಣ", "Other / ಇತರೆ"])
        details = st.text_area("Describe your request / ವಿನಂತಿ ವಿವರಿಸಿ", max_chars=500)
        submitted = st.form_submit_button("Submit request / ವಿನಂತಿ ಸಲ್ಲಿಸಿ", type="primary")
    if submitted:
        if not all(x.strip() for x in (name, area, details)):
            st.error("Please fill all fields / ದಯವಿಟ್ಟು ಎಲ್ಲಾ ವಿವರಗಳನ್ನು ಭರ್ತಿ ಮಾಡಿ")
        else:
            with connect() as conn:
                conn.execute("INSERT INTO requests (name,area,category,details,created_at) VALUES (?,?,?,?,?)",
                             (name.strip(), area.strip(), category, details.strip(), datetime.now().isoformat(timespec="seconds")))
            st.success("Request saved successfully! / ವಿನಂತಿ ಯಶಸ್ವಿಯಾಗಿ ಉಳಿಸಲಾಗಿದೆ!")

elif page == "volunteer":
    st.subheader("Volunteer registration / ಸ್ವಯಂಸೇವಕರ ನೋಂದಣಿ")
    with st.form("volunteer_form", clear_on_submit=True):
        name = st.text_input("Name / ಹೆಸರು", max_chars=60)
        area = st.text_input("Area / ಪ್ರದೇಶ", max_chars=80)
        skills = st.multiselect("Ways you can help / ಸಹಾಯದ ವಿಧಗಳು", [
            "Kannada conversation", "Forms and public services", "Education", "Transport guidance", "Digital literacy"])
        submitted = st.form_submit_button("Register / ನೋಂದಾಯಿಸಿ", type="primary")
    if submitted:
        if not name.strip() or not area.strip() or not skills:
            st.error("Enter your name, area and at least one skill.")
        else:
            with connect() as conn:
                conn.execute("INSERT INTO volunteers (name,area,skills,created_at) VALUES (?,?,?,?)",
                             (name.strip(), area.strip(), ", ".join(skills), datetime.now().isoformat(timespec="seconds")))
            st.success("Volunteer registered! / ನೋಂದಣಿ ಯಶಸ್ವಿಯಾಗಿದೆ!")
    st.warning("Registration is for demonstration only. It does not constitute identity verification.")


elif page == "board":
    st.subheader("Community help board / ಸಮುದಾಯ ಸಹಾಯ ಪಟ್ಟಿ")
    requests = get_requests()

    if not requests:
        st.info("No requests yet. Submit a sample request to try the workflow.")
    else:
        matching_counts = {
            request["id"]: count_matching_volunteers(request)
            for request in requests
        }

        selected_status = st.selectbox(
            "Filter status",
            ["All", "Open", "In progress", "Completed"]
        )

        shown = (
            requests if selected_status == "All"
            else [r for r in requests if r["status"] == selected_status]
        )

        if shown:
            for request in shown:
                with st.container(border=True):
                    st.write(f"**Request ID:** {request['id']}")
                    st.write(f"**Category:** {request['category']}")
                    st.write(f"**Area:** {request['area']}")
                    st.write(f"**Request:** {request['details']}")
                    st.write(f"**Status:** {request['status']}")

                    count = matching_counts[request["id"]]
                    if request["status"] == "Open":
                        if count > 0:
                            st.success("A suitable volunteer is available.")
                        else:
                            st.info("No matching volunteer is available yet.")

        else:
            st.info("No requests match this status.")


        st.caption(
            "Prototype only: No authentication yet. "
            "Do not use this public board with real personal information."
        )
