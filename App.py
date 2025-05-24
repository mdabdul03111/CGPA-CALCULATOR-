import streamlit as st
import pandas as pd

# Streamlit config
st.set_page_config(page_title="CGPA Calculator", layout="centered")

# Grade mapping
def map_grade(score):
    return {10: "O", 9: "A+", 8: "A", 7: "B+", 6: "B", 5: "C"}.get(score, "NA")

# Welcome / user info page
if "user_submitted" not in st.session_state:
    st.session_state.user_submitted = False

if not st.session_state.user_submitted:
    st.title("Welcome to CGPA Calculator")
    st.markdown("### Please fill in your details:")

    name = st.text_input("Name")
    college = st.text_input("College")
    department = st.text_input("Department")
    entry_type = st.selectbox(
        "Select Entry Type",
        ["Regular", "Lateral", "Sandwich – Regular", "Sandwich – Lateral"]
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

# CGPA calculator logic
if st.session_state.user_submitted:
    st.title("CGPA Calculator")
    st.markdown("#### Welcome to the CGPA calculator page. Fill in your semester details below.")

    user = st.session_state.user_data
    st.info(
        f"Calculating CGPA for:\n\n"
        f"**{user['Name']}**\n{user['College']} – {user['Department']}\n"
        f"Entry Type: {user['EntryType']}"
    )

    # Set semester range
    entry_type = user["EntryType"]
    if "Lateral" in entry_type:
        min_sem = 3
    else:
        min_sem = 1

    max_sem = 8 if "Regular" in entry_type and "Sandwich" not in entry_type else 10
    total_semesters = st.slider("Select number of semesters", min_sem, max_sem, max_sem)

    records = []
    for sem in range(min_sem, total_semesters + 1):
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
                grade = map_grade(score)
                records.append({
                    "Semester": sem,
                    "Credit": credit,
                    "Score": score,
                    "Grade": grade
                })

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

        # Generate printable HTML
        html = f"""
        <html>
        <head>
            <style>
                @media print {{
                    .page {{ page-break-after: always; }}
                }}
                body {{
                    font-family: Arial, sans-serif;
                    margin: 40px;
                }}
                h1, h2 {{
                    text-align: center;
                }}
                .page {{
                    border: 2px solid #000;
                    padding: 30px;
                    margin-bottom: 50px;
                    position: relative;
                }}
                table {{
                    width: 100%;
                    border-collapse: collapse;
                    margin-top: 20px;
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
                    font-size: 10px;
                    color: #888;
                }}
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
                <h2>Semester-wise GPA</h2>
                {sem_stats.to_html(index=False)}
                <div class="watermark">Disclaimer: This CGPA was calculated based on data fed by student</div>
            </div>
        """

        for sem in sorted(df['Semester'].unique()):
            html += f"<div class='page'><h2>Semester {sem} Breakdown</h2>"
            sem_data = df[df['Semester'] == sem][["Credit", "Score", "Grade", "Weighted"]]
            html += sem_data.to_html(index=False)
            html += "<div class='watermark'>Disclaimer: This CGPA was calculated based on data fed by student</div></div>"

        html += """
        <script>
            function printPage() {
                var w = window.open('', '_blank');
                w.document.write(document.documentElement.innerHTML);
                w.document.close();
                w.print();
            }
        </script>
        <div style='text-align:center; margin-top:20px;'>
            <button onclick="printPage()">Print Report</button>
        </div>
        </body></html>
        """

        st.components.v1.html(html, height=900, scrolling=True)
