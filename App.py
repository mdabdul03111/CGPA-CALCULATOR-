import streamlit as st import pandas as pd

Streamlit config

st.set_page_config(page_title="CGPA Calculator", layout="centered")

if "user_submitted" not in st.session_state: st.session_state.user_submitted = False

Step 1: User Info

if not st.session_state.user_submitted: st.title("Welcome to CGPA Calculator") st.markdown("### Please fill in your details:")

name = st.text_input("Name")
college = st.text_input("College")
department = st.text_input("Department")
entry_type = st.selectbox("Entry Type", ["Regular", "Lateral", "Sandwich - Regular", "Sandwich - Lateral"])

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

Step 2: CGPA Calculator

if st.session_state.user_submitted: user = st.session_state.user_data st.title("CGPA Calculator") st.info(f"Calculating CGPA for:\n\n**{user['Name']}**\n{user['College']} – {user['Department']}\nEntry Type: {user['EntryType']}")

# Determine semester range based on entry type
entry_type = user["EntryType"]
if entry_type == "Regular":
    sem_start, sem_end = 1, 8
elif entry_type == "Lateral":
    sem_start, sem_end = 3, 8
elif entry_type == "Sandwich - Regular":
    sem_start, sem_end = 1, 10
else:  # Sandwich - Lateral
    sem_start, sem_end = 3, 10

total_semesters = st.number_input("Number of Semesters", min_value=sem_start, max_value=sem_end, step=1, value=sem_end)

records = []
for sem in range(sem_start, total_semesters + 1):
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

if st.button("Generate Report and Print"):
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

    # Build HTML with borders and pages
    html = f"""
    <html>
    <head>
        <style>
            body {{ font-family: Arial; margin: 0; padding: 0; }}
            .page {{
                page-break-after: always;
                border: 2px solid black;
                padding: 20px;
                margin: 20px;
            }}
            table, th, td {{ border: 1px solid black; border-collapse: collapse; padding: 8px; }}
            th {{ background-color: #f2f2f2; }}
            h1, h2 {{ text-align: center; margin-bottom: 20px; }}
            p {{ font-size: 16px; }}
            .btn-print {{
                position: fixed;
                bottom: 20px;
                right: 20px;
                padding: 10px 20px;
                font-size: 16px;
                cursor: pointer;
            }}
        </style>
    </head>
    <body>
        <!-- Welcome Page -->
        <div class="page">
            <h1>Welcome, {user['Name']}!</h1>
        </div>
        <!-- User Info + Semester 1 -->
        <div class="page">
            <h2>Student Information</h2>
            <p><strong>Name:</strong> {user['Name']}<br>
               <strong>College:</strong> {user['College']}<br>
               <strong>Department:</strong> {user['Department']}<br>
               <strong>Entry Type:</strong> {user['EntryType']}<br>
               <strong>Overall CGPA:</strong> {overall_cgpa:.2f}</p>
            <h2>Semester 1 GPA</h2>
            {sem_stats[sem_stats['Semester'] == sem_start][['Credits', 'GPA']].to_html(index=False)}
        </div>
    """

    # Additional semesters
    for sem in sorted(df['Semester'].unique()):
        if sem == sem_start:
            continue
        html += f"""
        <div class='page'>
            <h2>Semester {sem} Breakdown</h2>
            {df[df['Semester'] == sem][['Credit', 'Score', 'Weighted']].to_html(index=False)}
        </div>
        """

    html += """
        <button class="btn-print" onclick="window.print();">Print Report</button>
    </body>
    </html>
    """

    st.components.v1.html(html, height=800, scrolling=True)

