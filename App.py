import streamlit as st
import pandas as pd

# Streamlit config
st.set_page_config(page_title="CGPA Calculator", layout="centered")

if "user_submitted" not in st.session_state:
    st.session_state.user_submitted = False

# Step 1: User Info
if not st.session_state.user_submitted:
    st.title("Welcome to CGPA Calculator")
    st.markdown("### Please fill in your details:")

    name = st.text_input("Name")
    college = st.text_input("College")
    department = st.text_input("Department")

    entry_type = st.selectbox(
        "Entry Type",
        ["Regular", "Lateral", "Sandwich - Regular", "Sandwich - Lateral"]
    )

    if st.button("Submit"):
        if all([name, college, department, entry_type]):
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
    st.markdown("Welcome! Please enter your semester-wise course details below:")

    if user["EntryType"] == "Regular":
        min_sem, max_sem = 1, 8
    elif user["EntryType"] == "Lateral":
        min_sem, max_sem = 3, 8
    elif user["EntryType"] == "Sandwich - Regular":
        min_sem, max_sem = 1, 10
    elif user["EntryType"] == "Sandwich - Lateral":
        min_sem, max_sem = 3, 10

    selected_max_sem = st.slider(
        "Select number of semesters you want to enter:",
        min_value=min_sem,
        max_value=max_sem,
        value=min_sem,
        step=1
    )

    records = []
    for sem in range(min_sem, selected_max_sem + 1):
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

        # Printable HTML with watermark and improved design
        html = f"""
        <html>
        <head>
            <style>
                body {{
                    font-family: 'Segoe UI', sans-serif;
                    margin: 40px;
                    color: #222;
                }}
                .page {{
                    border: 3px solid #000;
                    padding: 30px;
                    margin-bottom: 50px;
                    page-break-after: always;
                    position: relative;
                }}
                h1, h2 {{
                    text-align: center;
                    margin-bottom: 20px;
                }}
                table {{
                    width: 100%;
                    border-collapse: collapse;
                    margin-top: 20px;
                    font-size: 14px;
                }}
                th, td {{
                    border: 1px solid #000;
                    padding: 8px;
                    text-align: center;
                }}
                th {{
                    background-color: #f0f0f0;
                }}
                .watermark {{
                    position: absolute;
                    bottom: 10px;
                    left: 10px;
                    font-size: 12px;
                    color: #888;
                }}
            </style>
        </head>
        <body>
            <div class="page">
                <h1>Student Details</h1>
                <p><strong>Name:</strong> {user['Name']}<br>
                   <strong>College:</strong> {user['College']}<br>
                   <strong>Department:</strong> {user['Department']}<br>
                   <strong>Entry Type:</strong> {user['EntryType']}<br>
                   <strong>Overall CGPA:</strong> {overall_cgpa:.2f}</p>
                <div class="watermark">Disclaimer! This CGPA was calculated based on data fed by student</div>
            </div>

            <div class="page">
                <h2>Semester-wise GPA</h2>
                {sem_stats.to_html(index=False)}
                <div class="watermark">Disclaimer! This CGPA was calculated based on data fed by student</div>
            </div>
        """

        for sem in sorted(df['Semester'].unique()):
            sem_data = df[df['Semester'] == sem][["Credit", "Score", "Weighted"]]
            html += f"""
            <div class="page">
                <h2>Semester {sem} Breakdown</h2>
                {sem_data.to_html(index=False)}
                <div class="watermark">Disclaimer! This CGPA was calculated based on data fed by student</div>
            </div>
            """

        html += """
        <script>
            function printPage() {
                var w = window.open('', '_blank');
                w.document.write(document.documentElement.innerHTML);
                w.document.close();
                w.print();
            }
        </script>
        <center><button onclick="printPage()">Print Report</button></center>
        </body></html>
        """

        st.components.v1.html(html, height=800, scrolling=True)
