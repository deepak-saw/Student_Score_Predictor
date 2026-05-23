import streamlit as st
import joblib
import pandas as pd
import json
import os
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(
    page_title="EduPredict | Student Performance Portal",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# =========================
# CUSTOM CSS
# =========================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Clash+Display:wght@400;500;600;700&family=Syne:wght@400;600;700;800&family=DM+Sans:ital,wght@0,300;0,400;0,500;1,300&display=swap');

*, *::before, *::after { box-sizing: border-box; margin:0; padding:0; }

html, body, .stApp {
    background: #060b18 !important;
    color: #dce3f0;
    font-family: 'DM Sans', sans-serif;
    scroll-behavior: smooth;
}

/* ── hide default streamlit chrome ── */
#MainMenu, footer, header { visibility: hidden; }
.stDeployButton { display:none; }
[data-testid="stToolbar"] { display:none; }

/* ── Background mesh ── */
.stApp::before {
    content:'';
    position:fixed; inset:0; z-index:0; pointer-events:none;
    background:
        radial-gradient(ellipse 80% 60% at 10% 20%, rgba(0,114,255,.12) 0%, transparent 60%),
        radial-gradient(ellipse 60% 50% at 90% 80%, rgba(0,255,213,.08) 0%, transparent 60%),
        radial-gradient(ellipse 40% 40% at 50% 50%, rgba(124,58,237,.06) 0%, transparent 70%);
}
.stApp::after {
    content:'';
    position:fixed; inset:0; z-index:0; pointer-events:none;
    background-image:
        linear-gradient(rgba(0,255,213,.025) 1px, transparent 1px),
        linear-gradient(90deg, rgba(0,255,213,.025) 1px, transparent 1px);
    background-size: 72px 72px;
    animation: gridScroll 25s linear infinite;
}
@keyframes gridScroll { to { background-position: 0 72px; } }

/* ── NAV ── */
.nav-bar {
    display:flex; align-items:center; justify-content:space-between;
    padding: 20px 48px;
    position:relative; z-index:10;
    border-bottom: 1px solid rgba(255,255,255,.06);
    background: rgba(6,11,24,.8);
    backdrop-filter: blur(12px);
}
.nav-logo {
    display:flex; align-items:center; gap:10px;
    font-family:'Syne',sans-serif; font-size:20px; font-weight:800;
    color:#dce3f0; letter-spacing:-0.5px;
}
.nav-logo .dot { color:#00ffd5; }
.nav-links {
    display:flex; gap:32px;
    font-size:13px; font-weight:500; color:#6b7a99;
}
.nav-links span { cursor:pointer; transition:color .2s; }
.nav-links span:hover { color:#00ffd5; }
.nav-cta {
    padding:9px 22px;
    background: linear-gradient(135deg,#00ffd5,#0072ff);
    border-radius:10px;
    font-family:'Syne',sans-serif; font-size:13px; font-weight:700;
    color:#060b18; cursor:pointer;
    box-shadow:0 4px 20px rgba(0,255,213,.25);
    transition: all .2s;
}
.nav-cta:hover { transform:translateY(-1px); box-shadow:0 8px 28px rgba(0,255,213,.35); }

/* ── HERO ── */
.hero-wrap {
    position:relative; z-index:5;
    padding: 80px 48px 60px;
    text-align:center;
}
.hero-badge {
    display:inline-flex; align-items:center; gap:8px;
    padding:7px 16px;
    background: rgba(0,255,213,.08);
    border:1px solid rgba(0,255,213,.2);
    border-radius:99px;
    font-size:12px; font-weight:500; color:#00ffd5;
    letter-spacing:.6px; text-transform:uppercase;
    margin-bottom:28px;
    animation: fadeUp .6s ease both;
}
.hero-badge::before { content:'●'; font-size:8px; animation:blink 1.5s ease-in-out infinite; }
@keyframes blink { 0%,100%{opacity:1} 50%{opacity:.3} }

.hero-title {
    font-family:'Syne',sans-serif;
    font-size:clamp(40px,6vw,76px);
    font-weight:800; line-height:1.05;
    letter-spacing:-2px; color:#dce3f0;
    margin-bottom:20px;
    animation: fadeUp .7s .1s ease both;
}
.hero-title .hl { 
    background: linear-gradient(135deg,#00ffd5,#0072ff);
    -webkit-background-clip:text; -webkit-text-fill-color:transparent;
    background-clip:text;
}

.hero-sub {
    font-size:17px; color:#6b7a99; line-height:1.7;
    max-width:560px; margin:0 auto 40px;
    animation: fadeUp .7s .2s ease both;
}
@keyframes fadeUp { from{opacity:0;transform:translateY(20px)} to{opacity:1;transform:translateY(0)} }

/* ── STATS ROW ── */
.stats-row {
    display:flex; justify-content:center; gap:48px;
    padding: 0 48px 56px;
    position:relative; z-index:5;
    animation: fadeUp .7s .3s ease both;
}
.stat-item { text-align:center; }
.stat-num {
    font-family:'Syne',sans-serif; font-size:36px; font-weight:800;
    background:linear-gradient(135deg,#00ffd5,#0072ff);
    -webkit-background-clip:text; -webkit-text-fill-color:transparent;
    background-clip:text;
}
.stat-label { font-size:13px; color:#6b7a99; margin-top:4px; }
.stat-divider { width:1px; background:rgba(255,255,255,.08); }

/* ── FEATURE CARDS ── */
.features-section {
    padding: 0 48px 72px;
    position:relative; z-index:5;
}
.features-heading {
    font-family:'Syne',sans-serif; font-size:13px; font-weight:600;
    color:#6b7a99; text-transform:uppercase; letter-spacing:2px;
    text-align:center; margin-bottom:36px;
}
.features-grid {
    display:grid; grid-template-columns:repeat(3,1fr); gap:16px;
    max-width:960px; margin:0 auto;
}
.feat-card {
    background:rgba(255,255,255,.03);
    border:1px solid rgba(255,255,255,.07);
    border-radius:20px; padding:28px 24px;
    transition: all .25s ease;
    position:relative; overflow:hidden;
}
.feat-card::before {
    content:''; position:absolute; inset:0; border-radius:20px;
    background:linear-gradient(135deg,rgba(0,255,213,.05),transparent);
    opacity:0; transition:opacity .25s;
}
.feat-card:hover { border-color:rgba(0,255,213,.2); transform:translateY(-3px); }
.feat-card:hover::before { opacity:1; }
.feat-icon {
    font-size:28px; margin-bottom:14px; display:block;
}
.feat-title {
    font-family:'Syne',sans-serif; font-size:16px; font-weight:700;
    color:#dce3f0; margin-bottom:8px;
}
.feat-desc { font-size:13px; color:#6b7a99; line-height:1.6; }

/* ── HOW IT WORKS ── */
.how-section {
    padding: 0 48px 72px;
    max-width:860px; margin:0 auto;
    position:relative; z-index:5;
}
.how-title {
    font-family:'Syne',sans-serif; font-size:32px; font-weight:800;
    color:#dce3f0; letter-spacing:-1px;
    text-align:center; margin-bottom:8px;
}
.how-sub { text-align:center; color:#6b7a99; font-size:14px; margin-bottom:40px; }
.steps-row { display:flex; gap:0; align-items:flex-start; }
.step {
    flex:1; text-align:center; padding:0 16px; position:relative;
}
.step:not(:last-child)::after {
    content:''; position:absolute;
    top:24px; right:-1px; width:calc(100% - 48px); height:1px;
    background:linear-gradient(90deg,rgba(0,255,213,.3),transparent);
}
.step-num {
    width:48px; height:48px; border-radius:14px;
    background:linear-gradient(135deg,#0072ff22,#00ffd522);
    border:1px solid rgba(0,255,213,.25);
    display:inline-flex; align-items:center; justify-content:center;
    font-family:'Syne',sans-serif; font-size:18px; font-weight:800; color:#00ffd5;
    margin-bottom:14px;
}
.step-title { font-family:'Syne',sans-serif; font-size:15px; font-weight:700; color:#dce3f0; margin-bottom:6px; }
.step-desc { font-size:12px; color:#6b7a99; line-height:1.6; }

/* ── AUTH SECTION ── */
.auth-section {
    padding: 0 48px 80px;
    position:relative; z-index:5;
    max-width:520px; margin:0 auto;
}
.auth-section-head {
    text-align:center; margin-bottom:32px;
}
.auth-section-head h2 {
    font-family:'Syne',sans-serif; font-size:30px; font-weight:800;
    color:#dce3f0; letter-spacing:-0.8px; margin-bottom:8px;
}
.auth-section-head p { font-size:14px; color:#6b7a99; }

/* ── AUTH CARD ── */
.auth-card {
    background:rgba(255,255,255,.04);
    border:1px solid rgba(255,255,255,.09);
    border-radius:24px; padding:36px 32px;
    backdrop-filter:blur(20px);
    box-shadow:0 32px 80px rgba(0,0,0,.6), inset 0 1px 0 rgba(255,255,255,.06);
    position:relative; overflow:hidden;
}
.auth-card::before {
    content:''; position:absolute;
    top:0; left:0; right:0; height:1px;
    background:linear-gradient(90deg,transparent,#00ffd5,transparent);
    opacity:.5;
}
.auth-tabs {
    display:flex; gap:4px;
    background:rgba(255,255,255,.05);
    border-radius:14px; padding:4px;
    margin-bottom:28px;
}
.auth-tab {
    flex:1; text-align:center;
    padding:10px 0;
    border-radius:10px;
    font-family:'Syne',sans-serif; font-size:14px; font-weight:600;
    color:#6b7a99; cursor:pointer;
    transition:all .2s;
}
.auth-tab.active-tab {
    background:linear-gradient(135deg,#0072ff,#7c3aed);
    color:white;
    box-shadow:0 4px 20px rgba(0,114,255,.35);
}

.form-label {
    font-size:11px; font-weight:600; color:#6b7a99;
    text-transform:uppercase; letter-spacing:.9px;
    display:block; margin-bottom:8px;
}
.form-heading { font-family:'Syne',sans-serif; font-size:21px; font-weight:700; color:#dce3f0; margin-bottom:4px; }
.form-subtext { font-size:13px; color:#6b7a99; margin-bottom:24px; }

/* ── Streamlit widget overrides ── */
.stTextInput > div > div > input {
    background:rgba(255,255,255,.05) !important;
    border:1px solid rgba(255,255,255,.09) !important;
    border-radius:12px !important;
    color:#dce3f0 !important;
    font-family:'DM Sans',sans-serif !important;
    font-size:15px !important;
    padding:12px 16px !important;
    transition:all .2s !important;
}
.stTextInput > div > div > input:focus {
    border-color:#00ffd5 !important;
    background:rgba(0,255,213,.05) !important;
    box-shadow:0 0 0 3px rgba(0,255,213,.08) !important;
    outline:none !important;
}
.stTextInput label {
    color:#6b7a99 !important;
    font-size:11px !important; font-weight:600 !important;
    text-transform:uppercase !important; letter-spacing:.9px !important;
    font-family:'DM Sans',sans-serif !important;
}
.stCheckbox label { color:#9aa3b5 !important; font-size:13px !important; }
.stCheckbox input[type="checkbox"] { accent-color:#00ffd5 !important; }
.stCaption { color:#6b7a99 !important; font-size:12px !important; }

/* All buttons base */
.stButton > button {
    width:100% !important;
    background:linear-gradient(135deg,#00ffd5,#0072ff) !important;
    color:#060b18 !important;
    font-family:'Syne',sans-serif !important; font-size:15px !important; font-weight:700 !important;
    border:none !important; border-radius:14px !important;
    padding:14px 20px !important; letter-spacing:.3px !important;
    box-shadow:0 8px 30px rgba(0,255,213,.2) !important;
    transition:all .2s !important; cursor:pointer !important;
}
.stButton > button:hover {
    transform:translateY(-2px) !important;
    box-shadow:0 12px 40px rgba(0,255,213,.35) !important;
}

/* Alerts */
div[data-testid="stAlert"] {
    border-radius:12px !important;
    font-family:'DM Sans',sans-serif !important; font-size:14px !important;
}

/* Selectbox */
.stSelectbox > div > div {
    background:rgba(255,255,255,.05) !important;
    border:1px solid rgba(255,255,255,.09) !important;
    border-radius:12px !important; color:#dce3f0 !important;
}

/* Slider */
.stSlider [data-baseweb="slider"] div { background:#0072ff !important; }
.stSlider label { color:#9aa3b5 !important; font-size:13px !important; }

/* ── SIDEBAR ── */
section[data-testid="stSidebar"] {
    background:#0a1020 !important;
    border-right:1px solid rgba(255,255,255,.05) !important;
}
section[data-testid="stSidebar"] .stButton > button {
    background:linear-gradient(135deg,#ff5e7a,#c0392b) !important;
    color:white !important;
    box-shadow:0 4px 20px rgba(255,94,122,.25) !important;
}

/* ── DASHBOARD ── */
.dash-title {
    font-family:'Syne',sans-serif; font-size:36px; font-weight:800;
    color:#dce3f0; letter-spacing:-1px;
    margin-bottom:4px;
}
.dash-title span { color:#00ffd5; }
.dash-sub { color:#6b7a99; font-size:14px; margin-bottom:32px; }

.metric-card {
    background:linear-gradient(135deg,rgba(0,114,255,.12),rgba(0,255,213,.06));
    border:1px solid rgba(0,255,213,.15);
    padding:24px 20px; border-radius:18px;
    text-align:center;
    font-family:'Syne',sans-serif; font-size:16px; font-weight:700; color:#dce3f0;
    box-shadow:0 8px 30px rgba(0,0,0,.3);
    transition:transform .2s;
}
.metric-card:hover { transform:translateY(-2px); }

.dash-card {
    background:rgba(255,255,255,.03);
    border:1px solid rgba(255,255,255,.07);
    padding:28px 24px; border-radius:20px;
    box-shadow:0 8px 40px rgba(0,0,0,.4);
    margin-bottom:20px; position:relative; overflow:hidden;
}
.dash-card::before {
    content:''; position:absolute; top:0; left:0; right:0; height:1px;
    background:linear-gradient(90deg,transparent,rgba(0,114,255,.5),transparent);
}

.score-display {
    text-align:center; padding:32px 20px;
}
.score-num {
    font-family:'Syne',sans-serif; font-size:80px; font-weight:800;
    line-height:1;
    background:linear-gradient(135deg,#00ffd5,#0072ff);
    -webkit-background-clip:text; -webkit-text-fill-color:transparent;
    background-clip:text;
}
.score-label { font-size:15px; color:#6b7a99; margin-top:8px; letter-spacing:.5px; }

/* Auth divider */
.a-divider {
    display:flex; align-items:center; gap:12px;
    color:#4a5568; font-size:12px; margin:20px 0;
}
.a-divider::before,.a-divider::after {
    content:''; flex:1; height:1px; background:rgba(255,255,255,.07);
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
if "auth_tab" not in st.session_state:
    st.session_state.auth_tab = "signin"

# =========================
# LANDING + AUTH PAGE
# =========================
if not st.session_state.logged_in:

    users = load_users()

    # ── NAV ──
    st.markdown("""
    <div class="nav-bar">
        <div class="nav-logo">🎓 Edu<span class="dot">Predict</span></div>
        <div class="nav-links">
            <span>Features</span>
            <span>How it Works</span>
            <span>About</span>
        </div>
        <div class="nav-cta">Get Started Free</div>
    </div>
    """, unsafe_allow_html=True)

    # ── HERO ──
    st.markdown("""
    <div class="hero-wrap">
        <div class="hero-badge">✦ &nbsp;AI-Powered Academic Intelligence</div>
        <h1 class="hero-title">
            Predict Your Academic<br>
            <span class="hl">Performance Score</span>
        </h1>
        <p class="hero-sub">
            Enter your study habits, attendance, and lifestyle data — 
            our machine learning model predicts your exam score with high accuracy.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # ── STATS ──
    st.markdown("""
    <div class="stats-row">
        <div class="stat-item">
            <div class="stat-num">95%</div>
            <div class="stat-label">Prediction Accuracy</div>
        </div>
        <div class="stat-divider"></div>
        <div class="stat-item">
            <div class="stat-num">12K+</div>
            <div class="stat-label">Students Analyzed</div>
        </div>
        <div class="stat-divider"></div>
        <div class="stat-item">
            <div class="stat-num">8</div>
            <div class="stat-label">Key Factors Tracked</div>
        </div>
        <div class="stat-divider"></div>
        <div class="stat-item">
            <div class="stat-num">Real-time</div>
            <div class="stat-label">Instant Insights</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── FEATURES ──
    st.markdown("""
    <div class="features-section">
        <div class="features-heading">✦ &nbsp; Why EduPredict</div>
        <div class="features-grid">
            <div class="feat-card">
                <span class="feat-icon">🧠</span>
                <div class="feat-title">ML-Powered Engine</div>
                <div class="feat-desc">Linear regression model trained on 12,000+ student records to deliver accurate score predictions.</div>
            </div>
            <div class="feat-card">
                <span class="feat-icon">📊</span>
                <div class="feat-title">Visual Analytics</div>
                <div class="feat-desc">Gauge charts and bar graphs give you an instant visual breakdown of your performance drivers.</div>
            </div>
            <div class="feat-card">
                <span class="feat-icon">⚡</span>
                <div class="feat-title">Instant Results</div>
                <div class="feat-desc">Get your predicted exam score in under a second — no waiting, no delays.</div>
            </div>
            <div class="feat-card">
                <span class="feat-icon">🔒</span>
                <div class="feat-title">Secure Accounts</div>
                <div class="feat-desc">Your data is stored securely with personalized login so only you can see your predictions.</div>
            </div>
            <div class="feat-card">
                <span class="feat-icon">🎯</span>
                <div class="feat-title">8 Key Metrics</div>
                <div class="feat-desc">Study hours, attendance, sleep, motivation, teacher quality, school type, and more.</div>
            </div>
            <div class="feat-card">
                <span class="feat-icon">📱</span>
                <div class="feat-title">Responsive Design</div>
                <div class="feat-desc">Clean, modern interface that works beautifully on desktop and mobile devices.</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── HOW IT WORKS ──
    st.markdown("""
    <div class="how-section">
        <h2 class="how-title">How It Works</h2>
        <p class="how-sub">Three simple steps to your predicted score</p>
        <div class="steps-row">
            <div class="step">
                <div class="step-num">1</div>
                <div class="step-title">Create Account</div>
                <div class="step-desc">Sign up in seconds with a username and password — no email required.</div>
            </div>
            <div class="step">
                <div class="step-num">2</div>
                <div class="step-title">Enter Your Data</div>
                <div class="step-desc">Input your study habits, attendance, sleep, and other factors via sliders.</div>
            </div>
            <div class="step">
                <div class="step-num">3</div>
                <div class="step-title">Get Your Score</div>
                <div class="step-desc">Our AI model instantly predicts your exam score with visual analytics.</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── AUTH SECTION ──
    st.markdown("""
    <div class="auth-section">
        <div class="auth-section-head">
            <h2>Get Started Today</h2>
            <p>Create your free account or sign in to your dashboard</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Centered auth card
    _, center, _ = st.columns([1, 2, 1])
    with center:

        # Tab buttons (using Streamlit columns as tab switcher)
        t1, t2 = st.columns(2)
        with t1:
            if st.button("🔐  Sign In", key="tab_signin", use_container_width=True):
                st.session_state.auth_tab = "signin"
                st.rerun()
        with t2:
            if st.button("📝  Create Account", key="tab_signup", use_container_width=True):
                st.session_state.auth_tab = "signup"
                st.rerun()

        st.write("")

        # ─── SIGN IN ───
        if st.session_state.auth_tab == "signin":
            st.markdown('<div class="auth-card">', unsafe_allow_html=True)
            st.markdown('<div class="form-heading">Welcome back 👋</div>', unsafe_allow_html=True)
            st.markdown('<div class="form-subtext">Sign in to access your prediction dashboard</div>', unsafe_allow_html=True)

            username = st.text_input("Username", placeholder="Enter your username", key="si_user")
            password = st.text_input("Password", placeholder="Enter your password", type="password", key="si_pass")

            st.write("")
            if st.button("Sign In →", key="do_signin"):
                if not username or not password:
                    st.error("⚠️ Please fill in all fields")
                elif username in users and users[username] == password:
                    st.session_state.logged_in = True
                    st.session_state.username = username
                    st.success("✅ Login successful!")
                    st.rerun()
                else:
                    st.error("❌ Invalid username or password")

            st.markdown('<div class="a-divider">or continue with</div>', unsafe_allow_html=True)
            c1, c2 = st.columns(2)
            with c1: st.button("🔵 Google", key="g_si")
            with c2: st.button("🔷 GitHub", key="gh_si")
            st.markdown('</div>', unsafe_allow_html=True)

        # ─── CREATE ACCOUNT ───
        else:
            st.markdown('<div class="auth-card">', unsafe_allow_html=True)
            st.markdown('<div class="form-heading">Create account ✨</div>', unsafe_allow_html=True)
            st.markdown('<div class="form-subtext">Join EduPredict — free forever</div>', unsafe_allow_html=True)

            full_name = st.text_input("Full Name", placeholder="Your full name", key="su_name")
            new_user  = st.text_input("Username", placeholder="Choose a username", key="su_user")
            new_pass  = st.text_input("Password", placeholder="Create a strong password (min 6 chars)", type="password", key="su_pass")

            if new_pass:
                score = sum([
                    len(new_pass) >= 8,
                    any(c.isupper() for c in new_pass),
                    any(c.isdigit() for c in new_pass),
                    any(c in "!@#$%^&*" for c in new_pass)
                ])
                labels = ["🔴 Weak","🟠 Fair","🟡 Good","🟢 Strong"]
                st.caption(f"Password strength: **{labels[max(0,score-1)]}**")

            agree = st.checkbox("I agree to the Terms of Service and Privacy Policy")

            st.write("")
            if st.button("Create Account →", key="do_signup"):
                if not full_name or not new_user or not new_pass:
                    st.error("⚠️ Please fill in all fields")
                elif not agree:
                    st.warning("⚠️ Accept terms to continue")
                elif len(new_pass) < 6:
                    st.error("⚠️ Password too short — minimum 6 characters")
                elif new_user in users:
                    st.error("❌ Username already taken — try another")
                else:
                    users[new_user] = new_pass
                    save_users(users)
                    st.success("🎉 Account created! Click 'Sign In' to login.")
                    st.session_state.auth_tab = "signin"

            st.markdown('<div class="a-divider">or sign up with</div>', unsafe_allow_html=True)
            c1, c2 = st.columns(2)
            with c1: st.button("🔵 Google", key="g_su")
            with c2: st.button("🔷 GitHub", key="gh_su")
            st.markdown('</div>', unsafe_allow_html=True)


# =========================
# MAIN DASHBOARD
# =========================
else:
    model   = joblib.load("student_model.pkl")
    columns = joblib.load("model_columns.pkl")

    # Sidebar
    st.sidebar.image("https://cdn-icons-png.flaticon.com/512/3135/3135755.png", width=90)
    st.sidebar.markdown(f"### 👋 {st.session_state.username}")
    st.sidebar.markdown("---")
    st.sidebar.caption("🎓 EduPredict Dashboard")
    st.sidebar.markdown("---")
    if st.sidebar.button("🚪 Logout"):
        st.session_state.logged_in = False
        st.rerun()

    # Header
    st.markdown(f'<div class="dash-title">📊 Performance <span>Dashboard</span></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="dash-sub">Hello {st.session_state.username} — enter your data and predict your score</div>', unsafe_allow_html=True)

    # Metric cards
    c1, c2, c3 = st.columns(3)
    with c1: st.markdown('<div class="metric-card">🧠 AI-Powered Prediction</div>', unsafe_allow_html=True)
    with c2: st.markdown('<div class="metric-card">⚡ Real-time Analytics</div>', unsafe_allow_html=True)
    with c3: st.markdown('<div class="metric-card">🎯 Smart Accuracy</div>', unsafe_allow_html=True)

    st.write("")

    # Input form
    st.markdown('<div class="dash-card">', unsafe_allow_html=True)
    st.markdown("#### 📝 Enter Your Details")
    st.write("")

    col1, col2 = st.columns(2)
    with col1:
        hours      = st.slider("📚 Hours Studied (per day)", 0, 24, 5)
        attendance = st.slider("🏫 Attendance (%)", 0, 100, 75)
        previous   = st.slider("📋 Previous Score", 0, 100, 60)
        sleep      = st.slider("😴 Sleep Hours", 0, 12, 7)
    with col2:
        motivation = st.selectbox("💪 Motivation Level", ["Low", "Medium", "High"])
        teacher    = st.selectbox("👨‍🏫 Teacher Quality", ["Poor", "Average", "Good"])
        school     = st.selectbox("🏛️ School Type", ["Public", "Private"])
        internet   = st.selectbox("🌐 Internet Access", ["Yes", "No"])

    st.markdown('</div>', unsafe_allow_html=True)

    if st.button("🚀 Predict My Score"):
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
        prediction  = model.predict(input_df)
        final_score = max(40, min(100, int(round(prediction[0]))))

        grade = "A+" if final_score>=90 else "A" if final_score>=80 else "B" if final_score>=70 else "C" if final_score>=60 else "D"
        remark = "Outstanding!" if final_score>=90 else "Excellent!" if final_score>=80 else "Good Job!" if final_score>=70 else "Keep Going!" if final_score>=60 else "Need Improvement"

        st.markdown(f"""
        <div class="dash-card score-display">
            <div class="score-num">{final_score}</div>
            <div class="score-label">Predicted Exam Score &nbsp;·&nbsp; Grade: {grade} &nbsp;·&nbsp; {remark}</div>
        </div>
        """, unsafe_allow_html=True)

        r1, r2 = st.columns(2)
        with r1:
            fig = go.Figure(go.Indicator(
                mode="gauge+number",
                value=final_score,
                title={'text':"Performance Score",'font':{'color':'#dce3f0','family':'Syne'}},
                number={'font':{'color':'#00ffd5','family':'Syne'}},
                gauge={
                    'axis':{'range':[0,100],'tickcolor':'#4a5568'},
                    'bar':{'color':'#00ffd5','thickness':.25},
                    'bgcolor':'rgba(0,0,0,0)',
                    'borderwidth':0,
                    'steps':[
                        {'range':[0,40],'color':'rgba(255,94,122,.15)'},
                        {'range':[40,70],'color':'rgba(255,157,58,.15)'},
                        {'range':[70,100],'color':'rgba(0,255,213,.12)'},
                    ],
                    'threshold':{'line':{'color':'#0072ff','width':4},'thickness':.8,'value':final_score}
                }
            ))
            fig.update_layout(
                paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                font_color='#dce3f0', height=300, margin=dict(t=40,b=20,l=20,r=20)
            )
            st.plotly_chart(fig, use_container_width=True)

        with r2:
            chart_data = pd.DataFrame({
                "Metric": ["Study\nHours","Attendance","Prev\nScore","Sleep\nHours"],
                "Value":  [hours, attendance, previous, sleep]
            })
            bar_fig = px.bar(
                chart_data, x="Metric", y="Value",
                color="Value", color_continuous_scale=["#0072ff","#00ffd5"],
                title="Your Key Metrics"
            )
            bar_fig.update_layout(
                paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                font_color='#dce3f0', height=300,
                title_font_family='Syne', title_font_size=15,
                coloraxis_showscale=False,
                margin=dict(t=40,b=20,l=20,r=20)
            )
            bar_fig.update_traces(marker_line_width=0)
            st.plotly_chart(bar_fig, use_container_width=True)
