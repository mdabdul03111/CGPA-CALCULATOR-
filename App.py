#CGPA Calculator App with Existing CGPA Option

import streamlit as st 
import pandas as pd

#Set Streamlit page config

st.set_page_config(page_title="CGPA Calculator", layout="centered")

#Session state defaults

if "user_submitted" not in st.session_state: st.session_state.user_submitted = False if "user_data" not in st.session_state: st.session_state.user_data = {}

#Step 1: User Info

if not st.session_state.user_submitted: st.title("Welcome to CGPA Calculator") st.markdown("### Please fill in your details:")

name = st.text_input("Name")
college = st.text_input("College")
department = st.text_input("Department")
entry_type = st.selectbox("Entry Type", ["Regular", "Lateral", "Sandwich - Regular", "Sandwich - Lateral"])

existing_cgpa_q = st.radio("Do you have an existing CGPA?", ["No", "Yes"])

if st.button("Submit"):
    if all([name, college, department, entry_type, existing_cgpa_q]):
        st.session_state.user_data = {
            "Name": name,
            "College": college,
            "Department": department,
            "EntryType": entry_type,
            "HasExistingCGPA": existing_cgpa_q == "Yes"
        }
        st.session_state.user_submitted = True
    else:
        st.warning("Please fill all fields before proceeding.")

#Step 2: Handle CGPA Calculation Path

if st.session_state.user_submitted: user = st.session_state.user_data st.title("Welcome, {}!".format(user['Name'])) st.markdown("### CGPA Calculator")

# Determine semester range
entry = user["EntryType"]
if entry == "Regular":
    sem_start, sem_end = 1, 8
elif entry == "Lateral":
    sem_start, sem_end = 3, 8
elif entry == "Sandwich - Regular":
    sem_start, sem_end = 1, 10
else:  # Sandwich - Lateral
    sem_start, sem_end = 3, 10

if user["HasExistingCGPA"]:
    completed_semester = st.number_input("Upto which semester do you have CGPA?", min_value=sem_start, max_value=sem_end, step=1)
    existing_cgpa = st.number_input("Enter your existing CGPA", min_value=1.0, max_value=10.0, step=0.01, format="%.2f")
    earned_credits = st.number_input("Total credits earned up to that semester", min_value=1, step=1)
    sem_start = int(completed_semester) + 1

sem_count = sem_end - sem_start + 1

if sem_count < 1:
    st.warning("You have already entered CGPA for all semesters. Nothing more to calculate.")
    st.stop()

sem_limit = st.slider("Select number of semesters you want to enter", min_value=1, max_value=sem_count, value=sem_count)

records = []
for sem in range(sem_start, sem_start + sem_limit):
    with st.expander(f"Semester {sem}"):
        num_courses = st.number_input(f"Number of Courses in Semester {sem}", min_value=1, value=5, step=1, key=f"courses_{sem}")
        for course in range(1, num_courses + 1):
            col1, col2 = st.columns(2)
            with col1:
                credit = st.selectbox(f"Course {course} Credit (0–4)", options=[0,1,2,3,4], key=f"credit_{sem}_{course}")
            with col2:
                score = st.selectbox(f"Course {course} Score (5–10)", options=list(range(5, 11)), key=f"score_{sem}_{course}")
            records.append({"Semester": sem, "Credit": credit, "Score": score})

if st.button("Calculate CGPA"):
    df = pd.DataFrame(records)
    df["Weighted"] = df["Credit"] * df["Score"]

    total_credits = df["Credit"].sum()
    total_weighted = df["Weighted"].sum()

    if user["HasExistingCGPA"]:
        overall_cgpa = (existing_cgpa * earned_credits + total_weighted) / (earned_credits + total_credits) if (earned_credits + total_credits) > 0 else 0
    else:
        overall_cgpa = total_weighted / total_credits if total_credits > 0 else 0

    sem_stats = (
        df.groupby("Semester")
        .agg(Credits=("Credit", "sum"), WeightedScore=("Weighted", "sum"))
        .reset_index()
    )
    sem_stats["GPA"] = sem_stats["WeightedScore"] / sem_stats["Credits"]

    def grade(score):
        return {10: "O", 9: "A+", 8: "A", 7: "B+", 6: "B", 5: "C"}.get(score, "")

    df["Grade"] = df["Score"].apply(grade)

    st.success(f"**Overall CGPA: {overall_cgpa:.2f}**")
    st.subheader("Semester-wise GPA")
    st.dataframe(sem_stats[["Semester", "Credits", "GPA"]])
    st.subheader("Detailed Course Breakdown")
    st.dataframe(df)

    html = f"""
    <html>
    <head>
    <style>
    body {{ font-family: Arial; margin: 40px; border: 3px solid #000; padding: 20px; }}
    h1, h2 {{ text-align: center; }}
    table {{ border-collapse: collapse; width: 100%; }}
    th, td {{ border: 1px solid black; padding: 8px; text-align: center; }}
    th {{ background-color: #f2f2f2; }}
    .page {{ page-break-after: always; }}
    .watermark {{ position: fixed; bottom: 10px; left: 10px; font-size: 10px; color: gray; }}
    </style>
    </head>
    <body>
    <div class="watermark">Disclaimer! This CGPA was calculated based on data fed by student</div>
    <h1>CGPA Report</h1>
    <p><strong>Name:</strong> {user['Name']}<br>
       <strong>College:</strong> {user['College']}<br>
       <strong>Department:</strong> {user['Department']}<br>
       <strong>Entry Type:</strong> {user['EntryType']}<br>
       <strong>Overall CGPA:</strong> {overall_cgpa:.2f}</p>
    <div class="page">
    <h2>Semester-wise GPA</h2>
    {sem_stats.to_html(index=False)}</div>
    """

    for sem in sorted(df['Semester'].unique()):
        sem_data = df[df['Semester'] == sem][["Credit", "Score", "Grade", "Weighted"]]
        html += f"<div class='page'><h2>Semester {sem} Breakdown</h2>"
        html += sem_data.to_html(index=False)
        html += "</div>"

    html += """
    <script>
    function printPage() {
        var w = window.open('', '_blank');
        w.document.write(document.documentElement.innerHTML);
        w.document.close();
        w.print();
    }
    </script>
    <button onclick="printPage()">Print Report</button>
    </body></html>
    """

    st.components.v1.html(html, height=800, scrolling=True)

            
