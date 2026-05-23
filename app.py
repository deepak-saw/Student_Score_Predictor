import streamlit as st
import json
import os
import joblib
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# ─────────────────────────────────────────────────────────────────────────
#  1. कॉमन यूटिलिटीज और JSON हैंडलिंग (Common Utilities & JSON Handling)
# ─────────────────────────────────────────────────────────────────────────

def load_json(path):
    if not os.path.exists(path):
        return {}
    with open(path, "r") as f:
        return json.load(f)

def save_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


# ─────────────────────────────────────────────────────────────────────────
#  2. प्रोफाइल विजेट और थीम सेटिंग्स (Profile Widget & CSS Styles)
# ─────────────────────────────────────────────────────────────────────────

PROFILE_CSS = """
<style>
.profile-topbar {
    position: fixed; top: 12px; right: 24px;
    z-index: 9999; display: flex; align-items: center; gap: 10px;
}
.profile-avatar {
    width: 40px; height: 40px; border-radius: 50%;
    background: linear-gradient(135deg, #0072ff, #00ffd5);
    display: flex; align-items: center; justify-content: center;
    font-family: 'Syne', sans-serif;
    font-size: 16px; font-weight: 800; color: #050912;
    cursor: pointer; border: 2px solid rgba(0,255,213,.4);
    box-shadow: 0 0 16px rgba(0,255,213,.25);
    transition: box-shadow .2s; user-select: none;
}
.profile-avatar:hover { box-shadow: 0 0 28px rgba(0,255,213,.45); }
.profile-dropdown {
    background: rgba(10,16,30,.97);
    border: 1px solid rgba(255,255,255,.1);
    border-radius: 18px; padding: 22px 22px 16px; width: 270px;
    backdrop-filter: blur(24px);
    box-shadow: 0 24px 64px rgba(0,0,0,.6);
    animation: dropIn .18s ease;
}
@keyframes dropIn { from{opacity:0;transform:translateY(-8px)} to{opacity:1;transform:translateY(0)} }
.pd-name {
    font-family: 'Syne', sans-serif;
    font-size: 17px; font-weight: 700; color: #dce3f0; margin-bottom: 3px;
}
.pd-role-badge {
    display: inline-block; padding: 2px 10px; border-radius: 99px;
    font-size: 10px; font-weight: 700;
    text-transform: uppercase; letter-spacing: .8px; margin-bottom: 14px;
}
.badge-student { background:rgba(0,114,255,.15); border:1px solid rgba(0,114,255,.3); color:#0072ff; }
.badge-parent  { background:rgba(124,58,237,.15); border:1px solid rgba(124,58,237,.3); color:#7c3aed; }
.pd-info-row { display: flex; gap: 6px; font-size: 12px; color: #6b7a99; margin-bottom: 5px; }
.pd-info-row span { color: #9aa3b5; }
.pd-divider { height: 1px; background: rgba(255,255,255,.07); margin: 14px 0; }
</style>
"""

def show_profile_widget():
    st.markdown(PROFILE_CSS, unsafe_allow_html=True)

    username = st.session_state.get("username", "")
    role     = st.session_state.get("user_role", "student")
    students = load_json("students.json")
    parents  = load_json("parents.json")

    if role == "student":
        profile   = students.get(username, {})
        full_name = profile.get("full_name", username)
    else:
        profile   = parents.get(username, {})
        full_name = profile.get("full_name", username)

    parts    = full_name.strip().split()
    initials = (parts[0][0] + (parts[-1][0] if len(parts) > 1 else "")).upper() if parts else "??"

    if "app_theme" not in st.session_state:
        st.session_state.app_theme = "dark"
    if "profile_open" not in st.session_state:
        st.session_state.profile_open = False

    spacer, btn_col = st.columns([11, 1])
    with btn_col:
        if st.button(initials, key="profile_avatar_btn", help="Profile & Settings"):
            st.session_state.profile_open = not st.session_state.profile_open
            st.rerun()

    st.markdown("""
    <style>
    div[data-testid="column"]:last-child > div > div > button {
        width: 40px !important; height: 40px !important;
        border-radius: 50% !important; padding: 0 !important;
        background: linear-gradient(135deg,#0072ff,#00ffd5) !important;
        color: #050912 !important; font-family: 'Syne',sans-serif !important;
        font-size: 15px !important; font-weight: 800 !important;
        border: 2px solid rgba(0,255,213,.4) !important;
        box-shadow: 0 0 16px rgba(0,255,213,.25) !important;
        min-width: unset !important; float: right;
    }
    </style>
    """, unsafe_allow_html=True)

    if st.session_state.profile_open:
        with st.container():
            badge_class = "badge-student" if role == "student" else "badge-parent"
            badge_label = "Student"       if role == "student" else "Parent"

            if role == "student":
                info_rows = f"""
                <div class="pd-info-row">🏫 <span>{profile.get('school_name','—')}</span></div>
                <div class="pd-info-row">📚 <span>Class {profile.get('class_grade','—')} · Section {profile.get('section','—')}</span></div>
                <div class="pd-info-row">🎂 <span>Age {profile.get('age','—')}</span></div>
                <div class="pd-info-row">🔖 <span>Roll No. {profile.get('roll_no','—')}</span></div>
                """
            else:
                children_count = len(profile.get("children", []))
                info_rows = f"""
                <div class="pd-info-row">👨‍👩‍👧 <span>{children_count} child(ren) linked</span></div>
                <div class="pd-info-row">📞 <span>{profile.get('phone','—')}</span></div>
                <div class="pd-info-row">💼 <span>{profile.get('relation','Guardian')}</span></div>
                """

            st.markdown(f"""
            <div class="profile-dropdown">
                <div class="pd-name">{full_name}</div>
                <div class="pd-role-badge {badge_class}">{badge_label}</div>
                {info_rows}
                <div class="pd-divider"></div>
                <div style="font-size:11px;color:#6b7a99;margin-bottom:10px;letter-spacing:.5px;">SETTINGS</div>
            </div>
            """, unsafe_allow_html=True)

            col_a, col_b = st.columns(2)
            with col_a:
                if st.button("✏️  Edit Profile", key="open_edit_profile", use_container_width=True):
                    st.session_state.edit_profile_open = True
                    st.session_state.profile_open      = False
                    st.rerun()
            with col_b:
                theme_label = "🌙 Dark" if st.session_state.app_theme == "dark" else "☀️ Light"
                if st.button(theme_label, key="toggle_theme_btn", use_container_width=True):
                    st.session_state.app_theme = "light" if st.session_state.app_theme == "dark" else "dark"
                    st.rerun()

            st.write("")
            if st.button("🚪  Sign Out", key="profile_signout_btn", use_container_width=True, type="primary"):
                for k in ["logged_in", "username", "user_role"]:
                    st.session_state[k] = False if k == "logged_in" else ""
                st.session_state.profile_open = False
                st.rerun()

    if st.session_state.get("edit_profile_open", False):
        _show_edit_modal(username, role, profile, students, parents)

    if st.session_state.get("app_theme") == "light":
        st.markdown("""
        <style>
        html, body, .stApp { background:#f0f4ff !important; color:#1a1f36 !important; }
        .stApp::before { opacity:.3; } .stApp::after { opacity:.15; }
        .kpi-card, .input-card, .profile-card, .score-card, .profile-dropdown {
            background: rgba(255,255,255,.8) !important;
            border-color: rgba(0,0,0,.1) !important; color: #1a1f36 !important;
        }
        .kpi-label, .kpi-sub, .dash-sub, .profile-detail,
        .feat-text, .step-text { color:#444f72 !important; }
        .dash-title, .dash-greeting, .profile-name, .pd-name { color:#1a1f36 !important; }
        </style>
        """, unsafe_allow_html=True)


def _show_edit_modal(username, role, profile, students, parents):
    st.markdown("""
    <style>
    .edit-modal {
        background: rgba(10,16,30,.98); border: 1px solid rgba(0,255,213,.2);
        border-radius: 20px; padding: 28px 32px; max-width: 560px;
        margin: 0 auto 32px; box-shadow: 0 32px 80px rgba(0,0,0,.7);
        animation: dropIn .2s ease;
    }
    .edit-modal-title {
        font-family:'Syne',sans-serif; font-size:20px; font-weight:800;
        color:#dce3f0; margin-bottom:6px;
    }
    .edit-modal-sub { font-size:13px; color:#6b7a99; margin-bottom:22px; }
    </style>
    """, unsafe_allow_html=True)

    st.markdown('<div class="edit-modal">', unsafe_allow_html=True)
    st.markdown('<div class="edit-modal-title">✏️ Edit Profile</div>', unsafe_allow_html=True)
    st.markdown('<div class="edit-modal-sub">Update your personal information below</div>', unsafe_allow_html=True)

    if role == "student":
        with st.form("edit_student_form"):
            c1, c2 = st.columns(2)
            with c1:
                new_name  = st.text_input("Full Name",    value=profile.get("full_name", ""))
                new_age   = st.number_input("Age", min_value=5, max_value=25, value=int(profile.get("age", 15)))
                new_class = st.text_input("Class / Grade", value=profile.get("class_grade", ""))
            with c2:
                new_section = st.text_input("Section",     value=profile.get("section", ""))
                new_roll    = st.text_input("Roll Number", value=profile.get("roll_no", ""))
                new_school  = st.text_input("School Name", value=profile.get("school_name", ""))

            col_save, col_cancel = st.columns(2)
            with col_save:
                save_btn   = st.form_submit_button("💾  Save Changes", use_container_width=True, type="primary")
            with col_cancel:
                cancel_btn = st.form_submit_button("✕  Cancel", use_container_width=True)

            if save_btn:
                if username not in students:
                    students[username] = {}
                students[username].update({
                    "full_name": new_name, "age": new_age, "class_grade": new_class,
                    "section": new_section, "roll_no": new_roll, "school_name": new_school,
                })
                save_json("students.json", students)
                st.session_state.edit_profile_open = False
                st.toast("✅ Profile updated successfully!")
                st.rerun()
            if cancel_btn:
                st.session_state.edit_profile_open = False
                st.rerun()
    else:
        with st.form("edit_parent_form"):
            c1, c2 = st.columns(2)
            with c1:
                new_name  = st.text_input("Full Name",    value=profile.get("full_name", ""))
                new_phone = st.text_input("Phone Number", value=profile.get("phone", ""))
            with c2:
                current_relation = profile.get("relation", "Guardian")
                options = ["Father", "Mother", "Guardian"]
                default_idx = options.index(current_relation) if current_relation in options else 2
                new_relation = st.selectbox("Relation with Child", options, index=default_idx)

            col_save, col_cancel = st.columns(2)
            with col_save:
                save_btn   = st.form_submit_button("💾  Save Changes", use_container_width=True, type="primary")
            with col_cancel:
                cancel_btn = st.form_submit_button("✕  Cancel", use_container_width=True)

            if save_btn:
                if username not in parents:
                    parents[username] = {"children": []}
                parents[username].update({
                    "full_name": new_name, "phone": new_phone, "relation": new_relation,
                })
                save_json("parents.json", parents)
                st.session_state.edit_profile_open = False
                st.toast("✅ Profile updated successfully!")
                st.rerun()
            if cancel_btn:
                st.session_state.edit_profile_open = False
                st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────
#  3. छात्र डैशबोर्ड (Student Dashboard Function)
# ─────────────────────────────────────────────────────────────────────────

def show_student_dashboard():
    username = st.session_state.username
    students = load_json("students.json")
    profile  = students.get(username, {})

    try:
        model   = joblib.load("student_model.pkl")
        columns = joblib.load("model_columns.pkl")
    except Exception as e:
        st.error(f"Failed to load model files: {e}")
        return

    show_profile_widget()

    # ── Sidebar ──
    st.sidebar.image("https://cdn-icons-png.flaticon.com/512/3135/3135755.png", width=80)
    st.sidebar.markdown(f"### 👋 {profile.get('full_name', username)}")
    st.sidebar.markdown(
        '<span style="background:rgba(0,114,255,.15);border:1px solid rgba(0,114,255,.3);'
        'color:#0072ff;font-size:11px;font-weight:700;padding:3px 10px;border-radius:99px;'
        'text-transform:uppercase;letter-spacing:.8px;">Student</span>',
        unsafe_allow_html=True)
    st.sidebar.markdown("---")
    st.sidebar.markdown("**🎓 EduPredict**")
    st.sidebar.caption("AI Student Performance Portal")
    st.sidebar.markdown("---")
    st.sidebar.markdown("**📌 Quick Stats**")
    st.sidebar.caption("✅ Model: Linear Regression")
    st.sidebar.caption("📊 Trained on 12K+ records")
    st.sidebar.caption("⚡ Real-time predictions")
    st.sidebar.markdown("---")
    if st.sidebar.button("🚪 Logout", key="student_logout"):
        for k in ["logged_in", "username", "user_role"]:
            st.session_state[k] = False if k == "logged_in" else ""
        st.rerun()

    # ── Hero ──
    st.markdown(f"""
    <div class="dash-hero">
        <div class="dash-greeting">Welcome back, student</div>
        <div class="dash-title">Performance <span class="acc">Dashboard</span></div>
        <div class="dash-sub">Hello {profile.get('full_name', username)} — enter your details below and get your predicted score instantly</div>
    </div>
    """, unsafe_allow_html=True)

    if profile:
        st.markdown(f"""
        <div class="profile-card">
            <div class="profile-name">🎓 {profile.get('full_name','N/A')}</div>
            <div class="profile-detail">
                <span>Class:</span> {profile.get('class_grade','N/A')} &nbsp;|&nbsp;
                <span>Section:</span> {profile.get('section','N/A')} &nbsp;|&nbsp;
                <span>Roll No:</span> {profile.get('roll_no','N/A')} &nbsp;|&nbsp;
                <span>Age:</span> {profile.get('age','N/A')} &nbsp;|&nbsp;
                <span>School:</span> {profile.get('school_name','N/A')}
            </div>
        </div>
        """, unsafe_allow_html=True)

    # ── KPI Cards ──
    k1, k2, k3, k4 = st.columns(4)
    with k1:
        st.markdown("""<div class="kpi-card"><div class="kpi-icon">🧠</div>
            <div class="kpi-label">AI Prediction</div><div class="kpi-sub">ML-powered engine</div></div>""", unsafe_allow_html=True)
    with k2:
        st.markdown("""<div class="kpi-card"><div class="kpi-icon">📊</div>
            <div class="kpi-label">Visual Analytics</div><div class="kpi-sub">Charts & graphs</div></div>""", unsafe_allow_html=True)
    with k3:
        st.markdown("""<div class="kpi-card"><div class="kpi-icon">🎯</div>
            <div class="kpi-label">95% Accuracy</div><div class="kpi-sub">High precision model</div></div>""", unsafe_allow_html=True)
    with k4:
        st.markdown("""<div class="kpi-card"><div class="kpi-icon">⚡</div>
            <div class="kpi-label">Instant Results</div><div class="kpi-sub">Under 1 second</div></div>""", unsafe_allow_html=True)

    st.write("")

    # ── Inputs Form ──
    with st.form("student_prediction_form"):
        col1, col2 = st.columns(2, gap="large")
        with col1:
            st.markdown('<div class="input-card"><div class="input-section-title">📐 Academic Inputs</div>', unsafe_allow_html=True)
            hours      = st.slider("📚 Hours Studied (per day)", 0, 24, 5)
            attendance = st.slider("🏫 Attendance (%)", 0, 100, 75)
            previous   = st.slider("📋 Previous Score", 0, 100, 60)
            sleep      = st.slider("😴 Sleep Hours", 0, 12, 7)
            st.markdown('</div>', unsafe_allow_html=True)
        with col2:
            st.markdown('<div class="input-card"><div class="input-section-title">🎛️ Environmental Factors</div>', unsafe_allow_html=True)
            motivation = st.selectbox("💪 Motivation Level", ["Low", "Medium", "High"])
            teacher    = st.selectbox("👨‍🏫 Teacher Quality", ["Poor", "Average", "Good"])
            school     = st.selectbox("🏛️ School Type", ["Public", "Private"])
            internet   = st.selectbox("🌐 Internet Access", ["Yes", "No"])
            st.markdown('</div>', unsafe_allow_html=True)

        predict_btn = st.form_submit_button("🚀  Predict My Score", use_container_width=True)

    if predict_btn or "last_score" in profile:
        if predict_btn:
            data = {
                "Hours_Studied": hours, "Attendance": attendance,
                "Previous_Scores": previous, "Sleep_Hours": sleep,
                "Motivation_Level": motivation, "Teacher_Quality": teacher,
                "School_Type": school, "Internet_Access": internet
            }
            input_df = pd.DataFrame([data])
            input_df = pd.get_dummies(input_df)
            input_df = input_df.reindex(columns=columns, fill_value=0)
            prediction  = model.predict(input_df)
            final_score = max(40, min(100, int(round(prediction[0]))))

            grade  = ("A+" if final_score>=90 else "A" if final_score>=80 else
                      "B"  if final_score>=70 else "C" if final_score>=60 else "D")
            remark = ("Outstanding! 🌟" if final_score>=90 else "Excellent! 🎉" if final_score>=80 else
                      "Good Job! 👍"    if final_score>=70 else "Keep Going! 💪" if final_score>=60 else
                      "Need Improvement 📖")

            if username not in students:
                students[username] = {}
            students[username]["last_score"]     = final_score
            students[username]["last_grade"]     = grade
            students[username]["last_remark"]    = remark
            students[username]["last_predicted"] = datetime.now().strftime("%d %b %Y, %I:%M %p")
            students[username]["last_inputs"]    = data
            save_json("students.json", students)
        else:
            final_score = profile["last_score"]
            grade = profile.get("last_grade", "—")
            remark = profile.get("last_remark", "—")
            saved_inputs = profile.get("last_inputs", {})
            hours = saved_inputs.get("Hours_Studied", 5)
            attendance = saved_inputs.get("Attendance", 75)
            previous = saved_inputs.get("Previous_Scores", 60)
            sleep = saved_inputs.get("Sleep_Hours", 7)
            motivation = saved_inputs.get("Motivation_Level", "Medium")
            teacher = saved_inputs.get("Teacher_Quality", "Average")
            school = saved_inputs.get("School_Type", "Public")
            internet = saved_inputs.get("Internet_Access", "Yes")

        st.markdown(f"""
        <div class="score-card">
            <div class="score-big">{final_score}</div>
            <div class="score-grade">Grade: {grade}</div>
            <div class="score-remark">{remark}</div>
        </div>
        """, unsafe_allow_html=True)

        r1, r2 = st.columns(2, gap="large")
        with r1:
            fig = go.Figure(go.Indicator(
                mode="gauge+number", value=final_score,
                title={'text': "Performance Score", 'font': {'color': '#dce3f0', 'family': 'Syne', 'size': 15}},
                number={'font': {'color': '#00ffd5', 'family': 'Syne', 'size': 48}},
                gauge={
                    'axis': {'range': [0,100], 'tickcolor': '#4a5568', 'tickfont': {'color': '#6b7a99'}},
                    'bar': {'color': '#00ffd5', 'thickness': .28},
                    'bgcolor': 'rgba(0,0,0,0)', 'borderwidth': 0,
                    'steps': [
                        {'range': [0,40],  'color': 'rgba(255,94,122,.12)'},
                        {'range': [40,70], 'color': 'rgba(255,157,58,.12)'},
                        {'range': [70,100],'color': 'rgba(0,255,213,.1)'},
                    ],
                    'threshold': {'line': {'color': '#7c3aed', 'width': 4}, 'thickness': .82, 'value': final_score}
                }
            ))
            fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                font_color='#dce3f0', height=320, margin=dict(t=50,b=20,l=30,r=30))
            st.plotly_chart(fig, use_container_width=True)
        with r2:
            chart_data = pd.DataFrame({
                "Metric": ["Study Hours","Attendance","Prev Score","Sleep Hours"],
                "Value":  [hours, attendance, previous, sleep],
                "Max":    [24, 100, 100, 12]
            })
            bar_fig = px.bar(chart_data, x="Metric", y="Value",
                color="Value", color_continuous_scale=["#1a3a8f","#0072ff","#00ffd5"],
                title="Your Key Metrics Breakdown", text="Value")
            bar_fig.update_traces(marker_line_width=0, textposition='outside', textfont_color='#dce3f0')
            bar_fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                font_color='#dce3f0', height=320, title_font_family='Syne', title_font_size=14,
                coloraxis_showscale=False,
                xaxis=dict(gridcolor='rgba(255,255,255,.04)', tickfont_color='#9aa3b5'),
                yaxis=dict(gridcolor='rgba(255,255,255,.04)', tickfont_color='#9aa3b5'),
                margin=dict(t=50,b=20,l=20,r=20), bargap=0.35)
            st.plotly_chart(bar_fig, use_container_width=True)

        st.write("")
        pdf_bytes = None
        with st.spinner("Generating PDF report..."):
            try:
                from app import generate_pdf_report
                pdf_bytes = generate_pdf_report(
                    username=username, student_profile=profile,
                    hours=hours, attendance=attendance, previous=previous, sleep=sleep,
                    motivation=motivation, teacher=teacher, school=school, internet=internet,
                    final_score=final_score, grade=grade, remark=remark
                )
            except Exception as e:
                st.warning(f"Could not generate PDF report: {e}")

        if pdf_bytes:
            filename = f"EduPredict_{username}_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf"
            st.download_button(label="📄  Download PDF Report", data=pdf_bytes,
                file_name=filename, mime="application/pdf", use_container_width=True, key="student_dl_btn")


# ─────────────────────────────────────────────────────────────────────────
#  4. अभिभावक डैशबोर्ड (Parent Dashboard Function)
# ─────────────────────────────────────────────────────────────────────────

def show_parent_dashboard():
    username    = st.session_state.username
    parents     = load_json("parents.json")
    students    = load_json("students.json")
    users       = load_json("users.json")
    parent_info = parents.get(username, {})
    children    = parent_info.get("children", [])

    try:
        model   = joblib.load("student_model.pkl")
        columns = joblib.load("model_columns.pkl")
    except Exception as e:
        st.error(f"Failed to load model files: {e}")
        return

    show_profile_widget()

    # ── Sidebar ──
    st.sidebar.image("https://cdn-icons-png.flaticon.com/512/3135/3135755.png", width=80)
    st.sidebar.markdown(f"### 👋 {parent_info.get('full_name', username)}")
    st.sidebar.markdown(
        '<span style="background:rgba(124,58,237,.15);border:1px solid rgba(124,58,237,.3);'
        'color:#7c3aed;font-size:11px;font-weight:700;padding:3px 10px;border-radius:99px;'
        'text-transform:uppercase;letter-spacing:.8px;">Parent</span>',
        unsafe_allow_html=True)
    st.sidebar.markdown("---")
    st.sidebar.markdown("**📌 Your Children**")
    for child in children:
        cp    = students.get(child, {})
        last  = cp.get("last_score", "N/A")
        grade = cp.get("last_grade", "—")
        st.sidebar.caption(f"🎓 {cp.get('full_name', child)} — Score: {last} ({grade})")
    st.sidebar.markdown("---")
    if st.sidebar.button("🚪 Logout", key="parent_logout"):
        for k in ["logged_in", "username", "user_role"]:
            st.session_state[k] = False if k == "logged_in" else ""
        st.rerun()

    # ── Hero ──
    relation = parent_info.get("relation", "Parent")
    st.markdown(f"""
    <div class="dash-hero">
        <div class="dash-greeting">Parent Portal — {relation}</div>
        <div class="dash-title">Children <span class="acc">Overview</span></div>
        <div class="dash-sub">Monitor your child's predicted performance and academic inputs from one place</div>
    </div>
    """, unsafe_allow_html=True)

    # ── KPI ──
    k1, k2, k3, k4 = st.columns(4)
    with k1:
        st.markdown(f"""<div class="kpi-card"><div class="kpi-icon">👨‍👩‍👧</div>
            <div class="kpi-label">Linked Children</div><div class="kpi-sub">{len(children)} student(s)</div></div>""", unsafe_allow_html=True)
    with k2:
        avg_score    = "—"
        valid_scores = [students[c]["last_score"] for c in children if c in students and "last_score" in students[c]]
        if valid_scores:
            avg_score = int(sum(valid_scores) / len(valid_scores))
        st.markdown(f"""<div class="kpi-card"><div class="kpi-icon">📊</div>
            <div class="kpi-label">Avg Score</div><div class="kpi-sub">{avg_score} / 100</div></div>""", unsafe_allow_html=True)
    with k3:
        st.markdown("""<div class="kpi-card"><div class="kpi-icon">🧠</div>
            <div class="kpi-label">AI Predictions</div><div class="kpi-sub">ML-powered engine</div></div>""", unsafe_allow_html=True)
    with k4:
        st.markdown("""<div class="kpi-card"><div class="kpi-icon">⚡</div>
            <div class="kpi-label">Live Results</div><div class="kpi-sub">Real-time data</div></div>""", unsafe_allow_html=True)

    st.write("")

    # ── Add Child ──
    with st.expander("➕ Link Another Child's Account"):
        new_child = st.text_input("Child's Username", placeholder="Enter child's registered username", key="add_child_input")
        if st.button("Link Child", key="link_child_btn"):
            if not new_child:
                st.error("Please enter a username")
            elif new_child not in users:
                st.error("❌ No account found with that username")
            elif users[new_child].get("role") != "student":
                st.error("❌ That account is not a student account")
            elif new_child in children:
                st.warning("⚠️ Already linked")
            else:
                if username not in parents:
                    parents[username] = {"children": [], "full_name": username, "relation": "Guardian"}
                parents[username]["children"].append(new_child)
                save_json("parents.json", parents)
                if new_child not in students:
                    students[new_child] = {}
                students[new_child]["parent_username"] = username
                save_json("students.json", students)
                st.success(f"✅ {students.get(new_child, {}).get('full_name', new_child)} linked successfully!")
                st.rerun()

    st.write("")

    if not children:
        st.info("👨‍👩‍👧 No children linked yet. Use the panel above to link your child's account.")
        return

    if len(children) == 1:
        selected_child = children[0]
    else:
        child_options  = {students.get(c, {}).get("full_name", c): c for c in children}
        selected_name  = st.selectbox("Select Child to View", list(child_options.keys()))
        selected_child = child_options[selected_name]

    child_profile = students.get(selected_child, {})

    st.markdown(f"""
    <div class="profile-card">
        <div class="profile-name">🎓 {child_profile.get('full_name', selected_child)}</div>
        <div class="profile-detail">
            <span>Class:</span> {child_profile.get('class_grade','N/A')} &nbsp;|&nbsp;
            <span>Section:</span> {child_profile.get('section','N/A')} &nbsp;|&nbsp;
            <span>Roll No:</span> {child_profile.get('roll_no','N/A')} &nbsp;|&nbsp;
            <span>Age:</span> {child_profile.get('age','N/A')} &nbsp;|&nbsp;
            <span>School:</span> {child_profile.get('school_name','N/A')}
        </div>
    </div>
    """, unsafe_allow_html=True)

    if "last_score" in child_profile:
        st.markdown(f"""
        <div class="score-card" style="padding:24px 28px;">
            <div style="font-size:13px;color:#6b7a99;margin-bottom:8px;">Last Predicted Score</div>
            <div class="score-big" style="font-size:64px;">{child_profile['last_score']}</div>
            <div class="score-grade">Grade: {child_profile.get('last_grade','—')}</div>
            <div class="score-remark" style="font-size:13px;">Predicted on {child_profile.get('last_predicted','—')}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### 🔮 Run a New Prediction for This Child")
    st.caption("As a parent, you can run a prediction by entering your child's academic details:")

    # Inputs Form Container
    with st.form(f"parent_predict_form_{selected_child}"):
        col1, col2 = st.columns(2, gap="large")
        with col1:
            st.markdown('<div class="input-card"><div class="input-section-title">📐 Academic Inputs</div>', unsafe_allow_html=True)
            hours      = st.slider("📚 Hours Studied (per day)", 0, 24, 5, key=f"p_hours_{selected_child}")
            attendance = st.slider("🏫 Attendance (%)", 0, 100, 75,       key=f"p_att_{selected_child}")
            previous   = st.slider("📋 Previous Score", 0, 100, 60,       key=f"p_prev_{selected_child}")
            sleep      = st.slider("😴 Sleep Hours", 0, 12, 7,             key=f"p_sleep_{selected_child}")
            st.markdown('</div>', unsafe_allow_html=True)
        with col2:
            st.markdown('<div class="input-card"><div class="input-section-title">🎛️ Environmental Factors</div>', unsafe_allow_html=True)
            motivation = st.selectbox("💪 Motivation Level", ["Low","Medium","High"], key=f"p_mot_{selected_child}")
            teacher    = st.selectbox("👨‍🏫 Teacher Quality", ["Poor","Average","Good"], key=f"p_tq_{selected_child}")
            school_sel = st.selectbox("🏛️ School Type",      ["Public","Private"],     key=f"p_sc_{selected_child}")
            internet   = st.selectbox("🌐 Internet Access",   ["Yes","No"],              key=f"p_net_{selected_child}")
            st.markdown('</div>', unsafe_allow_html=True)

        predict_btn = st.form_submit_button(f"🚀  Predict Score for {child_profile.get('full_name', selected_child)}", use_container_width=True)

    if predict_btn:
        data = {
            "Hours_Studied": hours, "Attendance": attendance,
            "Previous_Scores": previous, "Sleep_Hours": sleep,
            "Motivation_Level": motivation, "Teacher_Quality": teacher,
            "School_Type": school_sel, "Internet_Access": internet
        }
        input_df = pd.DataFrame([data])
        input_df = pd.get_dummies(input_df)
        input_df = input_df.reindex(columns=columns, fill_value=0)
        prediction  = model.predict(input_df)
        final_score = max(40, min(100, int(round(prediction[0]))))

        grade  = ("A+" if final_score>=90 else "A" if final_score>=80 else
                  "B"  if final_score>=70 else "C" if final_score>=60 else "D")
        remark = ("Outstanding! 🌟" if final_score>=90 else "Excellent! 🎉" if final_score>=80 else
                  "Good Job! 👍"    if final_score>=70 else "Keep Going! 💪" if final_score>=60 else
                  "Need Improvement 📖")

        if selected_child not in students:
            students[selected_child] = {}
        students[selected_child]["last_score"]     = final_score
        students[selected_child]["last_grade"]     = grade
        students[selected_child]["last_remark"]    = remark
        students[selected_child]["last_predicted"] = datetime.now().strftime("%d %b %Y, %I:%M %p")
        students[selected_child]["last_inputs"]    = data
        save_json("students.json", students)

        st.markdown(f"""
        <div class="score-card">
            <div class="score-big">{final_score}</div>
            <div class="score-grade">Grade: {grade}</div>
            <div class="score-remark">{remark}</div>
        </div>
        """, unsafe_allow_html=True)

        r1, r2 = st.columns(2, gap="large")
        with r1:
            fig = go.Figure(go.Indicator(
                mode="gauge+number", value=final_score,
                title={'text': "Performance Score", 'font': {'color': '#dce3f0', 'family': 'Syne', 'size': 15}},
                number={'font': {'color': '#00ffd5', 'family': 'Syne', 'size': 48}},
                gauge={
                    'axis': {'range': [0,100], 'tickcolor': '#4a5568', 'tickfont': {'color': '#6b7a99'}},
                    'bar': {'color': '#00ffd5', 'thickness': .28},
                    'bgcolor': 'rgba(0,0,0,0)', 'borderwidth': 0,
                    'steps': [
                        {'range': [0,40],  'color': 'rgba(255,94,122,.12)'},
                        {'range': [40,70], 'color': 'rgba(255,157,58,.12)'},
                        {'range': [70,100],'color': 'rgba(0,255,213,.1)'},
                    ],
                    'threshold': {'line': {'color': '#7c3aed', 'width': 4}, 'thickness': .82, 'value': final_score}
                }
            ))
            fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                font_color='#dce3f0', height=320, margin=dict(t=50,b=20,l=30,r=30))
            st.plotly_chart(fig, use_container_width=True)
        with r2:
            chart_data = pd.DataFrame({
                "Metric": ["Study Hours","Attendance","Prev Score","Sleep Hours"],
                "Value":  [hours, attendance, previous, sleep],
                "Max":    [24, 100, 100, 12]
            })
            bar_fig = px.bar(chart_data, x="Metric", y="Value",
                color="Value", color_continuous_scale=["#1a3a8f","#0072ff","#00ffd5"],
                title=f"{child_profile.get('full_name', selected_child)}'s Key Metrics", text="Value")
            bar_fig.update_traces(marker_line_width=0, textposition='outside', textfont_color='#dce3f0')
            bar_fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                font_color='#dce3f0', height=320, title_font_family='Syne', title_font_size=14,
                coloraxis_showscale=False,
                xaxis=dict(gridcolor='rgba(255,255,255,.04)', tickfont_color='#9aa3b5'),
                yaxis=dict(gridcolor='rgba(255,255,255,.04)', tickfont_color='#9aa3b5'),
                margin=dict(t=50,b=20,l=20,r=20), bargap=0.35)
            st.plotly_chart(bar_fig, use_container_width=True)

        st.write("")
        pdf_bytes = None
        with st.spinner("Generating PDF report..."):
            try:
                from app import generate_pdf_report
                pdf_bytes = generate_pdf_report(
                    username=selected_child, student_profile=child_profile,
                    hours=hours, attendance=attendance, previous=previous, sleep=sleep,
                    motivation=motivation, teacher=teacher, school=school_sel, internet=internet,
                    final_score=final_score, grade=grade, remark=remark
                )
            except Exception as e:
                st.warning(f"Could not generate PDF report: {e}")
                
        if pdf_bytes:
            filename = f"EduPredict_{selected_child}_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf"
            st.download_button(label="📄  Download PDF Report", data=pdf_bytes,
                file_name=filename, mime="application/pdf",
                use_container_width=True, key=f"dl_{selected_child}")
