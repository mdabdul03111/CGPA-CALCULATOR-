import streamlit as st import pandas as pd from fpdf import FPDF import os import yagmail from dotenv import load_dotenv

Load email credentials

load_dotenv() EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS") EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")

def send_email(receiver_email, subject, body, pdf_path): try: yag = yagmail.SMTP(EMAIL_ADDRESS, EMAIL_PASSWORD) yag.send(to=receiver_email, subject=subject, contents=body, attachments=pdf_path) return True except Exception as e: st.error(f"Failed to send email: {e}") return False

Session state to control app flow

if "user_submitted" not in st.session_state: st.session_state.user_submitted = False

if not st.session_state.user_submitted: st.title("Student Information Form") name = st.text_input("Name") college = st.text_input("College") department = st.text_input("Department") mobile = st.text_input("Mobile Number") email = st.text_input("Email ID")

if st.button("Submit"):
    if name and college and department and mobile and email:
        st.session_state.user_data = {
            "Name": name,
            "College": college,
            "Department": department,
            "Mobile": mobile,
            "Email": email
        }
        st.session_state.user_submitted = True
    else:
        st.warning("Please fill in all fields.")

else: st.title("CGPA Calculator by Semester")

total_semesters = st.number_input("Number of semesters", min_value=1, step=1, value=2)
records = []

for sem in range(1, total_semesters + 1):
    with st.expander(f"Semester {sem}"):
        num_courses = st.number_input(
            f"Courses in Semester {sem}", min_value=1, step=1, value=5, key=f"num_courses_{sem}")
        for course in range(1, num_courses + 1):
            col1, col2 = st.columns(2)
            with col1:
                credit = st.selectbox(
                    f"Sem {sem} - Course {course} Credit Hours", options=[0, 1, 2, 3, 4], key=f"credit_{sem}_{course}")
            with col2:
                score = st.selectbox(
                    f"Sem {sem} - Course {course} Score", options=list(range(5, 11)), key=f"score_{sem}_{course}")
            records.append({"Semester": sem, "Credit": credit, "Score": score})

if st.button("Calculate CGPA"):
    df = pd.DataFrame(records)
    df["Weighted"] = df["Credit"] * df["Score"]

    total_credits = df["Credit"].sum()
    total_weighted = df["Weighted"].sum()
    overall_cgpa = total_weighted / total_credits if total_credits > 0 else 0.0

    sem_stats = df.groupby("Semester").agg(Credits=("Credit", "sum"), WeightedScore=("Weighted", "sum")).reset_index()
    sem_stats["GPA"] = sem_stats["WeightedScore"] / sem_stats["Credits"]

    st.success(f"Overall CGPA: {overall_cgpa:.2f}")
    st.dataframe(sem_stats)

    # Create PDF
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(200, 10, txt="Score Sheet", ln=True, align="C")

    pdf.set_font("Arial", "", 12)
    for key, value in st.session_state.user_data.items():
        pdf.cell(200, 10, txt=f"{key}: {value}", ln=True)

    pdf.add_page()
    for sem in range(1, total_semesters + 1):
        pdf.set_font("Arial", "B", 14)
        pdf.cell(200, 10, txt=f"Semester {sem}", ln=True)
        pdf.set_font("Arial", "", 12)
        pdf.cell(200, 10, txt="Credit | Score", ln=True)
        for record in df[df.Semester == sem].itertuples():
            pdf.cell(200, 10, txt=f"{record.Credit}     | {record.Score}", ln=True)
        pdf.add_page()

    pdf.output("cgpa_report.pdf")

    st.success("PDF generated!")
    with open("cgpa_report.pdf", "rb") as f:
        st.download_button("Download PDF", f, file_name="cgpa_report.pdf")

    if send_email(
        receiver_email=st.session_state.user_data['Email'],
        subject="Your CGPA Score Sheet",
        body="Dear student,\n\nPlease find attached your CGPA score sheet.\n\nBest regards,\nCGPA App",
        pdf_path="cgpa_report.pdf"
    ):
        st.success("PDF emailed successfully!")

