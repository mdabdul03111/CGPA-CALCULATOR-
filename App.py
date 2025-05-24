import streamlit as st 
import pandas as pd 
import io

st.set_page_config(page_title="CGPA Calculator", layout="centered")

if "user_submitted" not in st.session_state: st.session_state.user_submitted = False

Grade calculation function

def get_grade(score): return { 10: "O", 9: "A+", 8: "A", 7: "B+", 6: "B", 5: "C" }.get(score, "RA")

Entry options and semester rules

def get_semester_range(entry_type): if entry_type == "Regular": return 1, 8 elif entry_type == "Lateral": return 3, 8 elif entry_type == "Sandwich - Regular": return 1, 10 elif entry_type == "Sandwich - Lateral": return 3, 10 else: return 1, 8

Step 1: User Details Page

if not st.session_state.user_submitted: st.title("Welcome to CGPA Calculator")

st.markdown("### Please fill in your details:")

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

Step 2: CGPA Calculator

if st.session_state.user_submitted: user = st.session_state.user_data st.title(f"Welcome, {user['Name']}!") st.subheader("Enter your semester-wise course data")

records = []
for sem in range(user['StartSem'], user['MaxSem'] + 1):
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
            grade = get_grade(score)
            records.append({"Semester": sem, "Credit": credit, "Score": score, "Grade": grade})

if st.button("Calculate CGPA and Print"):
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

    st.success(f"**Overall CGPA: {overall_cgpa:.2f}**")

    st.subheader("Semester-wise GPA")
    st.dataframe(sem_stats[["Semester", "Credits", "GPA"]])

    st.subheader("Detailed Course Breakdown")
    st.dataframe(df)

    # Simulated Print - Plain Text Export (no external module)
    output = io.StringIO()
    output.write("CGPA Report\n")
    output.write("="*50 + "\n")
    output.write(f"Name: {user['Name']}\nCollege: {user['College']}\nDepartment: {user['Department']}\nEntry Type: {user['EntryType']}\n")
    output.write("\n")
    output.write(f"Overall CGPA: {overall_cgpa:.2f}\n\n")

    for sem in range(user['StartSem'], user['MaxSem'] + 1):
        output.write(f"Semester {sem} Results\n")
        output.write("-"*40 + "\n")
        sem_df = df[df["Semester"] == sem]
        output.write(sem_df.to_string(index=False))
        output.write("\n\n")

    output.write("Disclaimer: CGPA was calculated based on the data fed by student.\n")

    st.download_button(
        label="Download Text Report",
        data=output.getvalue(),
        file_name="cgpa_report.txt",
        mime="text/plain"
    )

