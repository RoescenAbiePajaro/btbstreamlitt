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
CORRECT_CODE = "hswh"
VIRTUAL_PAINTER_URL = "http://localhost:8501"  # URL for the Virtual Painter app

# Initialize global loading state
if 'is_loading' not in st.session_state:
    st.session_state.is_loading = False


def set_loading(loading: bool):
    """Set the global loading state"""
    st.session_state.is_loading = loading


def show_loading_screen(duration: float = 2.0):
    """Show a loading screen with progress bar

    Args:
        duration (float): Duration of the loading screen in seconds
    """
    set_loading(True)

    st.markdown(
        """
        <div class="loading-container">
        </div>
        """,
        unsafe_allow_html=True,
    )

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
    """Check if the application is currently in loading state"""
    return st.session_state.is_loading


# Custom CSS
def load_css():
    st.markdown(
        """
        <style>
        html {
            overflow-y: auto;
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

        /* Loading container */
        .loading-container {
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 200px;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def show_entry_page():
    """Show the main entry page with role selection and code entry"""
    load_css()

    # Initialize session state for form submission
    if 'submitted' not in st.session_state:
        st.session_state.submitted = False
    if 'role' not in st.session_state:
        st.session_state.role = "Student"
    if 'access_granted' not in st.session_state:
        st.session_state.access_granted = False

    # If access is granted, show a different view
    if st.session_state.access_granted:
        st.markdown("<h3>Application is launching...</h3>", unsafe_allow_html=True)
        return

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
        role = st.radio("", ("Student", "Educator"), index=0, label_visibility="collapsed", key="role_radio")
        st.session_state.role = role

        # New access code input with placeholder
        st.markdown("<div class='access-code-container'>", unsafe_allow_html=True)
        st.markdown("<h3>Enter Access Code:</h3>", unsafe_allow_html=True)
        code = st.text_input(
            "",
            type="password",
            label_visibility="collapsed",
            placeholder="Enter your 5-digit access code",
            key="access_code"
        )
        st.markdown("</div>", unsafe_allow_html=True)

        if st.button("ENTER") or st.session_state.submitted:
            st.session_state.submitted = True
            verify_code(code, role.lower())


def verify_code(entered_code, role):
    """Verify the access code and launch the program if correct"""
    if entered_code == CORRECT_CODE:
        # Store the success state
        st.session_state.access_granted = True
        st.success("Access granted! Launching application...")
        show_loading_screen(1.5)  # Show loading for 1.5 seconds
        launch_virtual_painter(role)
    else:
        st.error("Incorrect access code. Please try again.")


def launch_virtual_painter(role):
    """Launch the VirtualPainter program with the selected role"""
    # Set authentication state in session
    st.session_state.access_granted = True

    if getattr(sys, 'frozen', False):
        subprocess.Popen([sys.executable, "VirtualPainter.py", role])
    else:
        # Start VirtualPainter using streamlit
        subprocess.Popen([sys.executable, "-m", "streamlit", "run", "VirtualPainter.py", "--", role])
        time.sleep(1)  # Small delay to ensure server starts

    # Redirect to VirtualPainter URL
    st.markdown(
        f"""
        <meta http-equiv="refresh" content="0; url='{VIRTUAL_PAINTER_URL}'" />
        """,
        unsafe_allow_html=True
    )


def main():
    # Initialize session state for authentication
    if 'access_granted' not in st.session_state:
        st.session_state.access_granted = False

    show_entry_page()


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--painter":
        import VirtualPainter

        # Check authentication before running VirtualPainter
        if not st.session_state.get('access_granted', False):
            st.error("Access denied. Please authenticate through the main application.")
            st.stop()
        VirtualPainter.run_application(sys.argv[2] if len(sys.argv) > 2 else "student")
    else:
        main()