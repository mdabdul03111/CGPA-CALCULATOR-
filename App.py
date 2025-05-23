import streamlit as st
import pandas as pd

st.set_page_config(page_title="CGPA Calculator", layout="centered")

if "user_submitted" not in st.session_state:
    st.session_state.user_submitted = False

if not st.session_state.user_submitted:
    st.title("Welcome to CGPA Calculator")
    st.markdown("### Please fill in your details:")

    name = st.text_input("Name")
    college = st.text_input("College")
    department = st.text_input("Department")
    mobile = st.text_input("Mobile Number")
    email = st.text_input("Email ID")

    if st.button("Submit"):
        if all([name, college, department, mobile, email]):
            st.session_state.user_data = {
                "Name": name,
                "College": college,
                "Department": department,
                "Mobile": mobile,
                "Email": email
            }
            st.session_state.user_submitted = True
        else:
            st.warning("Please fill all fields before proceeding.")

if st.session_state.user_submitted:
    st.title("CGPA Calculator")

    user = st.session_state.user_data
    st.info(f"Calculating CGPA for:\n\n**{user['Name']}**\n{user['College']} – {user['Department']}\nMobile: {user['Mobile']}\nEmail: {user['Email']}")

    total_semesters = st.number_input("Number of Semesters", min_value=1, step=1, value=2)

    records = []
    for sem in range(1, total_semesters + 1):
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
                records.append({"Semester": sem, "Course": course, "Credit": credit, "Score": score})

    if st.button("Calculate CGPA"):
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

        html = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial; margin: 40px; }}
                h1, h2 {{ text-align: center; }}
                .page {{ page-break-after: always; }}
                table {{
                    width: 100%;
                    border-collapse: collapse;
                    margin-top: 20px;
                }}
                th, td {{
                    border: 1px solid #000;
                    padding: 8px;
                    text-align: center;
                    font-size: 14px;
                }}
                th {{
                    background-color: #f2f2f2;
                }}
                .info p {{
                    margin: 5px 0;
                    font-size: 16px;
                }}
                .btn-container {{
                    text-align: center;
                    margin-top: 30px;
                }}
                button {{
                    padding: 10px 20px;
                    font-size: 16px;
                    cursor: pointer;
                }}
            </style>
        </head>
        <body>
            <h1>CGPA Report</h1>
            <div class="info">
                <p><strong>Name:</strong> {user['Name']}</p>
                <p><strong>College:</strong> {user['College']}</p>
                <p><strong>Department:</strong> {user['Department']}</p>
                <p><strong>Mobile:</strong> {user['Mobile']}</p>
                <p><strong>Email:</strong> {user['Email']}</p>
                <p><strong>Overall CGPA:</strong> {overall_cgpa:.2f}</p>
            </div>
        """

        for sem in sorted(df["Semester"].unique()):
            sem_df = df[df["Semester"] == sem]
            gpa = sem_stats[sem_stats["Semester"] == sem]["GPA"].values[0]
            html += f"""
            <div class='page'>
                <h2>Semester {sem} Report</h2>
                <p><strong>Semester GPA:</strong> {gpa:.2f}</p>
                <table>
                    <tr>
                        <th>Course</th>
                        <th>Credit</th>
                        <th>Score</th>
                        <th>Weighted</th>
                    </tr>
            """
            for _, row in sem_df.iterrows():
                html += f"""
                    <tr>
                        <td>{int(row['Course'])}</td>
                        <td>{row['Credit']}</td>
                        <td>{row['Score']}</td>
                        <td>{row['Weighted']}</td>
                    </tr>
                """
            html += "</table></div>"

        html += """
            <div class="btn-container">
                <button onclick="window.print()">Print Report</button>
            </div>
        </body>
        </html>
        """

        st.components.v1.html(html, height=1000, scrolling=True)
