import streamlit as st
import time
from PIL import Image
import subprocess
import sys
import webbrowser
from pymongo import MongoClient

# MongoDB connection
client = MongoClient("mongodb://localhost:27017/")
db = client["beyond_the_brush"]
access_codes_collection = db["access_codes"]
students_collection = db["students"]  # Added students collection

# Set page config first
st.set_page_config(
    page_title="Beyond The Brush",
    page_icon="static/icons.png",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Constants
VIRTUAL_PAINTER_URL = "http://localhost:8501"

# Initialize global loading state
if 'is_loading' not in st.session_state:
    st.session_state.is_loading = False
if 'submitted' not in st.session_state:
    st.session_state.submitted = False
if 'role' not in st.session_state:
    st.session_state.role = "Student"
if 'access_granted' not in st.session_state:
    st.session_state.access_granted = False
if 'username' not in st.session_state:
    st.session_state.username = ""


def set_loading(loading: bool):
    st.session_state.is_loading = loading


def show_loading_screen(duration: float = 2.0):
    set_loading(True)
    st.markdown("<div class='loading-container'></div>", unsafe_allow_html=True)
    progress_bar = st.progress(0)
    steps = 100
    step_duration = duration / steps

    for percent_complete in range(steps):
        time.sleep(step_duration)
        progress_bar.progress(percent_complete + 1)

    progress_bar.empty()
    st.empty()
    set_loading(False)


def is_loading():
    return st.session_state.is_loading


def load_css():
    st.markdown("""
    <style>
    /* Main container styling */
    .main {
        background-color: #0E1117;
        color: white;
    }

    /* Input field styling */
    .stTextInput > div > div > input {
        color: white !important;
        background-color: rgba(30, 30, 47, 0.7) !important;
        padding: 12px !important;
        border-radius: 8px !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
    }

    /* Button styling */
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

    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(106, 17, 203, 0.4);
    }

    /* Radio button styling */
    .stRadio > div {
        display: flex;
        justify-content: center;
        gap: 2rem;
    }

    .stRadio > div > label {
        color: white !important;
        font-size: 16px;
    }

    /* Register button styling */
    .register-btn {
        position: fixed;
        bottom: 20px;
        right: 20px;
        z-index: 1000;
    }

    .register-btn button {
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

    /* Loading animation */
    .loading-container {
        display: flex;
        justify-content: center;
        align-items: center;
        height: 100vh;
    }

    /* Access code container */
    .access-code-container {
        margin: 2rem 0;
    }

    /* Title styling */
    h1, h2, h3 {
        text-align: center;
        color: white;
    }
    </style>
    """, unsafe_allow_html=True)


def show_entry_page():
    load_css()

    if st.session_state.access_granted:
        st.markdown("<h3>Application is launching...</h3>", unsafe_allow_html=True)
        return

    # Main content
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        try:
            logo = Image.open("static/icons.png")
            st.image(logo, width=200, use_column_width=False)
        except FileNotFoundError:
            st.warning("Application logo not found")

        st.markdown("<h1>Beyond The Brush</h1>", unsafe_allow_html=True)
        st.markdown("<h3>Select your role:</h3>", unsafe_allow_html=True)

        role = st.radio("", ("Student", "Educator"), index=0, label_visibility="collapsed", key="role_radio")
        st.session_state.role = role

        if role == "Student":
            st.markdown("<div class='access-code-container'>", unsafe_allow_html=True)
            st.markdown("<h3>Login</h3>", unsafe_allow_html=True)

            # Add username input
            name = st.text_input(
                "",
                label_visibility="collapsed",
                placeholder="Enter your name",
                key="name_input"
            )

            code = st.text_input(
                "",
                type="password",
                label_visibility="collapsed",
                placeholder="Enter your access code",
                key="access_code"
            )
            st.markdown("</div>", unsafe_allow_html=True)

            if st.button("LOGIN") or st.session_state.submitted:
                st.session_state.submitted = True
                verify_code(code, role.lower(), name)
        else:
            # Educator login with built-in code
            st.info("Educators: Use your admin access code")
            code = st.text_input(
                "",
                type="password",
                label_visibility="collapsed",
                placeholder="Enter admin access code",
                key="admin_code"
            )

            if st.button("LOGIN") or st.session_state.submitted:
                st.session_state.submitted = True
                verify_code(code, role.lower(), "")

    # Register button at the bottom
    if st.button("Register New Student", key="register_btn"):
        # Launch register.py in a new process
        subprocess.Popen(["streamlit", "run", "register.py"])
        # Close the current app
        st.stop()


def verify_code(entered_code, role, name):
    # Check both access codes and student registrations
    code_data = access_codes_collection.find_one({"code": entered_code})
    student_data = students_collection.find_one({"access_code": entered_code, "name": name})

    if role == "student":
        if student_data:
            st.session_state.access_granted = True
            st.session_state.username = name
            st.success("Access granted! Launching application...")
            show_loading_screen(1.5)
            launch_virtual_painter(role)
        else:
            st.error("Invalid name or access code. Please try again.")
    elif role == "educator" and code_data:
        st.session_state.access_granted = True
        st.success("Access granted! Launching application...")
        show_loading_screen(1.5)
        subprocess.Popen(["streamlit", "run", "educators.py"])
    else:
        st.error("Incorrect access code. Please try again.")


def launch_virtual_painter(role):
    st.session_state.access_granted = True
    if getattr(sys, 'frozen', False):
        subprocess.Popen([sys.executable, "VirtualPainter.py", role])
    else:
        subprocess.Popen([sys.executable, "-m", "streamlit", "run", "VirtualPainter.py", "--", role])
        time.sleep(1)

    st.markdown(
        f"""<meta http-equiv="refresh" content="0; url='{VIRTUAL_PAINTER_URL}'" />""",
        unsafe_allow_html=True
    )


def main():
    show_entry_page()


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--painter":
        import VirtualPainter

        if not st.session_state.get('access_granted', False):
            st.error("Access denied. Please authenticate through the main application.")
            st.stop()
        VirtualPainter.run_application(sys.argv[2] if len(sys.argv) > 2 else "student")
    else:
        main()