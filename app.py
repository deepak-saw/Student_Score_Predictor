import streamlit as st
import joblib
import pandas as pd
import json
import os
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(
    page_title="Student Dashboard",
    page_icon="🎓",
    layout="wide"
)

# =========================
# CUSTOM CSS
# =========================
st.markdown("""
<style>

.stApp {
    background: linear-gradient(to right, #141e30, #243b55);
    color: white;
}

.main-title {
    font-size: 45px;
    font-weight: bold;
    text-align: center;
    color: #00ffd5;
}

.card {
    background-color: rgba(255,255,255,0.08);
    padding: 20px;
    border-radius: 20px;
    box-shadow: 0px 0px 15px rgba(0,255,255,0.3);
    margin-bottom: 20px;
}

.metric-card {
    background: linear-gradient(135deg,#00c6ff,#0072ff);
    padding: 20px;
    border-radius: 18px;
    text-align:center;
    color:white;
    font-size:20px;
    font-weight:bold;
}

.sidebar .sidebar-content {
    background: #111827;
}

</style>
""", unsafe_allow_html=True)

# =========================
# USER FILE
# =========================
USER_FILE = "users.json"

if not os.path.exists(USER_FILE):
    with open(USER_FILE, "w") as f:
        json.dump({}, f)

def load_users():
    with open(USER_FILE, "r") as f:
        return json.load(f)

def save_users(users):
    with open(USER_FILE, "w") as f:
        json.dump(users, f)

# =========================
# SESSION STATE
# =========================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "username" not in st.session_state:
    st.session_state.username = ""

# =========================
# LOGIN SYSTEM
# =========================
if not st.session_state.logged_in:

    st.markdown('<p class="main-title">🎓 Student Predictor Portal</p>', unsafe_allow_html=True)

    menu = st.sidebar.selectbox("Menu", ["Login", "Sign Up"])

    users = load_users()

    if menu == "Sign Up":

        st.markdown('<div class="card">', unsafe_allow_html=True)

        st.subheader("📝 Create Account")

        new_user = st.text_input("Username")
        new_pass = st.text_input("Password", type="password")

        if st.button("Create Account"):

            if new_user in users:
                st.error("Username already exists!")

            elif new_user == "" or new_pass == "":
                st.warning("Enter all fields")

            else:
                users[new_user] = new_pass
                save_users(users)
                st.success("Account Created Successfully!")

        st.markdown('</div>', unsafe_allow_html=True)

    else:

        st.markdown('<div class="card">', unsafe_allow_html=True)

        st.subheader("🔐 Login")

        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        if st.button("Login"):

            if username in users and users[username] == password:

                st.session_state.logged_in = True
                st.session_state.username = username
                st.success("Login Successful")
                st.rerun()

            else:
                st.error("Invalid Credentials")

        st.markdown('</div>', unsafe_allow_html=True)

# =========================
# MAIN DASHBOARD
# =========================
else:

    model = joblib.load("student_model.pkl")
    columns = joblib.load("model_columns.pkl")

    # Sidebar
    st.sidebar.image(
        "https://cdn-icons-png.flaticon.com/512/3135/3135755.png",
        width=120
    )

    st.sidebar.success(f"Welcome {st.session_state.username}")

    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()

    # Header
    st.markdown('<p class="main-title">📊 Student Performance Dashboard</p>', unsafe_allow_html=True)

    # Metrics Row
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(
            '<div class="metric-card">📚 AI Powered Prediction</div>',
            unsafe_allow_html=True
        )

    with col2:
        st.markdown(
            '<div class="metric-card">⚡ Real-time Analytics</div>',
            unsafe_allow_html=True
        )

    with col3:
        st.markdown(
            '<div class="metric-card">🎯 Smart Accuracy</div>',
            unsafe_allow_html=True
        )

    st.write("")

    # Input Form
    col1, col2 = st.columns(2)

    with col1:
        hours = st.slider("Hours Studied", 0, 24, 5)
        attendance = st.slider("Attendance %", 0, 100, 75)
        previous = st.slider("Previous Score", 0, 100, 60)
        sleep = st.slider("Sleep Hours", 0, 12, 7)

    with col2:
        motivation = st.selectbox("Motivation", ["Low", "Medium", "High"])
        teacher = st.selectbox("Teacher Quality", ["Poor", "Average", "Good"])
        school = st.selectbox("School Type", ["Public", "Private"])
        internet = st.selectbox("Internet Access", ["Yes", "No"])

    if st.button("🚀 Predict Score"):

        data = {
            "Hours_Studied": hours,
            "Attendance": attendance,
            "Previous_Scores": previous,
            "Sleep_Hours": sleep,
            "Motivation_Level": motivation,
            "Teacher_Quality": teacher,
            "School_Type": school,
            "Internet_Access": internet
        }

        input_df = pd.DataFrame([data])

        input_df = pd.get_dummies(input_df)

        input_df = input_df.reindex(columns=columns, fill_value=0)

        prediction = model.predict(input_df)

        final_score = max(40, min(100, prediction[0]))
        final_score = int(round(final_score))

        # Result Card
        st.markdown(f"""
        <div class="card">
            <h1 style='text-align:center;color:#00ffd5;'>
                🎯 Predicted Score: {final_score}
            </h1>
        </div>
        """, unsafe_allow_html=True)

        # Gauge Chart
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=final_score,
            title={'text': "Performance"},
            gauge={
                'axis': {'range': [0, 100]},
                'bar': {'color': "cyan"},
                'steps': [
                    {'range': [0, 40], 'color': "red"},
                    {'range': [40, 70], 'color': "orange"},
                    {'range': [70, 100], 'color': "green"},
                ],
            }
        ))

        st.plotly_chart(fig, use_container_width=True)

        # Analytics Chart
        chart_data = pd.DataFrame({
            "Features": ["Study", "Attendance", "Previous", "Sleep"],
            "Values": [hours, attendance, previous, sleep]
        })

        bar_fig = px.bar(
            chart_data,
            x="Features",
            y="Values",
            title="Student Analytics"
        )

        st.plotly_chart(bar_fig, use_container_width=True)
