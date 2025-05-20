import streamlit as st
from pymongo import MongoClient
import subprocess
import time

# MongoDB connection with error handling
try:
    client = MongoClient("mongodb://localhost:27017/")
    db = client["beyond_the_brush"]
    students_collection = db["students"]
    access_codes_collection = db["access_codes"]
except Exception as e:
    st.error(f"Failed to connect to MongoDB: {str(e)}")
    st.stop()


def admin_portal():
    st.set_page_config(
        page_title="Educator Portal",
        page_icon="static/icons.png",
        layout="wide"
    )

    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Go to", ["Student Registrations", "Access Codes", "Virtual Painter"])

    # Add logout button at the bottom of sidebar
    st.sidebar.markdown("---")  # Add a separator
    if st.sidebar.button("Logout"):
        st.switch_page("app.py")

    if page == "Student Registrations":
        st.title("Student Registrations")

        # Display all registered students
        students = list(students_collection.find())

        if students:
            for student in students:
                col1, col2, col3 = st.columns([4, 1, 1])
                with col1:
                    st.write(f"**{student['name']}** (Registered: {time.ctime(student['registered_at'])})")
                with col2:
                    if st.button(f"Edit {student['name']}", key=f"edit_{student['_id']}"):
                        # Create a form for editing student details
                        with st.form(key=f"edit_form_{student['_id']}"):
                            new_name = st.text_input("New Name", value=student['name'])
                            submit_edit = st.form_submit_button("Save Changes")
                            if submit_edit and new_name:
                                students_collection.update_one(
                                    {"_id": student["_id"]},
                                    {"$set": {"name": new_name}}
                                )
                                st.success("Student information updated successfully!")
                                st.rerun()
                with col3:
                    if st.button(f"Delete {student['name']}", key=f"delete_{student['_id']}"):
                        students_collection.delete_one({"_id": student["_id"]})
                        st.rerun()
        else:
            st.info("No students registered yet.")

    elif page == "Access Codes":
        st.title("Access Codes Management")

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
                access_codes_collection.insert_one({
                    "code": new_code,
                    "created_at": time.time(),
                    "educator_id": "Admin"
                })
                st.rerun()

    elif page == "Virtual Painter":
        st.title("Launch Virtual Painter")
        if st.button("Open Virtual Painter"):
            subprocess.Popen(["streamlit", "run", "VirtualPainter.py"])


if __name__ == "__main__":
    admin_portal()