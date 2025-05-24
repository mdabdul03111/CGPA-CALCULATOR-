import streamlit as st
import pandas as pd

st.set_page_config(page_title="CGPA Calculator", layout="wide")

# Grade mapping
grade_map = {
    10: "O",
    9: "A+",
    8: "A",
    7: "B+",
    6: "B",
    5: "C",
}

# Entry types and corresponding semester settings
entry_config = {
    "Regular": (1, 8),
    "Lateral": (3, 8),
    "Sandwich - Regular": (1, 10),
    "Sandwich - Lateral": (3, 10),
}

if "submitted" not in st.session_state:
    st.session_state.submitted = False

if not st.session_state.submitted:
    st.title("Welcome to CGPA Calculator")

    name = st.text_input("Name")
    college = st.text_input("College")
    department = st.text_input("Department")
    entry_type = st.selectbox("Entry Type", list(entry_config.keys()))

    if st.button("Start"):
        if all([name, college, department, entry_type]):
            st.session_state.name = name
            st.session_state.college = college
            st.session_state.department = department
            st.session_state.entry_type = entry_type
            st.session_state.start_sem, st.session_state.max_sem = entry_config[entry_type]
            st.session_state.submitted = True
        else:
            st.warning("Please fill all fields before proceeding.")

if st.session_state.submitted:
    st.title("CGPA Calculator")

    name = st.session_state.name
    college = st.session_state.college
    dept = st.session_state.department
    entry = st.session_state.entry_type
    start_sem, max_sem = st.session_state.start_sem, st.session_state.max_sem

    st.markdown(f"#### Welcome, **{name}**")
    st.info(f"Calculating CGPA for: **{name}**, {college}, {dept} ({entry})")

    total_sem = st.number_input("Number of Semesters", min_value=start_sem, max_value=max_sem, step=1, value=start_sem)

    data = []
    for sem in range(start_sem, total_sem + 1):
        with st.expander(f"Semester {sem}"):
            courses = st.number_input(f"Number of courses in Semester {sem}", min_value=1, step=1, value=5, key=f"c_{sem}")
            for i in range(1, courses + 1):
                col1, col2 = st.columns(2)
                with col1:
                    credit = st.selectbox(f"Course {i} Credit", [1, 2, 3, 4], key=f"credit_{sem}_{i}")
                with col2:
                    score = st.selectbox(f"Course {i} Score", list(range(5, 11)), key=f"score_{sem}_{i}")
                grade = grade_map.get(score, "F")
                data.append({"Semester": sem, "Course": i, "Credit": credit, "Score": score, "Grade": grade})

    if st.button("Calculate CGPA and Generate Report"):
        df = pd.DataFrame(data)
        df["Weighted"] = df["Credit"] * df["Score"]

        sem_stats = df.groupby("Semester").agg(
            Total_Credits=("Credit", "sum"),
            Weighted_Score=("Weighted", "sum")
        ).reset_index()
        sem_stats["GPA"] = sem_stats["Weighted_Score"] / sem_stats["Total_Credits"]

        overall_cgpa = df["Weighted"].sum() / df["Credit"].sum()

        # Show result
        st.success(f"**Overall CGPA: {overall_cgpa:.2f}**")
        st.subheader("Semester-wise GPA")
        st.dataframe(sem_stats)

        st.subheader("Course Breakdown")
        st.dataframe(df)

        # Generate printable HTML report
        html = f"""
        <style>
            .page {{
                page-break-after: always;
                border: 2px solid black;
                padding: 20px;
                margin: 20px auto;
                max-width: 800px;
            }}
            .watermark {{
                color: #aaa;
                font-size: 10px;
                text-align: center;
                margin-top: 30px;
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
                margin-top: 10px;
            }}
            th, td {{
                border: 1px solid #333;
                padding: 8px;
                text-align: center;
            }}
        </style>
        """

        first_page = df[df["Semester"] == start_sem]
        html += f"""
        <div class="page">
            <h2>CGPA Report</h2>
            <p><strong>Name:</strong> {name}<br>
               <strong>College:</strong> {college}<br>
               <strong>Department:</strong> {dept}<br>
               <strong>Entry Type:</strong> {entry}</p>
            <h4>Semester {start_sem}</h4>
            <table>
                <tr><th>Course</th><th>Credit</th><th>Score</th><th>Grade</th></tr>
        """
        for _, row in first_page.iterrows():
            html += f"<tr><td>{row['Course']}</td><td>{row['Credit']}</td><td>{row['Score']}</td><td>{row['Grade']}</td></tr>"
        html += f"""
            </table>
            <p><strong>GPA:</strong> {sem_stats.loc[sem_stats['Semester'] == start_sem, 'GPA'].values[0]:.2f}</p>
            <div class="watermark">Disclaimer: CGPA was calculated based on the data fed by student</div>
        </div>
        """

        for sem in range(start_sem + 1, total_sem + 1):
            sem_data = df[df["Semester"] == sem]
            html += f"""
            <div class="page">
                <h4>Semester {sem}</h4>
                <table>
                    <tr><th>Course</th><th>Credit</th><th>Score</th><th>Grade</th></tr>
            """
            for _, row in sem_data.iterrows():
                html += f"<tr><td>{row['Course']}</td><td>{row['Credit']}</td><td>{row['Score']}</td><td>{row['Grade']}</td></tr>"
            html += f"""
                </table>
                <p><strong>GPA:</strong> {sem_stats.loc[sem_stats['Semester'] == sem, 'GPA'].values[0]:.2f}</p>
                <div class="watermark">Disclaimer: CGPA was calculated based on the data fed by student</div>
            </div>
            """

        html += f"""
        <div class="page">
            <h3>Overall CGPA: {overall_cgpa:.2f}</h3>
            <div class="watermark">Disclaimer: CGPA was calculated based on the data fed by student</div>
        </div>
        """

        st.markdown(html, unsafe_allow_html=True)
        st.markdown("**Use Ctrl+P or Command+P to print or save as PDF.**")
