import streamlit as st
import pandas as pd

st.set_page_config(page_title="CGPA Calculator", layout="centered")

if "user_submitted" not in st.session_state:
    st.session_state.user_submitted = False

# Grade mapping function
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

# Step 1: Collect user details
if not st.session_state.user_submitted:
    st.title("Welcome to CGPA Calculator")
    st.markdown("### Please fill in your details:")

    name = st.text_input("Name")
    college = st.text_input("College")
    department = st.text_input("Department")
    entry_type = st.radio("Entry Type", [
        "Regular", "Lateral", 
        "Sandwich - Regular", "Sandwich - Lateral"
    ])

    if st.button("Submit"):
        if all([name, college, department]):
            st.session_state.user_data = {
                "Name": name,
                "College": college,
                "Department": department,
                "EntryType": entry_type
            }
            st.session_state.user_submitted = True
        else:
            st.warning("Please fill all fields before proceeding.")

# Step 2: CGPA Calculator
if st.session_state.user_submitted:
    user = st.session_state.user_data
    st.title("CGPA Calculator")
    st.info(f"Calculating CGPA for **{user['Name']}** – {user['College']} ({user['Department']})")

    entry = user["EntryType"]
    if entry == "Lateral":
        start_sem, max_sem = 3, 8
    elif entry == "Regular":
        start_sem, max_sem = 1, 8
    elif entry == "Sandwich - Regular":
        start_sem, max_sem = 1, 10
    elif entry == "Sandwich - Lateral":
        start_sem, max_sem = 3, 10
    else:
        start_sem, max_sem = 1, 8

    total_semesters = st.number_input(
        "Number of Semesters",
        min_value=1,
        max_value=max_sem - start_sem + 1,
        step=1,
        value=max_sem - start_sem + 1
    )

    records = []

    for sem in range(start_sem, start_sem + total_semesters):
        if sem > max_sem:
            break
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
                        f"Course {course} Credit",
                        options=[0, 1, 2, 3, 4],
                        key=f"credit_{sem}_{course}"
                    )
                with col2:
                    score = st.selectbox(
                        f"Course {course} Score",
                        options=list(range(5, 11)),
                        key=f"score_{sem}_{course}"
                    )
                records.append({
                    "Semester": sem,
                    "Course": course,
                    "Credit": credit,
                    "Score": score,
                    "Grade": get_grade(score),
                    "Weighted": credit * score
                })

    if st.button("Calculate CGPA"):
        df = pd.DataFrame(records)
        total_credits = df["Credit"].sum()
        total_weighted = df["Weighted"].sum()
        overall_cgpa = total_weighted / total_credits if total_credits > 0 else 0.0

        sem_stats = df.groupby("Semester").agg(
            Credits=("Credit", "sum"),
            WeightedScore=("Weighted", "sum")
        ).reset_index()
        sem_stats["GPA"] = sem_stats["WeightedScore"] / sem_stats["Credits"]

        st.success(f"**Overall CGPA: {overall_cgpa:.2f}**")
        st.subheader("Semester-wise GPA")
        st.dataframe(sem_stats[["Semester", "Credits", "GPA"]])

        st.subheader("Detailed Course Breakdown")
        st.dataframe(df)

        # Printable HTML with border and watermark
        html = f"""
        <html>
        <head>
            <style>
                body {{
                    font-family: Arial;
                    border: 3px solid black;
                    padding: 30px;
                }}
                h1, h2 {{
                    text-align: center;
                }}
                .info {{
                    font-size: 16px;
                    margin-bottom: 10px;
                }}
                table {{
                    width: 100%;
                    border-collapse: collapse;
                    margin-top: 10px;
                    margin-bottom: 30px;
                }}
                th, td {{
                    border: 1px solid #000;
                    padding: 6px;
                    text-align: center;
                }}
                th {{
                    background-color: #f2f2f2;
                }}
                .watermark {{
                    position: fixed;
                    bottom: 80px;
                    width: 100%;
                    text-align: center;
                    opacity: 0.1;
                    font-size: 30px;
                    transform: rotate(-30deg);
                }}
                .disclaimer {{
                    text-align: center;
                    font-size: 12px;
                    color: #888;
                }}
                .print-btn {{
                    text-align: center;
                    margin-top: 20px;
                }}
            </style>
        </head>
        <body>
            <div class="watermark">Disclaimer: CGPA was calculated based on the data fed by student</div>
            <h1>CGPA Report</h1>
            <div class="info">
                <p><strong>Name:</strong> {user['Name']}</p>
                <p><strong>College:</strong> {user['College']}</p>
                <p><strong>Department:</strong> {user['Department']}</p>
                <p><strong>Entry Type:</strong> {user['EntryType']}</p>
                <p><strong>Overall CGPA:</strong> {overall_cgpa:.2f}</p>
            </div>
        """

        for sem in sorted(df["Semester"].unique()):
            sem_df = df[df["Semester"] == sem]
            gpa = sem_stats[sem_stats["Semester"] == sem]["GPA"].values[0]
            html += f"""
            <h2>Semester {sem}</h2>
            <p><strong>GPA:</strong> {gpa:.2f}</p>
            <table>
                <tr>
                    <th>Course</th>
                    <th>Credit</th>
                    <th>Score</th>
                    <th>Grade</th>
                    <th>Weighted</th>
                </tr>
            """
            for _, row in sem_df.iterrows():
                html += f"""
                <tr>
                    <td>{int(row['Course'])}</td>
                    <td>{row['Credit']}</td>
                    <td>{row['Score']}</td>
                    <td>{row['Grade']}</td>
                    <td>{row['Weighted']}</td>
                </tr>
                """
            html += "</table>"

        html += """
            <div class="disclaimer">Disclaimer: CGPA was calculated based on the data fed by student</div>
            <div class="print-btn">
                <button onclick="window.print()">Print Report</button>
            </div>
        </body>
        </html>
        """

        st.components.v1.html(html, height=1300, scrolling=True)
