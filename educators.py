import streamlit as st
import subprocess
import time
import os
from dotenv import load_dotenv
from pymongo import MongoClient
from contextlib import contextmanager

# Load environment variables
load_dotenv()

st.set_page_config(
    page_title="Educator Portal",
    page_icon="static/icons.png",
    layout="wide"
)

# Add loading screen CSS
st.markdown(
    """
    <style>
    /* Progress bar */
    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, #6a11cb 0%, #2575fc 100%);
        height: 10px;
        border-radius: 5px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


@contextmanager
def get_mongodb_connection():
    """Context manager for MongoDB connection"""
    client = None
    try:
        MONGODB_URI = os.getenv("MONGODB_URI")
        if not MONGODB_URI:
            raise ValueError("MONGODB_URI environment variable is not set")

        client = MongoClient(MONGODB_URI)
        # Test the connection
        client.admin.command('ping')
        db = client["beyond_the_brush"]
        students_collection = db["students"]
        access_codes_collection = db["access_codes"]
        yield students_collection, access_codes_collection
    except Exception as e:
        st.error(f"Failed to connect to MongoDB: {str(e)}")
        st.stop()
    finally:
        if client:
            client.close()


def clear_session_state():
    """Clear all session state variables"""
    for key in list(st.session_state.keys()):
        del st.session_state[key]


def admin_portal():
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Go to", ["Student Registrations", "Access Codes", "Virtual Painter"])

    # Add logout button at the bottom of sidebar
    st.sidebar.markdown("---")  # Add a separator
    if st.sidebar.button("Logout"):
        clear_session_state()
        st.markdown(
            """
            <meta http-equiv="refresh" content="0; url='http://localhost:8501/'" />
            """,
            unsafe_allow_html=True
        )

    if page == "Student Registrations":
        st.title("Student Registrations")

        with get_mongodb_connection() as (students_collection, _):
            # Display all registered students
            students = list(students_collection.find())

            if students:
                for student in students:
                    col1, col2, col3 = st.columns([4, 1, 1])
                    with col1:
                        st.write(f"**{student['name']}** (Registered: {time.ctime(student['registered_at'])})")
                    with col2:
                        if st.button(f"Edit {student['name']}", key=f"edit_{student['_id']}"):
                            st.session_state['editing_student'] = student['_id']
                    with col3:
                        if st.button(f"Delete {student['name']}", key=f"delete_{student['_id']}"):
                            students_collection.delete_one({"_id": student["_id"]})
                            st.rerun()

                # Show edit form if a student is being edited
                if 'editing_student' in st.session_state:
                    student_to_edit = next((s for s in students if s['_id'] == st.session_state['editing_student']),
                                           None)
                    if student_to_edit:
                        with st.form(key=f"edit_form_{student_to_edit['_id']}"):
                            new_name = st.text_input("New Name", value=student_to_edit['name'])
                            submit_edit = st.form_submit_button("Save Changes")
                            cancel_edit = st.form_submit_button("Cancel")

                            if submit_edit and new_name:
                                students_collection.update_one(
                                    {"_id": student_to_edit["_id"]},
                                    {"$set": {"name": new_name}}
                                )
                                del st.session_state['editing_student']
                                st.success("Student information updated successfully!")
                                st.rerun()

                            if cancel_edit:
                                del st.session_state['editing_student']
                                st.rerun()
            else:
                st.info("No students registered yet.")

    elif page == "Access Codes":
        st.title("Access Codes Management")

        with get_mongodb_connection() as (_, access_codes_collection):
            # Display existing access codes
            codes = list(access_codes_collection.find())

            if codes:
                for code in codes:
                    col1, col2 = st.columns([4, 1])
                    with col1:
                        st.write(f"Code: {code['code']} (Created by: {code.get('educator_id', 'System')})")
                    with col2:
                        if st.button(f"Delete {code['code']}", key=f"del_code_{code['_id']}"):
                            access_codes_collection.delete_one({"_id": code["_id"]})
                            st.rerun()

            # Add new access code
            with st.form("add_code_form"):
                new_code = st.text_input("New Access Code")
                submit_code = st.form_submit_button("Add Code")
                if submit_code and new_code:
                    # Check if code already exists
                    existing_code = access_codes_collection.find_one({"code": new_code})
                    if existing_code:
                        st.warning(f"Access code '{new_code}' already exists!")
                    else:
                        access_codes_collection.insert_one({
                            "code": new_code,
                            "created_at": time.time(),
                            "educator_id": "Admin"
                        })
                        st.rerun()

    elif page == "Virtual Painter":
        st.title("Virtual Painter")
        st.info("Virtual Painter functionality has been moved to a separate module.")


if __name__ == "__main__":
    admin_portal()