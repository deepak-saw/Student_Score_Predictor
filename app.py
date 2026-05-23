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
st.set_page_config(page_title="EduPredict AI | Premium Portal", page_icon="🎓", layout="wide", initial_sidebar_state="expanded")

GLOBAL_CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;800&family=Syne:wght@600;800&display=swap');
    
    html, body, [class*="css"]  {
        font-family: 'Inter', sans-serif;
    }
    
    h1, h2, h3, .dash-title, .profile-name, .kpi-label {
        font-family: 'Syne', sans-serif !important;
    }

    /* Auth Background & Box */
    .stApp {
        background-color: #0b1120;
        background-image: radial-gradient(circle at 50% 0%, #1e293b 0%, transparent 70%);
        color: #e2e8f0;
    }
    .auth-container {
        background: rgba(15, 23, 42, 0.8);
        backdrop-filter: blur(16px);
        padding: 40px;
        border-radius: 24px;
        border: 1px solid rgba(0, 255, 213, 0.15);
        box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
        max-width: 480px;
        margin: 20px auto;
        text-align: center;
    }

    /* Input Fields Customization */
    div[data-baseweb="input"] > div {
        background-color: rgba(30, 41, 59, 0.7) !important;
        border: 1px solid rgba(148, 163, 184, 0.2) !important;
        border-radius: 12px !important;
    }
    
    /* Hero Section */
    .dash-hero {
        background: linear-gradient(135deg, rgba(14, 165, 233, 0.15), rgba(16, 185, 129, 0.05));
        border: 1px solid rgba(56, 189, 248, 0.2);
        padding: 35px 40px;
        border-radius: 24px;
        margin-bottom: 30px;
        position: relative;
        overflow: hidden;
    }
    .dash-hero::before {
        content: ''; position: absolute; top: -50%; left: -50%; width: 200%; height: 200%;
        background: radial-gradient(circle, rgba(56,189,248,0.1) 0%, transparent 60%);
        z-index: 0; pointer-events: none;
    }
    .dash-greeting { font-size: 14px; color: #38bdf8; text-transform: uppercase; letter-spacing: 2px; font-weight: 600; position: relative; z-index: 1;}
    .dash-title { font-size: 42px; color: #ffffff; margin: 10px 0; font-weight: 800; position: relative; z-index: 1;}
    .dash-title .acc { color: #34d399; }
    .dash-sub { color: #94a3b8; font-size: 16px; position: relative; z-index: 1;}

    /* Cards */
    .kpi-card {
        background: rgba(30, 41, 59, 0.5);
        border: 1px solid rgba(255, 255, 255, 0.05);
        padding: 25px;
        border-radius: 20px;
        text-align: center;
        transition: all 0.3s ease;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    .kpi-card:hover { transform: translateY(-8px); border-color: rgba(52, 211, 153, 0.4); box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.2); }
    .kpi-icon { font-size: 32px; margin-bottom: 12px; }
    .kpi-label { color: #f8fafc; font-size: 18px; font-weight: 600; }
    .kpi-sub { color: #64748b; font-size: 13px; margin-top: 5px; }

    .input-card {
        background: rgba(30, 41, 59, 0.4);
        border: 1px solid rgba(255, 255, 255, 0.05);
        padding: 30px;
        border-radius: 20px;
        margin-bottom: 20px;
    }
    .input-section-title { color: #38bdf8; font-weight: 600; margin-bottom: 25px; font-size: 18px; display: flex; align-items: center; gap: 10px;}

    .score-card {
        background: linear-gradient(135deg, rgba(14, 165, 233, 0.2), rgba(16, 185, 129, 0.15));
        border: 1px solid rgba(52, 211, 153, 0.4);
        border-radius: 24px;
        padding: 40px;
        text-align: center;
        margin: 30px 0;
        box-shadow: 0 20px 40px -15px rgba(52, 211, 153, 0.2);
    }
    .score-big { font-size: 80px; font-weight: 800; color: #ffffff; font-family: 'Syne', sans-serif; line-height: 1; text-shadow: 0 0 20px rgba(52, 211, 153, 0.4);}
    .score-grade { font-size: 26px; color: #34d399; font-weight: 600; margin: 15px 0; text-transform: uppercase; letter-spacing: 2px;}
    .score-remark { font-size: 18px; color: #cbd5e1; }
    
    /* Buttons */
    .stButton>button {
        border-radius: 12px !important;
        font-weight: 600 !important;
        transition: all 0.3s !important;
    }
    .stButton>button:hover { transform: scale(1.02); }
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
if "auth_mode" not in st.session_state:
    st.session_state.auth_mode = "Login"
if "current_page" not in st.session_state:
    st.session_state.current_page = "Dashboard"

# ==========================================
# 2. PDF GENERATION LOGIC
# ==========================================
def generate_pdf_report(username, profile, data, final_score, grade, remark):
    pdf = FPDF()
    pdf.add_page()
    
    # Header
    pdf.set_font("Arial", 'B', 26)
    pdf.set_text_color(14, 165, 233)
    pdf.cell(200, 15, txt="EduPredict Performance Report", ln=True, align='C')
    pdf.set_font("Arial", 'I', 11)
    pdf.set_text_color(120, 120, 120)
    pdf.cell(200, 10, txt=f"Generated on: {datetime.now().strftime('%B %d, %Y - %I:%M %p')}", ln=True, align='C')
    pdf.line(10, 35, 200, 35)
    pdf.ln(15)
    
    # Profile Details
    pdf.set_font("Arial", 'B', 16)
    pdf.set_text_color(30, 41, 59)
    pdf.cell(200, 10, txt="Academic Profile", ln=True)
    pdf.set_font("Arial", '', 12)
    pdf.cell(200, 8, txt=f"Name: {profile.get('full_name', username)}", ln=True)
    pdf.cell(200, 8, txt=f"Class: {profile.get('class_grade', 'N/A')} | Roll No: {profile.get('roll_no', 'N/A')}", ln=True)
    pdf.cell(200, 8, txt=f"Institution: {profile.get('school_name', 'N/A')}", ln=True)
    pdf.ln(10)
    
    # Final Score Box
    pdf.set_fill_color(240, 248, 255)
    pdf.set_font("Arial", 'B', 18)
    pdf.cell(200, 15, txt=" AI Prediction Analysis ", ln=True, align='C', fill=True)
    pdf.set_font("Arial", 'B', 48)
    pdf.set_text_color(16, 185, 129)
    pdf.cell(200, 25, txt=f"{final_score}%", ln=True, align='C')
    
    pdf.set_font("Arial", 'B', 16)
    pdf.set_text_color(30, 41, 59)
    pdf.cell(200, 10, txt=f"Estimated Grade: {grade}", ln=True, align='C')
    pdf.set_font("Arial", 'I', 12)
    pdf.cell(200, 10, txt=f"Remarks: {remark}", ln=True, align='C')
    pdf.ln(15)

    # Breakdown
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(200, 10, txt="Factor Breakdown", ln=True)
    pdf.set_font("Arial", '', 12)
    
    inputs_text = [
        f"Daily Study Hours: {data.get('Hours_Studied')} hrs",
        f"School Attendance: {data.get('Attendance')}%",
        f"Previous Term Score: {data.get('Previous_Scores')}%",
        f"Average Sleep: {data.get('Sleep_Hours')} hrs",
        f"Self Motivation: {data.get('Motivation_Level')}",
        f"Teacher Assessment: {data.get('Teacher_Quality')}"
    ]
    
    for item in inputs_text:
        pdf.cell(200, 8, txt=f"* {item}", ln=True)
        
    pdf.ln(20)
    pdf.set_font("Arial", 'I', 9)
    pdf.set_text_color(150, 150, 150)
    pdf.cell(200, 10, txt="Disclaimer: This is an AI-generated predictive estimate based on provided parameters.", ln=True, align='C')

    return pdf.output(dest='S').encode('latin-1')

# ==========================================
# 3. AUTHENTICATION (LOGIN / SIGN UP)
# ==========================================
def show_auth_page():
    st.markdown("<h1 style='text-align:center; color:#38bdf8; font-size: 56px; margin-top:40px; font-weight:800;'>🎓 EduPredict AI</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; color:#94a3b8; margin-bottom: 30px; font-size:18px;'>Your Personal Academic Intelligence Platform</p>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        st.markdown("<div class='auth-container'>", unsafe_allow_html=True)
        
        # Segmented Control for Login/Signup
        mode = st.radio("Mode", ["Login", "Sign Up"], horizontal=True, label_visibility="collapsed", index=0 if st.session_state.auth_mode == "Login" else 1)
        st.session_state.auth_mode = mode
        
        st.write("")
        
        if st.session_state.auth_mode == "Login":
            st.markdown("<h3 style='color:#fff; margin-bottom: 20px;'>Welcome Back</h3>", unsafe_allow_html=True)
            l_user = st.text_input("Username", placeholder="Enter your username")
            l_pass = st.text_input("Password", type="password", placeholder="Enter your password")
            
            st.write("")
            if st.button("Secure Login", use_container_width=True, type="primary"):
                users = load_json("users.json")
                if l_user in users and users[l_user]["password"] == hash_password(l_pass):
                    st.session_state.logged_in = True
                    st.session_state.username = l_user
                    st.session_state.user_role = users[l_user]["role"]
                    st.session_state.current_page = "Dashboard"
                    st.rerun()
                else:
                    st.error("❌ Invalid Username or Password")
                    
        else:
            st.markdown("<h3 style='color:#fff; margin-bottom: 20px;'>Create Account</h3>", unsafe_allow_html=True)
            s_user = st.text_input("Choose Username", placeholder="e.g. deepak123")
            s_pass = st.text_input("Choose Password", type="password", placeholder="Minimum 5 characters")
            s_role = st.selectbox("I am registering as a:", ["student", "parent"])
            
            st.markdown("<hr style='border-color: rgba(255,255,255,0.1);'>", unsafe_allow_html=True)
            if s_role == "student":
                s_name = st.text_input("Full Name", placeholder="e.g. Deepak")
                s_age = st.number_input("Age", min_value=10, max_value=30, value=22)
                c1, c2 = st.columns(2)
                s_class = c1.text_input("Degree/Class", placeholder="e.g. BCA")
                s_school = c2.text_input("Institution", placeholder="e.g. Srinath University")
            else:
                p_name = st.text_input("Full Name (Parent)", placeholder="Enter your name")
                p_phone = st.text_input("Phone Number")
                p_relation = st.selectbox("Relation to Student", ["Father", "Mother", "Guardian"])

            st.write("")
            if st.button("Create Account", use_container_width=True, type="primary"):
                users = load_json("users.json")
                if s_user in users:
                    st.error("⚠️ Username already exists. Please choose another.")
                elif len(s_user) < 3 or len(s_pass) < 5:
                    st.warning("⚠️ Username (>3) and Password (>4) must be longer.")
                else:
                    # Save Credentials
                    users[s_user] = {"password": hash_password(s_pass), "role": s_role}
                    save_json("users.json", users)
                    
                    # Save Profile
                    if s_role == "student":
                        students = load_json("students.json")
                        students[s_user] = {
                            "full_name": s_name, "age": s_age, "class_grade": s_class,
                            "section": "", "roll_no": "", "school_name": s_school, "parent_username": ""
                        }
                        save_json("students.json", students)
                    else:
                        parents = load_json("parents.json")
                        parents[s_user] = {
                            "full_name": p_name, "phone": p_phone, "relation": p_relation, "children": []
                        }
                        save_json("parents.json", parents)
                    
                    st.success("✅ Account created! Redirecting to login...")
                    st.session_state.auth_mode = "Login"
                    st.rerun()
                    
        st.markdown("</div>", unsafe_allow_html=True)


# ==========================================
# 4. PREDICTION LOGIC HANDLER
# ==========================================
def get_prediction(data):
    try:
        model = joblib.load("student_model.pkl")
        columns = joblib.load("model_columns.pkl")
        input_df = pd.DataFrame([data])
        input_df = pd.get_dummies(input_df)
        input_df = input_df.reindex(columns=columns, fill_value=0)
        prediction = model.predict(input_df)
        return max(40, min(100, int(round(prediction[0]))))
    except:
        # Fallback Logic if model is missing
        base = 40
        base += (data["Hours_Studied"] / 24) * 20
        base += (data["Attendance"] / 100) * 25
        base += (data["Previous_Scores"] / 100) * 15
        if data["Motivation_Level"] == "High": base += 5
        if data["Internet_Access"] == "Yes": base += 2
        return max(40, min(100, int(base)))


# ==========================================
# 5. SIDEBAR NAVIGATION & PROFILE EDITOR
# ==========================================
def render_sidebar():
    st.sidebar.markdown(f"<h2 style='color:#38bdf8; text-align:center;'>🎓 EduPredict</h2>", unsafe_allow_html=True)
    st.sidebar.markdown("---")
    
    # Navigation
    st.session_state.current_page = st.sidebar.radio(
        "Navigation Menu",
        ["📊 Dashboard", "👤 My Profile"],
        index=0 if st.session_state.current_page == "Dashboard" else 1
    )
    
    st.sidebar.markdown("---")
    if st.sidebar.button("🚪 Logout", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.session_state.user_role = ""
        st.rerun()

def show_profile_editor(username, role):
    st.markdown("<div class='dash-hero'><div class='dash-title'>My <span class='acc'>Profile</span></div><div class='dash-sub'>Manage your personal and academic information here.</div></div>", unsafe_allow_html=True)
    
    if role == "student":
        students = load_json("students.json")
        profile = students.get(username, {})
        
        with st.form("edit_profile_form"):
            st.subheader("Edit Details")
            c1, c2 = st.columns(2)
            new_name = c1.text_input("Full Name", value=profile.get("full_name", ""))
            new_age = c2.number_input("Age", value=profile.get("age", 15))
            new_class = c1.text_input("Class/Degree", value=profile.get("class_grade", ""))
            new_section = c2.text_input("Section/Specialization", value=profile.get("section", ""))
            new_roll = c1.text_input("Roll Number", value=profile.get("roll_no", ""))
            new_school = c2.text_input("Institution Name", value=profile.get("school_name", ""))
            
            if st.form_submit_button("💾 Save Profile Changes", type="primary"):
                students[username].update({
                    "full_name": new_name, "age": new_age, "class_grade": new_class,
                    "section": new_section, "roll_no": new_roll, "school_name": new_school
                })
                save_json("students.json", students)
                st.success("✅ Profile updated successfully!")
                st.rerun()
                
    elif role == "parent":
        parents = load_json("parents.json")
        profile = parents.get(username, {})
        
        with st.form("edit_parent_profile"):
            st.subheader("Edit Details")
            c1, c2 = st.columns(2)
            new_name = c1.text_input("Full Name", value=profile.get("full_name", ""))
            new_phone = c2.text_input("Phone Number", value=profile.get("phone", ""))
            rel_options = ["Father", "Mother", "Guardian"]
            current_rel = profile.get("relation", "Guardian")
            new_rel = c1.selectbox("Relation", rel_options, index=rel_options.index(current_rel) if current_rel in rel_options else 2)
            
            if st.form_submit_button("💾 Save Profile Changes", type="primary"):
                parents[username].update({
                    "full_name": new_name, "phone": new_phone, "relation": new_rel
                })
                save_json("parents.json", parents)
                st.success("✅ Profile updated successfully!")
                st.rerun()


# ==========================================
# 6. STUDENT DASHBOARD
# ==========================================
def show_student_dashboard():
    username = st.session_state.username
    students = load_json("students.json")
    profile = students.get(username, {})

    # Hero
    st.markdown(f"""
    <div class="dash-hero">
        <div class="dash-greeting">Student Portal</div>
        <div class="dash-title">Performance <span class="acc">Analytics</span></div>
        <div class="dash-sub">Welcome back, {profile.get('full_name', username)}! Enter your latest academic details below.</div>
    </div>
    """, unsafe_allow_html=True)

    # Inputs Container
    with st.container():
        st.markdown("### 📊 Run Prediction Model")
        with st.form("student_predict"):
            col1, col2 = st.columns(2)
            with col1:
                st.markdown('<div class="input-card"><div class="input-section-title">📐 Academic Inputs</div>', unsafe_allow_html=True)
                hours = st.slider("📚 Hours Studied (per day)", 0, 24, 5)
                attendance = st.slider("🏫 Attendance (%)", 0, 100, 75)
                previous = st.slider("📋 Previous Term Score (%)", 0, 100, 60)
                sleep = st.slider("😴 Sleep Hours", 0, 12, 7)
                st.markdown('</div>', unsafe_allow_html=True)
            with col2:
                st.markdown('<div class="input-card"><div class="input-section-title">🎛️ Environmental Factors</div>', unsafe_allow_html=True)
                motivation = st.selectbox("💪 Self Motivation", ["Low", "Medium", "High"])
                teacher = st.selectbox("👨‍🏫 Teacher Quality", ["Poor", "Average", "Good"])
                school = st.selectbox("🏛️ Institution Type", ["Public", "Private"])
                internet = st.selectbox("🌐 Internet Access", ["Yes", "No"])
                st.markdown('</div>', unsafe_allow_html=True)

            predict_btn = st.form_submit_button("🚀 Analyze & Predict Score", use_container_width=True)

    if predict_btn or "last_score" in profile:
        st.markdown("---")
        st.markdown("### 🎯 Your Results")
        
        if predict_btn:
            data = {"Hours_Studied": hours, "Attendance": attendance, "Previous_Scores": previous, "Sleep_Hours": sleep,
                    "Motivation_Level": motivation, "Teacher_Quality": teacher, "School_Type": school, "Internet_Access": internet}
            
            final_score = get_prediction(data)
            grade = "A+" if final_score>=90 else "A" if final_score>=80 else "B" if final_score>=70 else "C" if final_score>=60 else "D"
            remark = "Outstanding performance! 🌟 Keep it up." if final_score>=85 else "Good progress! 👍 Focus a bit more on revisions." if final_score>=65 else "Need serious improvement 📖. Increase study hours."

            students[username].update({"last_score": final_score, "last_grade": grade, "last_remark": remark, "last_inputs": data})
            save_json("students.json", students)
        else:
            final_score = profile["last_score"]
            grade = profile.get("last_grade", "")
            remark = profile.get("last_remark", "")
            data = profile.get("last_inputs", {})
            hours, attendance, previous = data.get("Hours_Studied", 5), data.get("Attendance", 75), data.get("Previous_Scores", 60)

        # Show Score Card
        st.markdown(f"""
        <div class="score-card">
            <div class="score-big">{final_score}%</div>
            <div class="score-grade">Estimated Grade: {grade}</div>
            <div class="score-remark">{remark}</div>
        </div>
        """, unsafe_allow_html=True)

        # Visual Analytics (Plotly)
        c1, c2 = st.columns(2)
        with c1:
            chart_df = pd.DataFrame({"Exam": ["Previous Score", "Predicted Next Score"], "Score": [previous, final_score]})
            fig = px.bar(chart_df, x="Exam", y="Score", text="Score", color="Exam", color_discrete_sequence=["#94a3b8", "#34d399"], title="Growth Comparison")
            fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="#cbd5e1", showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
            
        with c2:
            st.markdown("#### 💡 AI Study Tips for You")
            if final_score > previous:
                st.success("✅ Your current routine is showing positive growth!")
            else:
                st.warning("⚠️ Your score might drop. Consider increasing study time.")
            
            if hours < 4: st.info("📚 Try to study at least 4-5 hours daily.")
            if attendance < 80: st.info("🏫 Improve your attendance to grasp concepts better.")
            if data.get("Sleep_Hours", 7) < 6: st.info("😴 Your sleep is low. Aim for 7-8 hours for better memory retention.")

        # PDF Download
        pdf_bytes = generate_pdf_report(username, profile, data, final_score, grade, remark)
        st.download_button("📄 Download Complete PDF Report", data=pdf_bytes, file_name=f"{username}_report.pdf", mime="application/pdf", use_container_width=True)


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

    st.markdown(f"""
    <div class="dash-hero">
        <div class="dash-greeting">Parent/Guardian Portal</div>
        <div class="dash-title">Student <span class="acc">Oversight</span></div>
        <div class="dash-sub">Monitor and predict academic performance for your dependents.</div>
    </div>
    """, unsafe_allow_html=True)

    # Link Child Section
    with st.expander("➕ Link a Student Account"):
        st.write("Enter the registered username of the student you wish to monitor.")
        new_child = st.text_input("Student Username")
        if st.button("Link Student Account", type="primary"):
            if new_child in users and users[new_child]["role"] == "student":
                if new_child not in children:
                    parents[username]["children"].append(new_child)
                    save_json("parents.json", parents)
                    if new_child in students:
                        students[new_child]["parent_username"] = username
                        save_json("students.json", students)
                    st.success(f"✅ Successfully linked {new_child}!")
                    st.rerun()
                else:
                    st.warning("This student is already linked to your account.")
            else:
                st.error("❌ Invalid student username.")

    if not children:
        st.info("No students linked yet. Please use the option above to link an account.")
        return

    st.markdown("---")
    # Select Child
    child_names = {students.get(c, {}).get("full_name", c): c for c in children}
    selected_name = st.selectbox("📌 Select Student Profile", list(child_names.keys()))
    selected_child = child_names[selected_name]
    child_profile = students.get(selected_child, {})

    st.markdown(f"""
    <div style="background: rgba(30, 41, 59, 0.6); padding: 20px; border-radius: 12px; border-left: 5px solid #38bdf8; margin-bottom:20px;">
        <h3 style="margin:0; color:#fff;">🎓 {child_profile.get('full_name', selected_child)}</h3>
        <p style="margin:5px 0 0; color:#cbd5e1;">Class: {child_profile.get('class_grade','N/A')} | School: {child_profile.get('school_name','N/A')}</p>
    </div>
    """, unsafe_allow_html=True)

    # Predict for Child
    with st.form(f"parent_predict_{selected_child}"):
        st.markdown(f"#### Run Assessment for {selected_name}")
        c1, c2, c3, c4 = st.columns(4)
        hours = c1.number_input("Study Hrs/Day", 0, 24, 5)
        attendance = c2.number_input("Attendance %", 0, 100, 75)
        previous = c3.number_input("Previous %", 0, 100, 60)
        sleep = c4.number_input("Sleep Hrs", 0, 12, 7)
        
        c5, c6, c7, c8 = st.columns(4)
        motivation = c5.selectbox("Motivation", ["Low", "Medium", "High"])
        teacher = c6.selectbox("Teacher Quality", ["Poor", "Average", "Good"])
        school = c7.selectbox("School Type", ["Public", "Private"])
        internet = c8.selectbox("Internet", ["Yes", "No"])

        if st.form_submit_button("🚀 Generate Prediction", type="primary", use_container_width=True):
            data = {"Hours_Studied": hours, "Attendance": attendance, "Previous_Scores": previous, "Sleep_Hours": sleep,
                    "Motivation_Level": motivation, "Teacher_Quality": teacher, "School_Type": school, "Internet_Access": internet}
            
            final_score = get_prediction(data)
            grade = "A+" if final_score>=90 else "A" if final_score>=80 else "B" if final_score>=70 else "C" if final_score>=60 else "D"
            remark = "Outstanding performance! 🌟" if final_score>=85 else "Good progress! 👍" if final_score>=65 else "Needs attention and improvement 📖."
            
            students[selected_child].update({"last_score": final_score, "last_grade": grade, "last_remark": remark, "last_inputs": data})
            save_json("students.json", students)
            st.rerun()

    # Show Last Result & PDF
    if "last_score" in child_profile:
        st.markdown(f"""
        <div class="score-card">
            <div style="color:#38bdf8; font-weight:600; margin-bottom:10px;">LATEST PREDICTION</div>
            <div class="score-big">{child_profile['last_score']}%</div>
            <div class="score-grade">Grade: {child_profile['last_grade']}</div>
            <div class="score-remark">{child_profile['last_remark']}</div>
        </div>
        """, unsafe_allow_html=True)
        
        data = child_profile["last_inputs"]
        pdf_bytes = generate_pdf_report(selected_child, child_profile, data, child_profile['last_score'], child_profile['last_grade'], child_profile['last_remark'])
        st.download_button("📄 Download Academic Report PDF", data=pdf_bytes, file_name=f"{selected_child}_parent_report.pdf", mime="application/pdf", use_container_width=True)

# ==========================================
# MAIN APP ROUTING
# ==========================================
if not st.session_state.logged_in:
    show_auth_page()
else:
    render_sidebar()
    
    if st.session_state.current_page == "Dashboard":
        if st.session_state.user_role == "student":
            show_student_dashboard()
        elif st.session_state.user_role == "parent":
            show_parent_dashboard()
    elif st.session_state.current_page == "👤 My Profile":
        show_profile_editor(st.session_state.username, st.session_state.user_role)
