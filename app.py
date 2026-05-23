import streamlit as st
import json
import os
import joblib
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import hashlib
from fpdf import FPDF

# ==========================================
# 0. PAGE CONFIG & GLOBAL CSS
# ==========================================
st.set_page_config(page_title="EduPredict AI | Dashboard", page_icon="🎓", layout="wide")

GLOBAL_CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;800&family=Syne:wght@600;800&display=swap');
    
    html, body, [class*="css"]  {
        font-family: 'Inter', sans-serif;
    }
    
    h1, h2, h3, .dash-title, .pd-name, .profile-name, .kpi-label {
        font-family: 'Syne', sans-serif !important;
    }

    /* Auth Forms Styling */
    .auth-box {
        background: rgba(25, 30, 45, 0.95);
        padding: 40px;
        border-radius: 20px;
        border: 1px solid rgba(0, 255, 213, 0.2);
        box-shadow: 0 10px 40px rgba(0, 0, 0, 0.5);
        max-width: 500px;
        margin: 0 auto;
    }
    
    /* Hero Section */
    .dash-hero {
        background: linear-gradient(135deg, rgba(0, 114, 255, 0.1), rgba(0, 255, 213, 0.05));
        border: 1px solid rgba(0, 255, 213, 0.2);
        padding: 30px 40px;
        border-radius: 20px;
        margin-bottom: 25px;
    }
    .dash-greeting { font-size: 14px; color: #00ffd5; text-transform: uppercase; letter-spacing: 1.5px; font-weight: 600;}
    .dash-title { font-size: 38px; color: #fff; margin: 5px 0 10px; font-weight: 800;}
    .dash-title .acc { color: #00ffd5; }
    .dash-sub { color: #9aa3b5; font-size: 15px; }

    /* Cards */
    .kpi-card {
        background: rgba(25, 30, 45, 0.6);
        border: 1px solid rgba(255, 255, 255, 0.05);
        padding: 20px;
        border-radius: 16px;
        text-align: center;
        transition: transform 0.2s;
    }
    .kpi-card:hover { transform: translateY(-5px); border-color: rgba(0, 255, 213, 0.3); }
    .kpi-icon { font-size: 28px; margin-bottom: 10px; }
    .kpi-label { color: #fff; font-size: 18px; font-weight: 600; }
    .kpi-sub { color: #6b7a99; font-size: 13px; margin-top: 5px; }

    .input-card {
        background: rgba(25, 30, 45, 0.6);
        border: 1px solid rgba(255, 255, 255, 0.05);
        padding: 25px;
        border-radius: 16px;
        margin-bottom: 20px;
    }
    .input-section-title { color: #00ffd5; font-weight: 600; margin-bottom: 20px; font-size: 16px; border-bottom: 1px solid rgba(0,255,213,0.2); padding-bottom: 10px;}

    .score-card {
        background: linear-gradient(135deg, rgba(0, 114, 255, 0.15), rgba(0, 255, 213, 0.15));
        border: 1px solid rgba(0, 255, 213, 0.4);
        border-radius: 20px;
        padding: 30px;
        text-align: center;
        margin-bottom: 25px;
        box-shadow: 0 10px 30px rgba(0, 255, 213, 0.1);
    }
    .score-big { font-size: 72px; font-weight: 800; color: #fff; font-family: 'Syne', sans-serif; line-height: 1; }
    .score-grade { font-size: 24px; color: #00ffd5; font-weight: 600; margin: 10px 0; }
    .score-remark { font-size: 16px; color: #dce3f0; }

    .profile-card {
        background: rgba(25, 30, 45, 0.8);
        border-left: 4px solid #00ffd5;
        padding: 15px 20px;
        border-radius: 8px;
        margin-bottom: 20px;
    }
    .profile-name { color: #fff; font-size: 18px; font-weight: 600; margin-bottom: 5px;}
    .profile-detail { color: #9aa3b5; font-size: 14px; }
    .profile-detail span { color: #00ffd5; font-weight: 600; }
</style>
"""
st.markdown(GLOBAL_CSS, unsafe_allow_html=True)


# ==========================================
# 1. UTILITIES & JSON DB
# ==========================================
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def load_json(path):
    if not os.path.exists(path):
        return {}
    with open(path, "r") as f:
        return json.load(f)

def save_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=2)

# Ensure DB files exist
for file in ["users.json", "students.json", "parents.json"]:
    if not os.path.exists(file):
        save_json(file, {})

# Session State Init
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.session_state.user_role = ""

# ==========================================
# 2. PDF GENERATION LOGIC
# ==========================================
def generate_pdf_report(username, student_profile, hours, attendance, previous, sleep, motivation, teacher, school, internet, final_score, grade, remark):
    pdf = FPDF()
    pdf.add_page()
    
    # Header
    pdf.set_font("Arial", 'B', 24)
    pdf.set_text_color(0, 114, 255)
    pdf.cell(200, 15, txt="EduPredict AI Report", ln=True, align='C')
    
    pdf.set_font("Arial", 'I', 12)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(200, 10, txt=f"Generated on: {datetime.now().strftime('%d %b %Y, %I:%M %p')}", ln=True, align='C')
    pdf.ln(10)
    
    # Student Details
    pdf.set_font("Arial", 'B', 16)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(200, 10, txt="Student Profile", ln=True)
    pdf.set_font("Arial", '', 12)
    pdf.cell(200, 8, txt=f"Name: {student_profile.get('full_name', username)}", ln=True)
    pdf.cell(200, 8, txt=f"Class: {student_profile.get('class_grade', 'N/A')} | Section: {student_profile.get('section', 'N/A')}", ln=True)
    pdf.cell(200, 8, txt=f"School: {student_profile.get('school_name', 'N/A')}", ln=True)
    pdf.ln(10)
    
    # Final Score Box
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt="Prediction Results", ln=True)
    pdf.set_font("Arial", 'B', 40)
    pdf.set_text_color(0, 150, 100)
    pdf.cell(200, 20, txt=f"{final_score} / 100", ln=True, align='C')
    pdf.set_font("Arial", 'B', 16)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(200, 10, txt=f"Grade: {grade}", ln=True, align='C')
    pdf.set_font("Arial", 'I', 12)
    pdf.cell(200, 10, txt=f"Remark: {remark}", ln=True, align='C')
    pdf.ln(15)

    # Inputs Details
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(200, 10, txt="Academic & Environmental Inputs", ln=True)
    pdf.set_font("Arial", '', 12)
    
    inputs_text = [
        f"Hours Studied: {hours} hrs/day",
        f"Attendance: {attendance}%",
        f"Previous Score: {previous}%",
        f"Sleep Hours: {sleep} hrs/day",
        f"Motivation Level: {motivation}",
        f"Teacher Quality: {teacher}",
        f"School Type: {school}",
        f"Internet Access: {internet}"
    ]
    
    for item in inputs_text:
        pdf.cell(200, 8, txt=f"- {item}", ln=True)
        
    pdf.ln(20)
    pdf.set_font("Arial", 'I', 10)
    pdf.set_text_color(150, 150, 150)
    pdf.cell(200, 10, txt="This is an AI-generated predictive report.", ln=True, align='C')

    return pdf.output(dest='S').encode('latin-1')

# ==========================================
# 3. AUTHENTICATION (LOGIN / SIGN UP)
# ==========================================
def show_auth_page():
    st.markdown("<h1 style='text-align:center; color:#00ffd5; font-size: 50px; margin-top:50px;'>🎓 EduPredict AI</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; color:#9aa3b5; margin-bottom: 40px;'>Predict, Analyze, and Improve Student Performance</p>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        tab1, tab2 = st.tabs(["🔒 Login", "📝 Sign Up"])
        
        # LOGIN TAB
        with tab1:
            st.markdown("<div class='auth-box'>", unsafe_allow_html=True)
            st.subheader("Welcome Back")
            l_user = st.text_input("Username", key="l_user")
            l_pass = st.text_input("Password", type="password", key="l_pass")
            
            if st.button("Login", use_container_width=True, type="primary"):
                users = load_json("users.json")
                if l_user in users and users[l_user]["password"] == hash_password(l_pass):
                    st.session_state.logged_in = True
                    st.session_state.username = l_user
                    st.session_state.user_role = users[l_user]["role"]
                    st.success("Login Successful!")
                    st.rerun()
                else:
                    st.error("Invalid Username or Password")
            st.markdown("</div>", unsafe_allow_html=True)

        # SIGN UP TAB
        with tab2:
            st.markdown("<div class='auth-box'>", unsafe_allow_html=True)
            st.subheader("Create an Account")
            s_user = st.text_input("Choose Username", key="s_user")
            s_pass = st.text_input("Choose Password", type="password", key="s_pass")
            s_role = st.selectbox("I am a:", ["student", "parent"], key="s_role")
            
            st.markdown("---")
            if s_role == "student":
                s_name = st.text_input("Full Name")
                s_age = st.number_input("Age", min_value=5, max_value=25, value=15)
                s_class = st.text_input("Class / Grade")
            else:
                p_name = st.text_input("Full Name (Parent)")
                p_phone = st.text_input("Phone Number")
                p_relation = st.selectbox("Relation to Student", ["Father", "Mother", "Guardian"])

            if st.button("Register Account", use_container_width=True, type="primary"):
                users = load_json("users.json")
                if s_user in users:
                    st.error("Username already exists. Please choose another.")
                elif len(s_user) < 3 or len(s_pass) < 4:
                    st.warning("Username (>3) and Password (>4) must be longer.")
                else:
                    # Save User Credentials
                    users[s_user] = {"password": hash_password(s_pass), "role": s_role}
                    save_json("users.json", users)
                    
                    # Save Profile Info
                    if s_role == "student":
                        students = load_json("students.json")
                        students[s_user] = {
                            "full_name": s_name, "age": s_age, "class_grade": s_class,
                            "section": "", "roll_no": "", "school_name": "", "parent_username": ""
                        }
                        save_json("students.json", students)
                    else:
                        parents = load_json("parents.json")
                        parents[s_user] = {
                            "full_name": p_name, "phone": p_phone, "relation": p_relation, "children": []
                        }
                        save_json("parents.json", parents)
                    
                    st.success("Account Created Successfully! Please login.")
            st.markdown("</div>", unsafe_allow_html=True)


# ==========================================
# 4. PROFILE WIDGET (TOP BAR)
# ==========================================
def show_profile_widget():
    username = st.session_state.username
    role = st.session_state.user_role
    students = load_json("students.json")
    parents = load_json("parents.json")

    profile = students.get(username, {}) if role == "student" else parents.get(username, {})
    full_name = profile.get("full_name", username)
    parts = full_name.strip().split()
    initials = (parts[0][0] + (parts[-1][0] if len(parts) > 1 else "")).upper() if parts else "??"

    colA, colB = st.columns([11, 1])
    with colB:
        if st.button(f"👤 {initials}", help="Sign Out"):
            st.session_state.logged_in = False
            st.session_state.username = ""
            st.session_state.user_role = ""
            st.rerun()


# ==========================================
# 5. PREDICTION LOGIC HANDLER
# ==========================================
def get_prediction(data):
    """
    Tries to load real model. If not found, uses a dummy logic
    so the app doesn't crash during testing.
    """
    try:
        model = joblib.load("student_model.pkl")
        columns = joblib.load("model_columns.pkl")
        input_df = pd.DataFrame([data])
        input_df = pd.get_dummies(input_df)
        input_df = input_df.reindex(columns=columns, fill_value=0)
        prediction = model.predict(input_df)
        return max(40, min(100, int(round(prediction[0]))))
    except:
        # Dummy Logic for Demonstration if model is missing
        base = 40
        base += (data["Hours_Studied"] / 24) * 20
        base += (data["Attendance"] / 100) * 25
        base += (data["Previous_Scores"] / 100) * 15
        if data["Motivation_Level"] == "High": base += 5
        if data["Internet_Access"] == "Yes": base += 2
        return max(40, min(100, int(base)))


# ==========================================
# 6. STUDENT DASHBOARD
# ==========================================
def show_student_dashboard():
    username = st.session_state.username
    students = load_json("students.json")
    profile = students.get(username, {})

    show_profile_widget()

    # Sidebar
    st.sidebar.markdown(f"### 👋 {profile.get('full_name', username)}")
    st.sidebar.caption("ROLE: STUDENT")
    st.sidebar.markdown("---")
    st.sidebar.success("Logged in successfully")

    # Hero
    st.markdown(f"""
    <div class="dash-hero">
        <div class="dash-greeting">Student Portal</div>
        <div class="dash-title">Performance <span class="acc">Dashboard</span></div>
        <div class="dash-sub">Enter your latest academic details to predict your next exam score.</div>
    </div>
    """, unsafe_allow_html=True)

    # Profile Bar
    st.markdown(f"""
    <div class="profile-card">
        <div class="profile-name">🎓 {profile.get('full_name', username)}</div>
        <div class="profile-detail">
            <span>Class:</span> {profile.get('class_grade','N/A')} |
            <span>Age:</span> {profile.get('age','N/A')} |
            <span>School:</span> {profile.get('school_name','Not Set')}
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Inputs
    with st.form("student_predict"):
        col1, col2 = st.columns(2)
        with col1:
            st.markdown('<div class="input-card"><div class="input-section-title">📐 Academic Inputs</div>', unsafe_allow_html=True)
            hours = st.slider("📚 Hours Studied (per day)", 0, 24, 5)
            attendance = st.slider("🏫 Attendance (%)", 0, 100, 75)
            previous = st.slider("📋 Previous Score (%)", 0, 100, 60)
            sleep = st.slider("😴 Sleep Hours", 0, 12, 7)
            st.markdown('</div>', unsafe_allow_html=True)
        with col2:
            st.markdown('<div class="input-card"><div class="input-section-title">🎛️ Environmental Factors</div>', unsafe_allow_html=True)
            motivation = st.selectbox("💪 Motivation", ["Low", "Medium", "High"])
            teacher = st.selectbox("👨‍🏫 Teacher Quality", ["Poor", "Average", "Good"])
            school = st.selectbox("🏛️ School Type", ["Public", "Private"])
            internet = st.selectbox("🌐 Internet Access", ["Yes", "No"])
            st.markdown('</div>', unsafe_allow_html=True)

        predict_btn = st.form_submit_button("🚀 Predict My Score", use_container_width=True)

    if predict_btn or "last_score" in profile:
        if predict_btn:
            data = {"Hours_Studied": hours, "Attendance": attendance, "Previous_Scores": previous, "Sleep_Hours": sleep,
                    "Motivation_Level": motivation, "Teacher_Quality": teacher, "School_Type": school, "Internet_Access": internet}
            
            final_score = get_prediction(data)
            grade = "A+" if final_score>=90 else "A" if final_score>=80 else "B" if final_score>=70 else "C" if final_score>=60 else "D"
            remark = "Outstanding! 🌟" if final_score>=90 else "Good Job! 👍" if final_score>=70 else "Need Improvement 📖"

            students[username].update({"last_score": final_score, "last_grade": grade, "last_remark": remark, "last_inputs": data})
            save_json("students.json", students)
        else:
            final_score = profile["last_score"]
            grade = profile.get("last_grade", "")
            remark = profile.get("last_remark", "")
            data = profile.get("last_inputs", {})
            hours, attendance, previous, sleep = data.get("Hours_Studied", 5), data.get("Attendance", 75), data.get("Previous_Scores", 60), data.get("Sleep_Hours", 7)
            motivation, teacher, school, internet = data.get("Motivation_Level", "Medium"), data.get("Teacher_Quality", "Average"), data.get("School_Type", "Public"), data.get("Internet_Access", "Yes")

        st.markdown(f"""
        <div class="score-card">
            <div class="score-big">{final_score}</div>
            <div class="score-grade">Grade: {grade}</div>
            <div class="score-remark">{remark}</div>
        </div>
        """, unsafe_allow_html=True)

        # PDF Download
        pdf_bytes = generate_pdf_report(username, profile, hours, attendance, previous, sleep, motivation, teacher, school, internet, final_score, grade, remark)
        st.download_button("📄 Download PDF Report", data=pdf_bytes, file_name=f"{username}_report.pdf", mime="application/pdf", use_container_width=True)


# ==========================================
# 7. PARENT DASHBOARD
# ==========================================
def show_parent_dashboard():
    username = st.session_state.username
    parents = load_json("parents.json")
    students = load_json("students.json")
    users = load_json("users.json")
    
    parent_info = parents.get(username, {})
    children = parent_info.get("children", [])

    show_profile_widget()

    st.sidebar.markdown(f"### 👋 {parent_info.get('full_name', username)}")
    st.sidebar.caption("ROLE: PARENT / GUARDIAN")
    st.sidebar.markdown("---")

    st.markdown(f"""
    <div class="dash-hero">
        <div class="dash-greeting">Parent Portal</div>
        <div class="dash-title">Children <span class="acc">Overview</span></div>
        <div class="dash-sub">Monitor and predict your child's academic performance.</div>
    </div>
    """, unsafe_allow_html=True)

    # Link Child Section
    with st.expander("➕ Link Your Child's Account"):
        new_child = st.text_input("Enter Child's Username")
        if st.button("Link Account"):
            if new_child in users and users[new_child]["role"] == "student":
                if new_child not in children:
                    parents[username]["children"].append(new_child)
                    save_json("parents.json", parents)
                    
                    if new_child in students:
                        students[new_child]["parent_username"] = username
                        save_json("students.json", students)
                    
                    st.success("✅ Child linked successfully!")
                    st.rerun()
                else:
                    st.warning("Child is already linked.")
            else:
                st.error("Invalid student username.")

    if not children:
        st.info("No children linked yet. Use the option above to link.")
        return

    # Select Child
    child_names = {students.get(c, {}).get("full_name", c): c for c in children}
    selected_name = st.selectbox("Select Child to View", list(child_names.keys()))
    selected_child = child_names[selected_name]
    child_profile = students.get(selected_child, {})

    st.markdown(f"""
    <div class="profile-card">
        <div class="profile-name">🎓 {child_profile.get('full_name', selected_child)}</div>
        <div class="profile-detail">Class: {child_profile.get('class_grade','N/A')} | Age: {child_profile.get('age','N/A')}</div>
    </div>
    """, unsafe_allow_html=True)

    # Predict for Child
    with st.form(f"parent_predict_{selected_child}"):
        st.markdown(f"**Run Prediction for {selected_name}**")
        c1, c2, c3, c4 = st.columns(4)
        hours = c1.number_input("Hours Studied", 0, 24, 5)
        attendance = c2.number_input("Attendance %", 0, 100, 75)
        previous = c3.number_input("Previous %", 0, 100, 60)
        sleep = c4.number_input("Sleep Hrs", 0, 12, 7)
        
        c5, c6, c7, c8 = st.columns(4)
        motivation = c5.selectbox("Motivation", ["Low", "Medium", "High"])
        teacher = c6.selectbox("Teacher Qty", ["Poor", "Average", "Good"])
        school = c7.selectbox("School Type", ["Public", "Private"])
        internet = c8.selectbox("Internet", ["Yes", "No"])

        if st.form_submit_button("🚀 Predict Score", use_container_width=True):
            data = {"Hours_Studied": hours, "Attendance": attendance, "Previous_Scores": previous, "Sleep_Hours": sleep,
                    "Motivation_Level": motivation, "Teacher_Quality": teacher, "School_Type": school, "Internet_Access": internet}
            
            final_score = get_prediction(data)
            grade = "A+" if final_score>=90 else "A" if final_score>=80 else "B" if final_score>=70 else "C" if final_score>=60 else "D"
            remark = "Outstanding! 🌟" if final_score>=90 else "Good Job! 👍" if final_score>=70 else "Need Improvement 📖"
            
            students[selected_child].update({"last_score": final_score, "last_grade": grade, "last_remark": remark, "last_inputs": data})
            save_json("students.json", students)
            st.rerun()

    # Show Last Result & PDF
    if "last_score" in child_profile:
        st.markdown(f"""
        <div class="score-card">
            <div class="score-big">{child_profile['last_score']}</div>
            <div class="score-grade">Grade: {child_profile['last_grade']}</div>
            <div class="score-remark">{child_profile['last_remark']}</div>
        </div>
        """, unsafe_allow_html=True)
        
        data = child_profile["last_inputs"]
        pdf_bytes = generate_pdf_report(selected_child, child_profile, data["Hours_Studied"], data["Attendance"], data["Previous_Scores"], data["Sleep_Hours"],
                                        data["Motivation_Level"], data["Teacher_Quality"], data["School_Type"], data["Internet_Access"], 
                                        child_profile['last_score'], child_profile['last_grade'], child_profile['last_remark'])
        st.download_button("📄 Download PDF Report", data=pdf_bytes, file_name=f"{selected_child}_report.pdf", mime="application/pdf", use_container_width=True)

# ==========================================
# MAIN APP ROUTING
# ==========================================
if not st.session_state.logged_in:
    show_auth_page()
else:
    if st.session_state.user_role == "student":
        show_student_dashboard()
    elif st.session_state.user_role == "parent":
        show_parent_dashboard()
