import streamlit as st
import pandas as pd
import streamlit.components.v1 as components

st.set_page_config(page_title="CGPA Calculator", layout="centered")

# Initialize session state
if "step" not in st.session_state:
    st.session_state.step = 1
if "user_data" not in st.session_state:
    st.session_state.user_data = {}
if "existing_cgpa_path" not in st.session_state:
    st.session_state.existing_cgpa_path = False

def get_grade(score):
    return {
        10: "O",
        9: "A+",
        8: "A",
        7: "B+",
        6: "B",
        5: "C"
    }.get(score, "-")

def get_semester_limits(entry_type):
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

# Step 1: User Info Page
if st.session_state.step == 1:
    st.title("Welcome to CGPA Calculator")
    st.markdown("### Please fill in your details:")

    name = st.text_input("Name")
    college = st.text_input("College")
    department = st.text_input("Department")
    entry_type = st.selectbox("Entry Type", ["Regular", "Lateral", "Sandwich - Regular", "Sandwich - Lateral"])
    existing_cgpa_option = st.radio("Do you already have a CGPA?", ["No", "Yes"])

    if st.button("Next"):
        if not (name and college and department):
            st.warning("Please fill all fields.")
        else:
            st.session_state.user_data = {
                "Name": name,
                "College": college,
                "Department": department,
                "Entry": entry_type,
                "ExistingCGPA": existing_cgpa_option == "Yes"
            }
            st.session_state.existing_cgpa_path = existing_cgpa_option == "Yes"
            st.session_state.step = 2
            st.experimental_rerun()

# Step 2: Existing CGPA path
if st.session_state.step == 2 and st.session_state.existing_cgpa_path:
    user = st.session_state.user_data
    st.title("Continue CGPA Calculation")

    start_sem, max_sem = get_semester_limits(user["Entry"])

    sem_completed = st.number_input(f"Upto which semester you have CGPA? (between {start_sem} and {max_sem})", 
                                    min_value=start_sem, max_value=max_sem, step=1)
    existing_cgpa = st.number_input("Enter your existing CGPA (1.0 to 10.0)", min_value=1.0, max_value=10.0, step=0.01, format="%.2f")
    prev_credits = st.number_input("Total credits earned upto previous semester", min_value=1, step=1)

    if sem_completed and existing_cgpa and prev_credits:
        remaining_sem_start = sem_completed + 1
        remaining_sem_max = max_sem

        max_remaining = remaining_sem_max - sem_completed
        if max_remaining <= 0:
            st.error("No remaining semesters to enter.")
        else:
            sem_limit = st.slider("Select number of semesters you want to enter", min_value=1, max_value=max_remaining, value=max_remaining)

            records = []
            for sem in range(remaining_sem_start, remaining_sem_start + sem_limit):
                with st.expander(f"Semester {sem}"):
                    num_courses = st.number_input(f"Number of courses in Semester {sem}", min_value=1, step=1, value=5, key=f"courses_{sem}")
                    for course in range(1, num_courses + 1):
                        col1, col2 = st.columns(2)
                        with col1:
                            credit = st.selectbox(f"Course {course} Credit", options=[0,1,2,3,4], key=f"credit_{sem}_{course}")
                        with col2:
                            score = st.selectbox(f"Course {course} Score", options=list(range(5,11)), key=f"score_{sem}_{course}")
                        records.append({"Semester": sem, "Credit": credit, "Score": score})

            if st.button("Calculate CGPA"):
                df = pd.DataFrame(records)
                df["Weighted"] = df["Credit"] * df["Score"]
                df["Grade"] = df["Score"].apply(get_grade)

                total_credits = df["Credit"].sum()
                total_weighted = df["Weighted"].sum()

                overall_cgpa = (existing_cgpa * prev_credits + total_weighted) / (prev_credits + total_credits)

                sem_stats = df.groupby("Semester").agg(Credits=("Credit", "sum"),
                                                       WeightedScore=("Weighted", "sum")).reset_index()
                sem_stats["GPA"] = sem_stats["WeightedScore"] / sem_stats["Credits"]

                st.success(f"**Updated CGPA: {overall_cgpa:.2f}**")

                # Generate printable report HTML
                html = f"""
                <html>
                <head>
                    <style>
                        body {{ font-family: Arial; margin: 40px; }}
                        .page {{ page-break-after: always; border: 2px solid black; padding: 20px; }}
                        table {{ border-collapse: collapse; width: 100%; }}
                        th, td {{ border: 1px solid black; padding: 8px; text-align: center; }}
                        th {{ background-color: #f2f2f2; }}
                        .watermark {{ text-align: center; margin-top: 20px; font-size: 12px; color: gray; }}
                    </style>
                </head>
                <body>
                    <div class="page">
                        <h1>CGPA Report</h1>
                        <p><strong>Name:</strong> {user['Name']}<br>
                           <strong>College:</strong> {user['College']}<br>
                           <strong>Department:</strong> {user['Department']}<br>
                           <strong>Entry Type:</strong> {user['Entry']}<br>
                           <strong>Updated CGPA:</strong> {overall_cgpa:.2f}</p>
                    </div>
                """

                for sem in sorted(df['Semester'].unique()):
                    html += f"<div class='page'><h2>Semester {sem} Breakdown</h2>"
                    sem_data = df[df['Semester'] == sem][["Credit", "Score", "Grade", "Weighted"]]
                    html += sem_data.to_html(index=False)
                    html += "</div>"

                html += """
                    <div class="watermark">Disclaimer! This CGPA was calculated based on data fed by student</div>
                </body></html>
                """

                components.html(html, height=800, scrolling=True)

# Step 3: New CGPA calculation (no existing CGPA)
if st.session_state.step == 2 and not st.session_state.existing_cgpa_path:
    user = st.session_state.user_data
    st.title("New CGPA Calculation")

    start_sem, max_sem = get_semester_limits(user["Entry"])

    sem_limit = st.slider(f"Select number of semesters to enter (from {start_sem} to {max_sem})", min_value=1, max_value=max_sem - start_sem + 1, value=max_sem - start_sem + 1)

    records = []
    for sem in range(start_sem, start_sem + sem_limit):
        with st.expander(f"Semester {sem}"):
            num_courses = st.number_input(f"Number of courses in Semester {sem}", min_value=1, step=1, value=5, key=f"courses_new_{sem}")
            for course in range(1, num_courses + 1):
                col1, col2 = st.columns(2)
                with col1:
                    credit = st.selectbox(f"Course {course} Credit", options=[0,1,2,3,4], key=f"credit_new_{sem}_{course}")
                with col2:
                    score = st.selectbox(f"Course {course} Score", options=list(range(5,11)), key=f"score_new_{sem}_{course}")
                records.append({"Semester": sem, "Credit": credit, "Score": score})

    if st.button("Calculate CGPA New"):
        df = pd.DataFrame(records)
        df["Weighted"] = df["Credit"] * df["Score"]
        df["Grade"] = df["Score"].apply(get_grade)

        total_credits = df["Credit"].sum()
        total_weighted = df["Weighted"].sum()

        overall_cgpa = total_weighted / total_credits if total_credits != 0 else 0

        sem_stats = df.groupby("Semester").agg(Credits=("Credit", "sum"),
                                               WeightedScore=("Weighted", "sum")).reset_index()
        sem_stats["GPA"] = sem_stats["WeightedScore"] / sem_stats["Credits"]

        st.success(f"**CGPA: {overall_cgpa:.2f}**")

        # Printable report HTML
        html = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial; margin: 40px; }}
                .page {{ page-break-after: always; border: 2px solid black; padding: 20px; }}
                table {{ border-collapse: collapse; width: 100%; }}
                th, td {{ border: 1px solid black; padding: 8px; text-align: center; }}
                th {{ background-color: #f2f2f2; }}
                .watermark {{ text-align: center; margin-top: 20px; font-size: 12px; color: gray; }}
            </style>
        </head>
        <body>
            <div class="page">
                <h1>CGPA Report</h1>
                <p><strong>Name:</strong> {user['Name']}<br>
                   <strong>College:</strong> {user['College']}<br>
                   <strong>Department:</strong> {user['Department']}<br>
                   <strong>Entry Type:</strong> {user['Entry']}<br>
                   <strong>CGPA:</strong> {overall_cgpa:.2f}</p>
            </div>
        """

        for sem in sorted(df['Semester'].unique()):
            html += f"<div class='page'><h2>Semester {sem} Breakdown</h2>"
            sem_data = df[df['Semester'] == sem][["Credit", "Score", "Grade", "Weighted"]]
            html += sem_data.to_html(index=False)
            html += "</div>"

        html += """
            <div class="watermark">Disclaimer! This CGPA was calculated based on data fed by student</div>
        </body></html>
        """

        components.html(html, height=800, scrolling=True)
