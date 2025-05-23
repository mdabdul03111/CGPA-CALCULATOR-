import streamlit as st
import pandas as pd
from fpdf import FPDF
import os
import yagmail
from dotenv import load_dotenv

# Load environment variables (for email credentials)
load_dotenv()

EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASS = os.getenv("EMAIL_PASS")

# Define session state to track form submission
if "form_submitted" not in st.session_state:
    st.session_state["form_submitted"] = False

# USER DETAILS FORM
if not st.session_state["form_submitted"]:
    st.title("User Information")

    with st.form("user_form"):
        name = st.text_input("Name")
        college = st.text_input("College")
        department = st.text_input("Department")
        mobile = st.text_input("Mobile Number")
        email = st.text_input("Email ID")

        submitted = st.form_submit_button("Continue to CGPA Calculator")
        if submitted:
            if all([name, college, department, mobile, email]):
                st.session_state.update({
                    "name": name,
                    "college": college,
                    "department": department,
                    "mobile": mobile,
                    "email": email,
                    "form_submitted": True
                })
            else:
                st.warning("Please fill in all fields before continuing.")

# CGPA CALCULATOR
if st.session_state["form_submitted"]:
    st.title("CGPA Calculator")

    total_semesters = st.number_input("Number of semesters", min_value=1, step=1, value=2)
    records = []

    for sem in range(1, total_semesters + 1):
        with st.expander(f"Semester {sem}"):
            num_courses = st.number_input(
                f"Courses in Semester {sem}", min_value=1, step=1, value=5, key=f"num_courses_{sem}"
            )
            for course in range(1, num_courses + 1):
                col1, col2 = st.columns(2)
                with col1:
                    credit = st.selectbox(
                        f"Sem {sem} - Course {course} Credit (0–4)",
                        options=[0, 1, 2, 3, 4],
                        key=f"credit_{sem}_{course}"
                    )
                with col2:
                    score = st.selectbox(
                        f"Sem {sem} - Course {course} Score (5–10)",
                        options=list(range(5, 11)),
                        key=f"score_{sem}_{course}"
                    )
                records.append({"Semester": sem, "Credit": credit, "Score": score})

    if st.button("Calculate CGPA and Generate PDF"):
        df = pd.DataFrame(records)
        df["Weighted"] = df["Credit"] * df["Score"]

        total_credits = df["Credit"].sum()
        total_weighted = df["Weighted"].sum()
        overall_cgpa = total_weighted / total_credits if total_credits > 0 else 0.0

        sem_stats = (
            df.groupby("Semester")
            .agg(Credits=("Credit", "sum"), WeightedScore=("Weighted", "sum"))
            .reset_index()
        )
        sem_stats["GPA"] = sem_stats["WeightedScore"] / sem_stats["Credits"]

        st.subheader("Overall Results")
        st.write(f"**Total Credits:** {total_credits}")
        st.write(f"**Overall CGPA:** {overall_cgpa:.2f}")
        st.dataframe(sem_stats)

        st.subheader("Detailed Breakdown")
        st.dataframe(df)

        # Generate PDF
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", "B", 16)
        pdf.cell(0, 10, "Score Sheet", ln=True, align="C")
        pdf.ln(10)

        # User details
        pdf.set_font("Arial", size=12)
        pdf.multi_cell(0, 10, f"Name: {st.session_state['name']}\nCollege: {st.session_state['college']}\nDepartment: {st.session_state['department']}\nMobile: {st.session_state['mobile']}\nEmail: {st.session_state['email']}")
        pdf.ln(10)

        # Semester data
        for sem in range(1, total_semesters + 1):
            pdf.add_page()
            pdf.set_font("Arial", "B", 14)
            pdf.cell(0, 10, f"Semester {sem}", ln=True, align="C")
            pdf.set_font("Arial", size=12)
            pdf.ln(5)
            pdf.cell(40, 10, "Credit", 1)
            pdf.cell(40, 10, "Score", 1)
            pdf.cell(40, 10, "Weighted", 1)
            pdf.ln()
            for record in df[df["Semester"] == sem].itertuples():
                pdf.cell(40, 10, str(record.Credit), 1)
                pdf.cell(40, 10, str(record.Score), 1)
                pdf.cell(40, 10, f"{record.Weighted:.2f}", 1)
                pdf.ln()
            sem_gpa = sem_stats[sem_stats["Semester"] == sem]["GPA"].values[0]
            pdf.ln(5)
            pdf.cell(0, 10, f"GPA for Semester {sem}: {sem_gpa:.2f}", ln=True)

        # Final CGPA
        pdf.add_page()
        pdf.set_font("Arial", "B", 16)
        pdf.cell(0, 10, "Overall CGPA", ln=True, align="C")
        pdf.set_font("Arial", size=12)
        pdf.ln(10)
        pdf.cell(0, 10, f"Total Credits: {total_credits}", ln=True)
        pdf.cell(0, 10, f"CGPA: {overall_cgpa:.2f}", ln=True)

        # Save PDF
        pdf_output = "cgpa_report.pdf"
        pdf.output(pdf_output)

        # Email the PDF
        try:
            yag = yagmail.SMTP(user=EMAIL_USER, password=EMAIL_PASS)
            yag.send(
                to=st.session_state["email"],
                subject="Your CGPA Score Sheet",
                contents="Please find your CGPA report attached.",
                attachments=pdf_output
            )
            st.success(f"CGPA PDF sent to {st.session_state['email']}")
        except Exception as e:
            st.error(f"Failed to send email: {e}")
