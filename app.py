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
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:wght@300;400;500&display=swap');

*, *::before, *::after { box-sizing: border-box; }

.stApp {
    background: #0a0f1e;
    color: #e8eaf6;
    font-family: 'DM Sans', sans-serif;
}

/* ── Animated grid bg ── */
.stApp::before {
    content: '';
    position: fixed; inset: 0; z-index: 0;
    background-image:
        linear-gradient(rgba(0,255,213,.03) 1px, transparent 1px),
        linear-gradient(90deg, rgba(0,255,213,.03) 1px, transparent 1px);
    background-size: 60px 60px;
    pointer-events: none;
    animation: gridMove 20s linear infinite;
}
@keyframes gridMove { from{background-position:0 0} to{background-position:0 60px} }

/* ── Logo / title ── */
.main-title {
    font-family: 'Syne', sans-serif;
    font-size: 42px; font-weight: 800;
    text-align: center;
    color: #e8eaf6;
    letter-spacing: -1px;
    margin-bottom: 4px;
}
.main-title span { color: #00ffd5; }

.main-sub {
    text-align: center;
    color: #6b7a99;
    font-size: 14px;
    margin-bottom: 32px;
    letter-spacing: 0.4px;
}

.logo-icon-wrap {
    text-align: center;
    margin-bottom: 12px;
}
.logo-icon {
    display: inline-block;
    font-size: 36px;
    background: linear-gradient(135deg, #00ffd5, #0072ff);
    border-radius: 18px;
    padding: 10px 16px;
    box-shadow: 0 0 30px rgba(0,255,213,.3);
    animation: iconPulse 3s ease-in-out infinite;
}
@keyframes iconPulse {
    0%,100%{box-shadow:0 0 30px rgba(0,255,213,.3)}
    50%{box-shadow:0 0 50px rgba(0,255,213,.5)}
}

/* ── Auth card ── */
.auth-card {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.09);
    border-radius: 24px;
    padding: 36px 32px;
    backdrop-filter: blur(20px);
    box-shadow: 0 24px 80px rgba(0,0,0,.6), inset 0 1px 0 rgba(255,255,255,.06);
    position: relative;
    overflow: hidden;
    max-width: 480px;
    margin: 0 auto;
}
.auth-card::before {
    content: '';
    position: absolute; top: 0; left: 0; right: 0; height: 1px;
    background: linear-gradient(90deg, transparent, #00ffd5, transparent);
    opacity: .6;
}

.form-heading {
    font-family: 'Syne', sans-serif;
    font-size: 22px; font-weight: 700; color: #e8eaf6;
    margin-bottom: 4px;
}
.form-sub { font-size: 13px; color: #6b7a99; margin-bottom: 24px; }

/* ── Streamlit input overrides ── */
.stTextInput > div > div > input {
    background: rgba(255,255,255,0.05) !important;
    border: 1px solid rgba(255,255,255,0.09) !important;
    border-radius: 12px !important;
    color: #e8eaf6 !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 15px !important;
    padding: 12px 16px !important;
    transition: all .2s ease !important;
}
.stTextInput > div > div > input:focus {
    border-color: #00ffd5 !important;
    background: rgba(0,255,213,0.06) !important;
    box-shadow: 0 0 0 3px rgba(0,255,213,.08) !important;
}
.stTextInput > label {
    color: #6b7a99 !important;
    font-size: 12px !important;
    font-weight: 500 !important;
    text-transform: uppercase !important;
    letter-spacing: .8px !important;
    font-family: 'DM Sans', sans-serif !important;
}

/* ── Primary button ── */
.stButton > button {
    width: 100% !important;
    background: linear-gradient(135deg, #00ffd5, #0072ff) !important;
    color: #0a0f1e !important;
    font-family: 'Syne', sans-serif !important;
    font-size: 15px !important; font-weight: 700 !important;
    border: none !important;
    border-radius: 14px !important;
    padding: 14px 20px !important;
    letter-spacing: .3px !important;
    box-shadow: 0 8px 30px rgba(0,255,213,.25) !important;
    transition: all .2s ease !important;
    cursor: pointer !important;
}
.stButton > button:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 12px 40px rgba(0,255,213,.35) !important;
}

/* ── Success / error messages ── */
.stSuccess {
    background: rgba(0,255,213,.1) !important;
    border: 1px solid rgba(0,255,213,.3) !important;
    border-radius: 12px !important;
    color: #00ffd5 !important;
}
.stError {
    background: rgba(255,94,122,.1) !important;
    border: 1px solid rgba(255,94,122,.3) !important;
    border-radius: 12px !important;
    color: #ff5e7a !important;
}
.stWarning {
    background: rgba(255,157,58,.1) !important;
    border: 1px solid rgba(255,157,58,.3) !important;
    border-radius: 12px !important;
}

/* ── Selectbox / tab styling ── */
.stSelectbox > div > div {
    background: rgba(255,255,255,0.05) !important;
    border: 1px solid rgba(255,255,255,0.09) !important;
    border-radius: 12px !important;
    color: #e8eaf6 !important;
}

/* ── Dashboard metric cards ── */
.metric-card {
    background: linear-gradient(135deg, #0072ff22, #00ffd522);
    border: 1px solid rgba(0,255,213,.2);
    padding: 22px 20px;
    border-radius: 18px;
    text-align: center;
    color: #e8eaf6;
    font-family: 'Syne', sans-serif;
    font-size: 17px; font-weight: 700;
    box-shadow: 0 8px 30px rgba(0,0,0,.3);
}

/* ── Divider ── */
.auth-divider {
    display: flex; align-items: center; gap: 12px;
    margin: 20px 0;
    font-size: 12px; color: #6b7a99;
}
.auth-divider::before, .auth-divider::after {
    content: ''; flex: 1; height: 1px;
    background: rgba(255,255,255,0.09);
}

/* ── Sidebar ── */
section[data-testid="stSidebar"] {
    background: #0d1424 !important;
    border-right: 1px solid rgba(255,255,255,.06) !important;
}
section[data-testid="stSidebar"] .stButton > button {
    background: linear-gradient(135deg, #ff5e7a, #ff2d55) !important;
    color: white !important;
    box-shadow: 0 4px 20px rgba(255,94,122,.3) !important;
}

/* ── Dashboard card ── */
.dash-card {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.09);
    padding: 24px;
    border-radius: 20px;
    box-shadow: 0 8px 30px rgba(0,0,0,.4);
    margin-bottom: 20px;
}

/* ── Sliders ── */
.stSlider > div > div > div { background: #0072ff !important; }
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
# AUTH PAGES
# =========================
if not st.session_state.logged_in:

    # Centered layout
    _, center, _ = st.columns([1, 2, 1])

    with center:
        # Logo
        st.markdown('<div class="logo-icon-wrap"><div class="logo-icon">🎓</div></div>', unsafe_allow_html=True)
        st.markdown('<p class="main-title">Student <span>Predictor</span></p>', unsafe_allow_html=True)
        st.markdown('<p class="main-sub">AI-powered academic performance portal</p>', unsafe_allow_html=True)

        # Tab selector
        tab = st.selectbox("", ["🔐  Sign In", "📝  Create Account"], label_visibility="collapsed")

        users = load_users()

        # ── LOGIN ──
        if tab == "🔐  Sign In":
            st.markdown('<div class="auth-card">', unsafe_allow_html=True)
            st.markdown('<div class="form-heading">Welcome back 👋</div>', unsafe_allow_html=True)
            st.markdown('<div class="form-sub">Sign in to access your dashboard</div>', unsafe_allow_html=True)

            username = st.text_input("Username", placeholder="Enter your username", key="login_user")
            password = st.text_input("Password", placeholder="Enter your password", type="password", key="login_pass")

            st.write("")
            if st.button("Sign In →", key="login_btn"):
                if not username or not password:
                    st.error("⚠️ Please fill in all fields")
                elif username in users and users[username] == password:
                    st.session_state.logged_in = True
                    st.session_state.username = username
                    st.success("✅ Login successful! Redirecting…")
                    st.rerun()
                else:
                    st.error("❌ Invalid username or password")

            st.markdown('<div class="auth-divider">or continue with</div>', unsafe_allow_html=True)
            c1, c2 = st.columns(2)
            with c1:
                st.button("🔵  Google", key="g_login", use_container_width=True)
            with c2:
                st.button("🔷  Facebook", key="f_login", use_container_width=True)

            st.markdown('</div>', unsafe_allow_html=True)

        # ── SIGN UP ──
        else:
            st.markdown('<div class="auth-card">', unsafe_allow_html=True)
            st.markdown('<div class="form-heading">Create account ✨</div>', unsafe_allow_html=True)
            st.markdown('<div class="form-sub">Join the student predictor portal</div>', unsafe_allow_html=True)

            full_name = st.text_input("Full Name", placeholder="Your full name", key="signup_name")
            new_user  = st.text_input("Username", placeholder="Choose a username", key="signup_user")
            new_pass  = st.text_input("Password", placeholder="Create a strong password", type="password", key="signup_pass")

            # Password strength indicator
            if new_pass:
                score = sum([
                    len(new_pass) >= 8,
                    any(c.isupper() for c in new_pass),
                    any(c.isdigit() for c in new_pass),
                    any(c in "!@#$%^&*" for c in new_pass)
                ])
                colors = ["🔴 Weak", "🟠 Fair", "🟡 Good", "🟢 Strong"]
                st.caption(f"Password strength: **{colors[score-1]}**")

            agree = st.checkbox("I agree to the Terms of Service and Privacy Policy")

            st.write("")
            if st.button("Create Account →", key="signup_btn"):
                if not full_name or not new_user or not new_pass:
                    st.error("⚠️ Please fill in all fields")
                elif not agree:
                    st.warning("⚠️ Please accept the terms and privacy policy")
                elif len(new_pass) < 6:
                    st.error("⚠️ Password must be at least 6 characters")
                elif new_user in users:
                    st.error("❌ Username already exists! Choose another.")
                else:
                    users[new_user] = new_pass
                    save_users(users)
                    st.success("🎉 Account created! Please sign in.")

            st.markdown('<div class="auth-divider">or sign up with</div>', unsafe_allow_html=True)
            c1, c2 = st.columns(2)
            with c1:
                st.button("🔵  Google", key="g_signup", use_container_width=True)
            with c2:
                st.button("🔷  Facebook", key="f_signup", use_container_width=True)

            st.markdown('</div>', unsafe_allow_html=True)

# =========================
# MAIN DASHBOARD
# =========================
else:

    model   = joblib.load("student_model.pkl")
    columns = joblib.load("model_columns.pkl")

    # Sidebar
    st.sidebar.image("https://cdn-icons-png.flaticon.com/512/3135/3135755.png", width=100)
    st.sidebar.markdown(f"### 👋 {st.session_state.username}")
    st.sidebar.markdown("---")

    if st.sidebar.button("🚪 Logout"):
        st.session_state.logged_in = False
        st.rerun()

    # Header
    st.markdown('<p class="main-title">📊 Student <span>Performance</span> Dashboard</p>', unsafe_allow_html=True)
    st.write("")

    # Metric cards
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown('<div class="metric-card">📚 AI Powered Prediction</div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="metric-card">⚡ Real-time Analytics</div>', unsafe_allow_html=True)
    with col3:
        st.markdown('<div class="metric-card">🎯 Smart Accuracy</div>', unsafe_allow_html=True)

    st.write("")
    st.markdown('<div class="dash-card">', unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        hours      = st.slider("Hours Studied", 0, 24, 5)
        attendance = st.slider("Attendance %", 0, 100, 75)
        previous   = st.slider("Previous Score", 0, 100, 60)
        sleep      = st.slider("Sleep Hours", 0, 12, 7)

    with col2:
        motivation = st.selectbox("Motivation Level", ["Low", "Medium", "High"])
        teacher    = st.selectbox("Teacher Quality", ["Poor", "Average", "Good"])
        school     = st.selectbox("School Type", ["Public", "Private"])
        internet   = st.selectbox("Internet Access", ["Yes", "No"])

    st.markdown('</div>', unsafe_allow_html=True)

    if st.button("🚀 Predict Score"):

        data = {
            "Hours_Studied":   hours,
            "Attendance":      attendance,
            "Previous_Scores": previous,
            "Sleep_Hours":     sleep,
            "Motivation_Level": motivation,
            "Teacher_Quality": teacher,
            "School_Type":     school,
            "Internet_Access": internet
        }

        input_df = pd.DataFrame([data])
        input_df = pd.get_dummies(input_df)
        input_df = input_df.reindex(columns=columns, fill_value=0)

        prediction  = model.predict(input_df)
        final_score = max(40, min(100, int(round(prediction[0]))))

        st.markdown(f"""
        <div class="dash-card" style="text-align:center;">
            <h1 style='font-family:Syne,sans-serif;color:#00ffd5;font-size:48px;margin:0;'>
                🎯 {final_score}
            </h1>
            <p style='color:#6b7a99;font-size:15px;margin-top:6px;'>Predicted Exam Score</p>
        </div>
        """, unsafe_allow_html=True)

        # Gauge
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=final_score,
            title={'text': "Performance", 'font': {'color': '#e8eaf6'}},
            number={'font': {'color': '#00ffd5'}},
            gauge={
                'axis': {'range': [0, 100], 'tickcolor': '#6b7a99'},
                'bar': {'color': '#00ffd5'},
                'bgcolor': 'rgba(0,0,0,0)',
                'steps': [
                    {'range': [0, 40],  'color': 'rgba(255,94,122,.2)'},
                    {'range': [40, 70], 'color': 'rgba(255,157,58,.2)'},
                    {'range': [70, 100],'color': 'rgba(0,255,213,.15)'},
                ],
                'threshold': {'line': {'color': '#0072ff', 'width': 3}, 'thickness': .75, 'value': final_score}
            }
        ))
        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font_color='#e8eaf6'
        )
        st.plotly_chart(fig, use_container_width=True)

        # Bar chart
        chart_data = pd.DataFrame({
            "Features": ["Study Hours", "Attendance", "Prev Score", "Sleep"],
            "Values":   [hours, attendance, previous, sleep]
        })
        bar_fig = px.bar(
            chart_data, x="Features", y="Values",
            title="Student Analytics",
            color="Values",
            color_continuous_scale=["#0072ff", "#00ffd5"]
        )
        bar_fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font_color='#e8eaf6',
            title_font_family='Syne'
        )
        st.plotly_chart(bar_fig, use_container_width=True)
