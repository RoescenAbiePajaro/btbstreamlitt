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
    page_icon="static/icons.png",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Constants
CORRECT_CODE = "12345"
VIRTUAL_PAINTER_URL = "http://localhost:8501"  # URL for the Virtual Painter app


# Custom CSS
def load_css():
    st.markdown(
        """
        <style>
        html {
            overflow-y: auto;
        }

        /* Loading screen */
        .loading-container {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            height: 5vh;
        }

        /* Progress bar */
        .stProgress > div > div > div > div {
            background: linear-gradient(90deg, #6a11cb 0%, #2575fc 100%);
            height: 10px;
            border-radius: 5px;
        }

        /* Logo styling */
        .logo {
            border-radius: 50%;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
        }

        /* Entry form container */
        .form-container {
            background: rgba(40, 40, 60, 0.8);
            padding: 2.5rem;
            border-radius: 15px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
            backdrop-filter: blur(8px);
            border: 1px solid rgba(255, 255, 255, 0.1);
            width: 100%;
            max-width: 500px;
            margin: 0 auto;
        }

        /* Radio buttons */
        .stRadio > div {
            background-color: rgba(30, 30, 47, 0.7);
            padding: 15px;
            border-radius: 10px;
            border: 1px solid rgba(255, 255, 255, 0.1);
        }

        /* Text input */
        .stTextInput > div > div > input {
            color: white !important;
            background-color: rgba(30, 30, 47, 0.7) !important;
            padding: 12px !important;
            border-radius: 8px !important;
            border: 1px solid rgba(255, 255, 255, 0.1) !important;
        }

        /* Placeholder styling */
        .stTextInput > div > div > input::placeholder {
            color: rgba(255, 255, 255, 0.6) !important;
            font-style: italic;
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

        /* Titles */
        h3 {
            color: white;
            text-align: center;
            margin-bottom: 1rem;
        }

        /* Success message */
        .stSuccess {
            background-color: rgba(46, 125, 50, 0.2) !important;
            border: 1px solid #2e7d32 !important;
            color: white !important;
        }

        /* Error message */
        .stError {
            background-color: rgba(198, 40, 40, 0.2) !important;
            border: 1px solid #c62828 !important;
            color: white !important;
        }

        /* Access code input container */
        .access-code-container {
            position: relative;
            margin: 1.5rem 0;
        }

        /* Access code label */
        .access-code-label {
            color: white;
            margin-bottom: 0.5rem;
            display: block;
            font-weight: 500;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def show_loading_screen():
    """Show a loading screen with progress bar"""
    st.markdown(
        """
        <div class="loading-container">
        </div>
        """,
        unsafe_allow_html=True,
    )

    progress_bar = st.progress(0)
    for percent_complete in range(100):
        time.sleep(0.02)
        progress_bar.progress(percent_complete + 1)

    progress_bar.empty()
    st.empty()


def show_entry_page():
    """Show the main entry page with role selection and code entry"""
    load_css()

    # Display logo in a centered column
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        try:
            logo = Image.open("static/icons.png")
            st.image(logo, width=200, use_container_width=False)
        except FileNotFoundError:
            st.warning("Application logo not found")

    # Main container
    col1, col2, col3 = st.columns([1, 3, 1])
    with col2:
        st.markdown("<h3>Select your role:</h3>", unsafe_allow_html=True)
        role = st.radio("", ("Student", "Educator"), index=0, label_visibility="collapsed")

        # New access code input with placeholder
        st.markdown("<div class='access-code-container'>", unsafe_allow_html=True)
        st.markdown("<h3>Enter Access Code:</h3>", unsafe_allow_html=True)
        code = st.text_input(
            "",
            type="password",
            label_visibility="collapsed",
            placeholder="Enter your 5-digit access code"
        )
        st.markdown("</div>", unsafe_allow_html=True)

        if st.button("ENTER"):
            verify_code(code, role.lower())


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
        # Start VirtualPainter using streamlit
        subprocess.Popen([sys.executable, "-m", "streamlit", "run", "VirtualPainter.py", "--", role])
        time.sleep(1)  # Small delay to ensure server starts


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