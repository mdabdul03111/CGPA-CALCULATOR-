import streamlit as st
import pandas as pd

st.set_page_config(page_title="CGPA Calculator", layout="centered")

# Grade mapping
def get_grade(score):
    return {
        10: "O",
        9: "A+",
        8: "A",
        7: "B+",
        6: "B",
        5: "C"
    }.get(score, "RA")

# Entry type semester range
def get_semester_range(entry_type):
    if entry_type == "Regular":
        return 1, 8
    elif entry_type == "Lateral":
        return 3, 8
    elif entry_type == "Sandwich - Regular":
        return 1, 10
    elif entry_type == "Sandwich - Lateral":
        return 3, 10
    else:
        return 1, 8

# Session state init
if "user_submitted" not in st.session_state:
    st.session_state.user_submitted = False

# Step 1 - User Details
if not st.session_state.user_submitted:
    st.title("Welcome to CGPA Calculator")

    name = st.text_input("Name")
    college = st.text_input("College")
    department = st.text_input("Department")
    entry_type = st.selectbox("Entry Type", ["Regular", "Lateral", "Sandwich - Regular", "Sandwich - Lateral"])

    if st.button("Submit"):
        if all([name, college, department, entry_type]):
            start_sem, max_sem = get_semester_range(entry_type)
            st.session_state.user_data = {
                "Name": name,
                "College": college,
                "Department": department,
                "EntryType": entry_type,
                "StartSem": start_sem,
                "MaxSem": max_sem
            }
            st.session_state.user_submitted = True
        else:
            st.warning("Please fill all fields before proceeding.")

# Step 2 - Semester Input
if st.session_state.user_submitted:
    user = st.session_state.user_data
    st.title(f"Welcome, {user['Name']}!")

    max_select = user['MaxSem']
    total_semesters = st.slider("How many semesters do you want to enter?", min_value=1, max_value=max_select - user['StartSem'] + 1, value=1)
    records = []

    for i in range(total_semesters):
        sem = user['StartSem'] + i
        with st.expander(f"Semester {sem}"):
            num_courses = st.number_input(f"Number of Courses in Semester {sem}", 1, 10, 5, key=f"courses_{sem}")
            for c in range(1, num_courses + 1):
                col1, col2 = st.columns(2)
                with col1:
                    credit = st.selectbox(f"Course {c} Credit (0–4)", [0, 1, 2, 3, 4], key=f"credit_{sem}_{c}")
                with col2:
                    score = st.selectbox(f"Course {c} Score (5–10)", list(range(5, 11)), key=f"score_{sem}_{c}")
                grade = get_grade(score)
                records.append({"Semester": sem, "Credit": credit, "Score": score, "Grade": grade})

    if st.button("Generate Printable Report"):
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

        html_content = f"""
        <style>
        .page {{ page-break-after: always; border: 2px solid black; padding: 20px; margin: 20px 0; }}
        .title {{ font-size: 24px; font-weight: bold; margin-bottom: 10px; }}
        .section {{ margin-bottom: 10px; }}
        table, th, td {{ border: 1px solid black; border-collapse: collapse; padding: 5px; }}
        </style>
        """

        # First Page: User Data + Semester 1
        html_content += f"""
        <div class='page'>
            <div class='title'>CGPA Report</div>
            <div class='section'>Name: {user['Name']}<br>College: {user['College']}<br>Department: {user['Department']}<br>Entry Type: {user['EntryType']}</div>
        """
        first_sem = user["StartSem"]
        sem_df = df[df["Semester"] == first_sem]
        html_content += "<div class='section'><b>Semester 1 Results</b><br><table><tr><th>Credit</th><th>Score</th><th>Grade</th></tr>"
        for _, row in sem_df.iterrows():
            html_content += f"<tr><td>{row['Credit']}</td><td>{row['Score']}</td><td>{row['Grade']}</td></tr>"
        gpa = sem_stats[sem_stats["Semester"] == first_sem]["GPA"].values[0]
        html_content += f"</table><br><b>GPA:</b> {gpa:.2f}</div><div class='section'><b>Overall CGPA:</b> {overall_cgpa:.2f}</div>"
        html_content += "<div class='section'><i>Disclaimer: CGPA was calculated based on the data fed by student.</i></div></div>"

        # Remaining Semesters
        for sem in range(user["StartSem"] + 1, user["StartSem"] + total_semesters):
            sem_df = df[df["Semester"] == sem]
            html_content += f"<div class='page'><div class='title'>Semester {sem} Results</div>"
            html_content += "<table><tr><th>Credit</th><th>Score</th><th>Grade</th></tr>"
            for _, row in sem_df.iterrows():
                html_content += f"<tr><td>{row['Credit']}</td><td>{row['Score']}</td><td>{row['Grade']}</td></tr>"
            gpa = sem_stats[sem_stats["Semester"] == sem]["GPA"].values[0]
            html_content += f"</table><br><b>GPA:</b> {gpa:.2f}<br><br><i>Disclaimer: CGPA was calculated based on the data fed by student.</i></div>"

        st.components.v1.html(f"""
            {html_content}
            <script>
                function printReport() {{
                    window.print();
                }}
            </script>
            <button onclick="printReport()">Print Report</button>
        """, height=1000)
