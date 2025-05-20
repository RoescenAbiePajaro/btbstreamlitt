import streamlit as st
from pymongo import MongoClient
import time
import subprocess

# MongoDB connection
client = MongoClient("mongodb://localhost:27017/")
db = client["beyond_the_brush"]
access_codes_collection = db["access_codes"]
students_collection = db["students"]


def register_student():
    st.set_page_config(
        page_title="Student Registration",
        page_icon="static/icons.png",
        layout="centered"
    )

    st.markdown("""
    <style>
    .stTextInput > div > div > input {
        color: white !important;
        background-color: rgba(30, 30, 47, 0.7) !important;
        padding: 12px !important;
        border-radius: 8px !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
    }
    .stButton > button {
        background: linear-gradient(90deg, #6a11cb 0%, #2575fc 100%);
        color: white;
        border: none;
        padding: 12px 28px;
        font-size: 16px;
        font-weight: 600;
        cursor: pointer;
        border-radius: 8px;
        transition: all 0.3s ease;
        width: 100%;
        margin-top: 1rem;
        box-shadow: 0 4px 15px rgba(106, 17, 203, 0.3);
    }
    .back-btn {
        position: fixed;
        bottom: 20px;
        right: 20px;
        z-index: 1000;
    }
    .back-btn button {
        background: linear-gradient(90deg, #6a11cb 0%, #2575fc 100%);
        color: white;
        border: none;
        padding: 10px 20px;
        font-size: 14px;
        font-weight: 600;
        cursor: pointer;
        border-radius: 8px;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(106, 17, 203, 0.3);
    }
    </style>
    """, unsafe_allow_html=True)

    st.title("Student Registration")

    with st.form("registration_form"):
        name = st.text_input("Full Name", placeholder="Enter your full name")
        access_code = st.text_input("Access Code", placeholder="Ask your educator for the access code")

        submitted = st.form_submit_button("Register")

        if submitted:
            if not name or not access_code:
                st.error("Please fill in all fields")
            else:
                # Check if access code exists in MongoDB
                code_data = access_codes_collection.find_one({"code": access_code})
                if code_data:
                    # Register student
                    student_data = {
                        "name": name,
                        "access_code": access_code,
                        "registered_at": time.time(),
                        "educator_id": code_data.get("educator_id", "")
                    }
                    students_collection.insert_one(student_data)
                    st.success("Registration successful! You can now log in.")
                else:
                    st.error("Invalid access code. Please ask your educator for a valid code.")

    # Add Back button
    if st.button("Back to Login", key="back_btn"):
        subprocess.Popen(["streamlit", "run", "app.py"])
        st.stop()


if __name__ == "__main__":
    register_student()