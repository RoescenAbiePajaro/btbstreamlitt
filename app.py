# app.py
import streamlit as st
import time
from PIL import Image
import subprocess
import sys
import webbrowser

# Set page config first
st.set_page_config(
    page_title="Beyond The Brush",
    page_icon="🎨",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Constants
CORRECT_CODE = "12345"
VIRTUAL_PAINTER_URL = "http://localhost:8080"  # URL for the Virtual Painter app

def show_loading_screen():
    """Show a loading screen with progress bar"""
    st.markdown(
        """
        <style>
        .stProgress > div > div > div > div {
            background-color: #3498db;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    # Centered layout
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        try:
            logo = Image.open("static/icons.png")
            st.image(logo, width=200)
        except FileNotFoundError:
            st.error("Logo image not found")

        progress_bar = st.progress(0)
        for percent_complete in range(100):
            time.sleep(0.02)
            progress_bar.progress(percent_complete + 1)

        progress_bar.empty()
        st.empty()

def show_entry_page():
    """Show the main entry page with role selection and code entry"""
    st.markdown(
        """
        <style>
        .stRadio > div {
            background-color: #383232;
            color: white;
            padding: 10px;
            border-radius: 10px;
        }
        .stTextInput > div > div > input {
            color: white;
            background-color: #383232;
            padding: 5px;
            border-radius: 5px;
        }
        .stButton > button {
            background-color: #ff00ff;
            color: white;
            border: none;
            padding: 10px 24px;
            font-size: 16px;
            cursor: pointer;
            border-radius: 8px;
            transition: 0.3s;
        }
        .stButton > button:hover {
            background-color: #cc00cc;
        }
        .center-container {
            display: flex;
            justify-content: center;
            align-items: center;
            flex-direction: column;
            padding-top: 20px;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    # Centered layout
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown('<div class="center-container">', unsafe_allow_html=True)

        try:
            logo = Image.open("logo.png")
            st.image(logo, width=200)
        except FileNotFoundError:
            pass  # Just skip if logo isn't found

        st.markdown("### Select your role:")
        role = st.radio("", ("Student", "Educator"), index=0)

        st.markdown("### Enter Access Code:")
        code = st.text_input("", type="password")

        if st.button("ENTER"):
            verify_code(code, role.lower())

        st.markdown('</div>', unsafe_allow_html=True)


def verify_code(entered_code, role):
    """Verify the access code and launch the program if correct"""
    if entered_code == CORRECT_CODE:
        st.success("Access granted! Launching application...")
        time.sleep(2)
        launch_virtual_painter(role)
    else:
        st.error("Incorrect access code. Please try again.")


def launch_virtual_painter(role):
    """Launch the VirtualPainter program with the selected role"""
    if getattr(sys, 'frozen', False):
        subprocess.Popen([sys.executable, "VirtualPainter.py", role])
    else:
        webbrowser.open_new_tab(VIRTUAL_PAINTER_URL)


def main():
    show_loading_screen()
    st.empty()
    show_entry_page()


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--painter":
        import VirtualPainter
        VirtualPainter.run_application(sys.argv[2] if len(sys.argv) > 2 else "student")
    else:
        main()
