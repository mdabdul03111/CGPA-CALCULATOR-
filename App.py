import streamlit as st
import pandas as pd

# Set up Streamlit page with custom theme
st.set_page_config(page_title="CGPA Calculator", layout="centered")

# Inject custom CSS for fonts and colors
st.markdown(
    """
    <style>
    /* Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Roboto&display=swap');

    html, body, [class*="css"]  {
        font-family: 'Roboto', sans-serif;
        color: #1c1e21;
        background-color: #f5f7fa;
    }
    h1, h2, h3, h4 {
        color: #0b3d91;
        font-weight: 700;
    }
    .stButton > button {
        background-color: #0b3d91;
        color: white;
        font-weight: 600;
        border-radius: 8px;
        padding: 10px 24px;
        transition: background-color 0.3s ease;
    }
    .stButton > button:hover {
        background-color: #0846a5;
        cursor: pointer;
    }
    .stTextInput > div > input, .stNumberInput > div > input {
        border: 2px solid #0b3d91;
        border-radius: 5px;
        padding: 8px;
    }
    .stSelectbox > div > div > div {
        border: 2px solid #0b3d91;
        border-radius: 5px;
        padding: 5px;
    }
    .stSlider > div > div > input {
        accent-color: #0b3d91;
    }
    .css-1d391kg {
        background-color: #e9efff;
        border-radius: 8px;
        padding: 15px;
        margin-bottom: 20px;
    }
    .stExpander > div {
        background-color: white !important;
        border: 1px solid #0b3d91;
        border-radius: 6px;
        padding: 15px;
        margin-bottom: 15px;
    }
    /* Table styling */
    table {
        border-collapse: collapse;
        width: 100%;
        margin-top: 10px;
    }
    th, td {
        border: 1px solid #0b3d91;
        text-align: center;
        padding: 8px;
    }
    th {
        background-color: #c3d1f7;
        font-weight: 700;
    }
    /* Print button style */
    .print-button {
        background-color: #0b3d91;
        color: white;
        border: none;
        padding: 10px 24px;
        font-size: 16px;
        border-radius: 8px;
        cursor: pointer;
        margin-top: 20px;
    }
    .print-button:hover {
        background-color: #0846a5;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Initialize session state
if "user_submitted" not in st.session_state:
    st.session_state.user_submitted = False
if "user_data" not in st.session_state:
    st.session_state.user_data = {}
if "step" not in st.session_state:
    st.session_state.step = 1

# Grade Mapping
def grade(score):
    return {
        10: 'O', 9: 'A+', 8: 'A',
        7: 'B+', 6: 'B', 5: 'C'
    }.get(score, '')

# Welcome message
st.title("CGPA Calculator")
st.markdown("#### Welcome! This tool helps you calculate your CGPA accurately.")

# Step 1: User Info
if st.session_state.step == 1:
    st.header("Enter Your Details")

    name = st.text_input("Name")
    college = st.text_input("College")
    department = st.text_input("Department")

    entry_type = st.selectbox("Entry Type", ["Regular", "Lateral", "Sandwich - Regular", "Sandwich - Lateral"])
    cgpa_available = st.radio("Do you already have an existing CGPA?", ["No", "Yes"])

    if st.button("Proceed"):
        if all([name, college, department]):
            st.session_state.user_data = {
                "Name": name,
                "College": college,
                "Department": department,
                "EntryType": entry_type,
                "CGPAAvailable": cgpa_available
            }
            st.session_state.step = 2
        else:
            st.warning("Please complete all fields.")

# Step 2: Existing CGPA entry if applicable
if st.session_state.step == 2:
    user = st.session_state.user_data
    if user["CGPAAvailable"] == "Yes":
        st.header("Existing CGPA Details")
        completed_sem = st.number_input("How many semesters completed?", min_value=0, max_value=10, step=1)
        existing_cgpa = st.number_input("Enter your existing CGPA", min_value=1.0, max_value=10.0, step=0.01, format="%.2f")
        earned_credits = st.number_input("Credits earned up to previous semesters", min_value=1, step=1)

        if st.button("Continue to Balance Semesters"):
            st.session_state.user_data.update({
                "CompletedSemesters": completed_sem,
                "ExistingCGPA": existing_cgpa,
                "EarnedCredits": earned_credits
            })
            st.session_state.step = 3
    else:
        st.session_state.user_data.update({
            "CompletedSemesters": 0,
            "ExistingCGPA": 0.0,
            "EarnedCredits": 0
        })
        st.session_state.step = 3

# Step 3: CGPA Calculator
if st.session_state.step == 3:
    user = st.session_state.user_data
    st.header("Enter Semester-wise Marks")

    # Determine semester range
    entry = user["EntryType"]
    sem_start = 1 if "Lateral" not in entry else 3
    sem_max = 8 if "Sandwich" not in entry else 10

    available_sem = list(range(sem_start, sem_max + 1))
    remaining = [i for i in available_sem if i > user["CompletedSemesters"]]
    sem_count = len(remaining)

    if sem_count < 1:
        st.warning("All semesters are already completed. No more semesters left to enter.")
        st.stop()

    # Avoid Streamlit slider crash when min=max=1
    if sem_count == 1:
        st.info("Only one semester left to enter.")
        sem_limit = 1
    else:
        sem_limit = st.slider(
            "Select number of semesters you want to enter",
            min_value=1,
            max_value=sem_count,
            value=sem_count
        )

    records = []

    for idx in range(sem_limit):
        sem = remaining[idx]
        with st.expander(f"Semester {sem}"):
            num_courses = st.number_input(f"Number of Courses in Semester {sem}", min_value=1, value=5, step=1, key=f"course_num_{sem}")
            for course in range(1, num_courses + 1):
                col1, col2 = st.columns(2)
                with col1:
                    credit = st.selectbox(f"Course {course} Credit", [1, 2, 3, 4], key=f"credit_{sem}_{course}")
                with col2:
                    score = st.selectbox(f"Course {course} Score", list(range(5, 11)), key=f"score_{sem}_{course}")
                records.append({"Semester": sem, "Credit": credit, "Score": score, "Grade": grade(score)})

    if st.button("Calculate CGPA"):
        df = pd.DataFrame(records)
        df["Weighted"] = df["Credit"] * df["Score"]

        total_new_credits = df["Credit"].sum()
        total_new_weighted = df["Weighted"].sum()

        # Combine with existing CGPA if available
        total_credits = user["EarnedCredits"] + total_new_credits
        total_weighted = (user["ExistingCGPA"] * user["EarnedCredits"]) + total_new_weighted
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

        # Generate HTML report with border and professional style
        html = f"""
        <html>
        <head>
        <style>
        body {{ font-family: 'Roboto', sans-serif; margin: 40px; background-color: #f5f7fa; }}
        h1, h2 {{ text-align: center; color: #0b3d91; }}
        .page {{ page-break-after: always; border: 3px solid #0b3d91; border-radius: 10px; padding: 20px; background-color: white; }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 15px; }}
        th, td {{ border: 1px solid #0b3d91; padding: 10px; text-align: center; }}
        th {{ background-color: #c3d1f7; font-weight: 700; }}
        .watermark {{ position: fixed; bottom: 10px; width: 100%; text-align: center; font-size: 12px; color: gray; }}
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
        </div>
        <div class="page">
            <h2>Semester-wise GPA</h2>
            {sem_stats.to_html(index=False)}
        </div>
        """

        for sem in sorted(df['Semester'].unique()):
            sem_data = df[df['Semester'] == sem][["Credit", "Score", "Grade", "Weighted"]]
            html += f"<div class='page'><h2>Semester {sem} Details</h2>{sem_data.to_html(index=False)}</div>"

        html += """
        <div class='watermark'>Disclaimer! This CGPA was calculated based on data fed by student</div>
        </body></html>
        """

        # Show print button and HTML report with embedded JS print function
        st.markdown("""
            <button class="print-button" onclick="window.print()">Print Report</button>
            """, unsafe_allow_html=True)

        st.components.v1.html(html, height=900, scrolling=True)
