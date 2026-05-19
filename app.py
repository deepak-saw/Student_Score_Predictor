import streamlit as st
import joblib
import pandas as pd
import json
import os

# =========================
# USER FILE
# =========================
USER_FILE = "users.json"

# Create file if not exists
if not os.path.exists(USER_FILE):
    with open(USER_FILE, "w") as f:
        json.dump({}, f)

# =========================
# LOAD USERS
# =========================
def load_users():
    with open(USER_FILE, "r") as f:
        return json.load(f)

# =========================
# SAVE USERS
# =========================
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
# LOGIN / SIGNUP PAGE
# =========================
if not st.session_state.logged_in:

    st.title("🔐 Student Score Predictor Login System")

    menu = st.sidebar.selectbox("Menu", ["Login", "Sign Up"])

    users = load_users()

    # =========================
    # SIGN UP
    # =========================
    if menu == "Sign Up":

        st.subheader("Create New Account")

        new_user = st.text_input("Username")
        new_pass = st.text_input("Password", type="password")

        if st.button("Sign Up"):

            if new_user in users:
                st.error("⚠ Username already exists!")

            elif new_user == "" or new_pass == "":
                st.warning("Please enter username and password")

            else:
                users[new_user] = new_pass
                save_users(users)

                st.success("✅ Account created successfully!")
                st.info("Go to Login Page")

    # =========================
    # LOGIN
    # =========================
    elif menu == "Login":

        st.subheader("Login")

        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        if st.button("Login"):

            if username in users and users[username] == password:
                st.success("✅ Login Successful")

                st.session_state.logged_in = True
                st.session_state.username = username

                st.rerun()

            else:
                st.error("❌ Invalid Username or Password")

# =========================
# MAIN APP AFTER LOGIN
# =========================
else:

    # =========================
    # LOAD MODEL
    # =========================
    model = joblib.load("student_model.pkl")
    columns = joblib.load("model_columns.pkl")

    # =========================
    # SIDEBAR
    # =========================
    st.sidebar.success(f"👋 Welcome {st.session_state.username}")

    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.rerun()

    # =========================
    # TITLE
    # =========================
    st.title("🎓 Student Score Predictor")

    # =========================
    # INPUT FIELDS
    # =========================
    hours = st.number_input("Hours Studied", 0.0, 24.0)
    attendance = st.number_input("Attendance", 0.0, 100.0)
    previous = st.number_input("Previous Score", 0.0, 100.0)
    sleep = st.number_input("Sleep Hours", 0.0, 12.0)

    motivation = st.selectbox("Motivation Level", ["Low", "Medium", "High"])
    teacher = st.selectbox("Teacher Quality", ["Poor", "Average", "Good"])
    school = st.selectbox("School Type", ["Public", "Private"])
    internet = st.selectbox("Internet Access", ["Yes", "No"])
    income = st.selectbox("Family Income", ["Low", "Medium", "High"])
    parent = st.selectbox("Parental Involvement", ["Low", "Medium", "High"])
    education = st.selectbox("Parent Education", ["School", "College"])
    peer = st.selectbox("Peer Influence", ["Negative", "Neutral", "Positive"])
    resources = st.selectbox("Learning Resources", ["Low", "Medium", "High"])
    activities = st.selectbox("Extracurricular Activities", ["Yes", "No"])

    # =========================
    # PREDICTION BUTTON
    # =========================
    if st.button("Predict Score"):

        # Create input dictionary
        data = {
            "Hours_Studied": hours,
            "Attendance": attendance,
            "Previous_Scores": previous,
            "Sleep_Hours": sleep,

            "Motivation_Level": motivation,
            "Teacher_Quality": teacher,
            "School_Type": school,
            "Internet_Access": internet,
            "Family_Income": income,
            "Parental_Involvement": parent,
            "Parental_Education_Level": education,
            "Peer_Influence": peer,
            "Learning_Resources": resources,
            "Extracurricular_Activities": activities
        }

        # Convert to DataFrame
        input_df = pd.DataFrame([data])

        # Apply encoding
        input_df = pd.get_dummies(input_df)

        # Match training columns
        input_df = input_df.reindex(columns=columns, fill_value=0)

        # =========================
        # PREDICT
        # =========================
        prediction = model.predict(input_df)

        # =========================
        # FIX UNREALISTIC VALUES
        # =========================
        final_score = max(40, min(100, prediction[0]))

        # Convert to integer
        final_score = int(round(final_score))

        # =========================
        # OUTPUT
        # =========================
        st.success(f"🎯 Predicted Exam Score: {final_score}")
