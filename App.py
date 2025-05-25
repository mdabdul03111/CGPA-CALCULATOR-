#Import necessary libraries

import streamlit as st 
import pandas as pd

#Set Streamlit page configuration

st.set_page_config(page_title="CGPA Calculator", layout="centered")

#Initialize session state

if "user_submitted" not in st.session_state: st.session_state.user_submitted = False

if "has_existing_cgpa" not in st.session_state: st.session_state.has_existing_cgpa = False

#Step 1: User Info Input

if not st.session_state.user_submitted: st.title("Welcome to CGPA Calculator") st.markdown("### Please fill in your details:")

name = st.text_input("Name")
college = st.text_input("College")
department = st.text_input("Department")

# Select type of entry
entry_type = st.selectbox("Entry Type", ["Regular", "Lateral", "Sandwich - Regular", "Sandwich - Lateral"])

# Ask if user has existing CGPA (not included in PDF)
existing_cgpa_answer = st.radio("Do you already have a CGPA?", ["No", "Yes"])

if st.button("Submit"):
    if all([name, college, department, entry_type]):
        st.session_state.user_data = {
            "Name": name,
            "College": college,
            "Department": department,
            "EntryType": entry_type,
            "ExistingCGPA": existing_cgpa_answer == "Yes"
        }
        st.session_state.user_submitted = True
        st.session_state.has_existing_cgpa = existing_cgpa_answer == "Yes"
    else:
        st.warning("Please fill all fields before proceeding.")

Step 2: Existing CGPA Input (if applicable)

if st.session_state.user_submitted and st.session_state.has_existing_cgpa and "existing_info_submitted" not in st.session_state: st.title("Existing CGPA Info") max_semester = 8 if "Sandwich" not in st.session_state.user_data["EntryType"] else 10

completed_semesters = st.slider("How many semesters have you completed?", min_value=1, max_value=max_semester)
existing_cgpa = st.number_input("Enter your existing CGPA", min_value=0.0, max_value=10.0, format="%0.2f")
existing_credits = st.number_input("Enter total credits earned so far", min_value=1, step=1)

if st.button("Proceed to Remaining Semesters"):
    st.session_state.completed_semesters = completed_semesters
    st.session_state.existing_cgpa = existing_cgpa
    st.session_state.existing_credits = existing_credits
    st.session_state.existing_info_submitted = True

Step 3: CGPA Calculator Page

if st.session_state.user_submitted and (not st.session_state.has_existing_cgpa or "existing_info_submitted" in st.session_state): st.title("Welcome to the CGPA Calculator")

user = st.session_state.user_data

# Determine semester range
if user["EntryType"] == "Regular":
    sem_start = 1
    sem_max = 8
elif user["EntryType"] == "Lateral":
    sem_start = 3
    sem_max = 8
elif user["EntryType"] == "Sandwich - Regular":
    sem_start = 1
    sem_max = 10
else:  # Sandwich - Lateral
    sem_start = 3
    sem_max = 10

if st.session_state.has_existing_cgpa:
    sem_start = st.session_state.completed_semesters + 1
    sem_max = sem_max

# Allow user to reduce the number of semesters
total_semesters = st.slider("Number of Semesters to Enter", min_value=1, max_value=sem_max - sem_start + 1, value=sem_max - sem_start + 1)

# Collect data per semester
records = []
for sem in range(sem_start, sem_start + total_semesters):
    with st.expander(f"Semester {sem}"):
        num_courses = st.number_input(
            f"Number of Courses in Semester {sem}",
            min_value=1,
            step=1,
            value=5,
            key=f"courses_{sem}"
        )
        for course in range(1, num_courses + 1):
            col1, col2 = st.columns(2)
            with col1:
                credit = st.selectbox(
                    f"Course {course} Credit (0–4)",
                    options=[0, 1, 2, 3, 4],
                    key=f"credit_{sem}_{course}"
                )
            with col2:
                score = st.selectbox(
                    f"Course {course} Score (5–10)",
                    options=list(range(5, 11)),
                    key=f"score_{sem}_{course}"
                )
            records.append({"Semester": sem, "Credit": credit, "Score": score})

if st.button("Calculate CGPA"):
    df = pd.DataFrame(records)
    df["Weighted"] = df["Credit"] * df["Score"]

    # Calculate total credits and weighted score
    total_credits = df["Credit"].sum()
    total_weighted = df["Weighted"].sum()

    if st.session_state.has_existing_cgpa:
        # Calculate updated CGPA using existing data
        prev_cgpa = st.session_state.existing_cgpa
        prev_credits = st.session_state.existing_credits
        overall_cgpa = (prev_cgpa * prev_credits + total_weighted) / (prev_credits + total_credits)
    else:
        overall_cgpa = total_weighted / total_credits if total_credits > 0 else 0.0

    # GPA per semester
    sem_stats = (
        df.groupby("Semester")
        .agg(Credits=("Credit", "sum"), WeightedScore=("Weighted", "sum"))
        .reset_index()
    )
    sem_stats["GPA"] = sem_stats["WeightedScore"] / sem_stats["Credits"]

    # Add grades
    def get_grade(score):
        return {10: "O", 9: "A+", 8: "A", 7: "B+", 6: "B", 5: "C"}.get(score, "F")
    df["Grade"] = df["Score"].apply(get_grade)

    st.success(f"**Overall CGPA: {overall_cgpa:.2f}**")
    st.subheader("Semester-wise GPA")
    st.dataframe(sem_stats[["Semester", "Credits", "GPA"]])

    st.subheader("Detailed Course Breakdown")
    st.dataframe(df)

    # Generate HTML for printable report
    html = f"""
    <html>
    <head>
        <style>
            @media print {{
                .page {{ page-break-after: always; border: 2px solid #000; padding: 30px; margin: 20px; }}
            }}
            body {{ font-family: Arial; margin: 40px; }}
            h1, h2 {{ text-align: center; }}
            .page {{ border: 2px solid black; padding: 20px; margin: 20px auto; max-width: 800px; }}
            table {{ border: 1px solid black; border-collapse: collapse; width: 100%; }}
            th, td {{ border: 1px solid black; padding: 8px; text-align: center; }}
            th {{ background-color: #f2f2f2; }}
            .watermark {{ position: fixed; bottom: 10px; right: 10px; opacity: 0.5; font-size: 12px; }}
        </style>
    </head>
    <body>
        <div class="page">
            <h1>CGPA Report</h1>
            <p><strong>Name:</strong> {user['Name']}<br>
               <strong>College:</strong> {user['College']}<br>
               <strong>Department:</strong> {user['Department']}<br>
               <strong>Entry Type:</strong> {user['EntryType']}<br>
               <strong>Overall CGPA:</strong> {overall_cgpa:.2f}</p>
        </div>
        <div class="page">
            <h2>Semester-wise GPA</h2>
            {sem_stats.to_html(index=False)}</div>
    """

    # Add semester-wise pages
    for sem in sorted(df['Semester'].unique()):
        html += f"<div class='page'><h2>Semester {sem} Breakdown</h2>"
        sem_data = df[df['Semester'] == sem][["Credit", "Score", "Grade", "Weighted"]]
        html += sem_data.to_html(index=False)
        html += "</div>"

    html += """
        <div class="watermark">Disclaimer! This CGPA was calculated based on data fed by student</div>
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

