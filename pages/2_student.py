import streamlit as st
from VirtualPainter import run as run_virtual_painter

# Check if user is authenticated as student
if not st.session_state.get('authenticated') or st.session_state.get('user_type') != 'student':
    st.error("Access denied. Please login as a student.")
    st.stop()

# Run the virtual painter for students
run_virtual_painter()