import streamlit as st
import pandas as pd

# Streamlit config
st.set_page_config(page_title="CGPA Calculator", layout="centered")

# Initialize session states
if "user_submitted" not in st.session_state:
    st.session_state.user_submitted = False
if "existing_cgpa_flow" not in st.session_state:
    st.session_state.existing_cgpa_flow = False

# Step 1: User Info
if not st.session_state.user_submitted:
    st.title("Welcome to CGPA Calculator")
    st.markdown("### Please fill in your details:")

    name = st.text_input("Name")
    college = st.text_input("College")
    department = st.text_input("Department")
    
    entry_type = st.selectbox("Mode of Entry", [
        "Regular",
        "Lateral",
        "Sandwich - Regular",
        "Sandwich - Lateral"
    ])

    existing_cgpa_q = st.radio("Do you already have an existing CGPA?", ["No", "Yes"])

    if st.button("Submit"):
        if all([name, college, department, entry_type]):
            st.session_state.user_data = {
                "Name": name,
                "College": college,
                "Department": department,
                "Entry": entry_type
            }
            st.session_state.user_submitted = True
            st.session_state.existing_cgpa_flow = (existing_cgpa_q == "Yes")
        else:
            st.warning("Please fill all fields before proceeding.")

# Step 2: Existing CGPA Info
if st.session_state.user_submitted and st.session_state.existing_cgpa_flow and "existing_cgpa" not in st.session_state:
    st.title("Existing CGPA Information")
    
    completed_sem = st.number_input("Upto which semester do you have CGPA?", min_value=1, max_value=10, step=1)
    prev_cgpa = st.number_input("Enter your existing CGPA", min_value=1.0, max_value=10.0, format="%.2f")
    prev_credits = st.number_input("Enter total credits earned up to previous semester", min_value=1)

    if st.button("Continue to Remaining Semesters"):
        st.session_state.existing_cgpa = {
            "completed_sem": completed_sem,
            "cgpa": prev_cgpa,
            "credits": prev_credits
        }

# Step 3: CGPA Calculator
if st.session_state.user_submitted and (
    not st.session_state.existing_cgpa_flow or "existing_cgpa" in st.session_state
):
    st.title("CGPA Calculator")
    
    user = st.session_state.user_data
    st.info(f"Calculating CGPA for:\n\n**{user['Name']}**\n{user['College']} – {user['Department']}\nEntry Mode: {user['Entry']}")

    # Set semester limits based on entry type
    entry = user["Entry"]
    if entry == "Regular":
        sem_start, sem_end = 1, 8
    elif entry == "Lateral":
        sem_start, sem_end = 3, 8
    elif entry == "Sandwich - Regular":
        sem_start, sem_end = 1, 10
    else:
        sem_start, sem_end = 3, 10

    if st.session_state.existing_cgpa_flow:
        sem_start = st.session_state.existing_cgpa["completed_sem"] + 1

    sem_count = sem_end - sem_start + 1

    # Slider to reduce number of semesters entered
    sem_limit = st.slider("Select number of semesters you want to enter", min_value=1, max_value=sem_count, value=sem_count)

    records = []
    for i, sem in enumerate(range(sem_start, sem_start + sem_limit)):
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

        # Grade conversion
        def score_to_grade(score):
            return {
                10: "O", 9: "A+", 8: "A", 7: "B+", 6: "B", 5: "C"
            }.get(score, "F")

        df["Grade"] = df["Score"].apply(score_to_grade)

        # New CGPA calculation
        if st.session_state.existing_cgpa_flow:
            prev = st.session_state.existing_cgpa
            total_weighted += prev["cgpa"] * prev["credits"]
            total_credits += prev["credits"]

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

        # HTML printable report
        html = f"""
        <html>
        <head>
            <style>
                body {{
                    font-family: Arial;
                    margin: 40px;
                    border: 10px solid #ddd;
                    padding: 20px;
                    position: relative;
                }}
                h1, h2 {{
                    text-align: center;
                }}
                .page {{
                    page-break-after: always;
                    border: 5px solid #444;
                    padding: 20px;
                    margin-bottom: 30px;
                    position: relative;
                }}
                table {{
                    width: 100%;
                    border-collapse: collapse;
                }}
                th, td {{
                    border: 1px solid black;
                    padding: 8px;
                    text-align: center;
                }}
                th {{
                    background-color: #f2f2f2;
                }}
                .watermark {{
                    position: absolute;
                    bottom: 10px;
                    left: 20px;
                    font-size: 12px;
                    color: #aaa;
                }}
            </style>
        </head>
        <body>
            <div class="page">
                <h1>CGPA Report</h1>
                <p><strong>Name:</strong> {user['Name']}<br>
                   <strong>College:</strong> {user['College']}<br>
                   <strong>Department:</strong> {user['Department']}<br>
                   <strong>Entry Mode:</strong> {user['Entry']}<br>
                   <strong>Overall CGPA:</strong> {overall_cgpa:.2f}</p>
                <div class="watermark">Disclaimer: This CGPA was calculated based on data fed by student.</div>
            </div>
            <div class="page">
                <h2>Semester-wise GPA</h2>
                {sem_stats.to_html(index=False)}
                <div class="watermark">Disclaimer: This CGPA was calculated based on data fed by student.</div>
            </div>
        """

        for sem in sorted(df["Semester"].unique()):
            sem_data = df[df["Semester"] == sem][["Credit", "Score", "Grade", "Weighted"]]
            html += f"""
            <div class='page'>
                <h2>Semester {sem} Breakdown</h2>
                {sem_data.to_html(index=False)}
                <div class="watermark">Disclaimer: This CGPA was calculated based on data fed by student.</div>
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
        <button onclick="printPage()">Print Report</button>
        </body>
        </html>
        """

        st.components.v1.html(html, height=800, scrolling=True)
