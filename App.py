import streamlit as st
import pandas as pd
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.units import inch
import tempfile
import os

# Set page config
st.set_page_config(page_title="CGPA Calculator", layout="centered")

# Function to get letter grade
def get_grade(score):
    if score == 10:
        return "O"
    elif score == 9:
        return "A+"
    elif score == 8:
        return "A"
    elif score == 7:
        return "B+"
    elif score == 6:
        return "B"
    else:
        return "RA"

# Create PDF
def generate_pdf(user_data, semesters):
    tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    c = canvas.Canvas(tmp_file.name, pagesize=A4)
    width, height = A4

    for i, (sem_no, sem_df) in enumerate(semesters.items()):
        c.setStrokeColorRGB(0, 0, 0)
        c.rect(20, 20, width - 40, height - 40)

        c.setFont("Helvetica-Bold", 14)
        if i == 0:
            c.drawCentredString(width / 2, height - 60, f"Welcome {user_data['Name']}")
            c.setFont("Helvetica", 12)
            c.drawString(50, height - 90, f"Name: {user_data['Name']}")
            c.drawString(50, height - 110, f"College: {user_data['College']}")
            c.drawString(50, height - 130, f"Department: {user_data['Department']}")
            c.drawString(50, height - 150, f"Entry Type: {user_data['Entry Type']}")

        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, height - 180 if i == 0 else height - 60, f"Semester {sem_no} Results:")

        table_data = [["Course", "Credit", "Score", "Grade"]]
        for j, row in sem_df.iterrows():
            table_data.append([
                f"Course {j+1}",
                row["Credit"],
                row["Score"],
                row["Grade"]
            ])

        # Draw table
        x_offset = 50
        y_offset = height - (210 if i == 0 else 90)
        row_height = 20
        col_widths = [100, 100, 100, 100]

        for row in table_data:
            for k, cell in enumerate(row):
                c.rect(x_offset + sum(col_widths[:k]), y_offset - row_height, col_widths[k], row_height)
                c.drawString(x_offset + sum(col_widths[:k]) + 5, y_offset - 15, str(cell))
            y_offset -= row_height

        gpa = round((sem_df["Credit"] * sem_df["Score"]).sum() / sem_df["Credit"].sum(), 2)
        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, y_offset - 30, f"GPA for Semester {sem_no}: {gpa}")

        c.setFont("Helvetica-Oblique", 10)
        c.setFillGray(0.5, 0.5)
        c.drawString(150, 30, "Disclaimer: CGPA was calculated based on the data fed by student")
        c.setFillColor(colors.black)
        c.showPage()

    c.save()
    return tmp_file.name

# State management
if "submitted" not in st.session_state:
    st.session_state.submitted = False

# User input
if not st.session_state.submitted:
    st.title("Welcome to CGPA Calculator")

    name = st.text_input("Name")
    college = st.text_input("College")
    department = st.text_input("Department")
    entry_type = st.selectbox("Entry Type", ["Regular", "Lateral", "Sandwich - Regular", "Sandwich - Lateral"])

    if st.button("Submit"):
        if name and college and department:
            st.session_state.user_data = {
                "Name": name,
                "College": college,
                "Department": department,
                "Entry Type": entry_type
            }
            st.session_state.submitted = True
        else:
            st.warning("Please fill all fields.")

# Semester input
if st.session_state.submitted:
    user = st.session_state.user_data
    st.title("CGPA Calculator")

    start_sem = 1
    max_sem = 8
    if user["Entry Type"] == "Lateral":
        start_sem = 3
    elif user["Entry Type"] == "Sandwich - Regular":
        max_sem = 10
    elif user["Entry Type"] == "Sandwich - Lateral":
        start_sem = 3
        max_sem = 10

    total_semesters = st.number_input("Number of Semesters", min_value=start_sem, max_value=max_sem, value=start_sem, step=1)
    
    semesters = {}
    total_credits = 0
    total_weighted = 0

    for sem in range(start_sem, total_semesters + 1):
        with st.expander(f"Semester {sem}"):
            num_courses = st.number_input(f"Number of Courses in Semester {sem}", min_value=1, value=5, step=1, key=f"ncourse_{sem}")
            records = []
            for i in range(num_courses):
                col1, col2 = st.columns(2)
                with col1:
                    credit = st.selectbox(f"Course {i+1} Credit", options=[1, 2, 3, 4], key=f"credit_{sem}_{i}")
                with col2:
                    score = st.selectbox(f"Course {i+1} Score", options=list(range(6, 11)), key=f"score_{sem}_{i}")
                grade = get_grade(score)
                records.append({"Credit": credit, "Score": score, "Grade": grade})
            sem_df = pd.DataFrame(records)
            semesters[sem] = sem_df
            total_credits += sem_df["Credit"].sum()
            total_weighted += (sem_df["Credit"] * sem_df["Score"]).sum()

    if st.button("Generate PDF Report"):
        overall_cgpa = round(total_weighted / total_credits, 2) if total_credits > 0 else 0.0
        st.success(f"Overall CGPA: {overall_cgpa}")
        
        pdf_path = generate_pdf(user, semesters)
        with open(pdf_path, "rb") as f:
            st.download_button("Download CGPA PDF", f, file_name="cgpa_report.pdf", mime="application/pdf")

        os.remove(pdf_path)
