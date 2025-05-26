import streamlit as st
import pandas as pd

# Set up Streamlit page
st.set_page_config(page_title="CGPA Calculator", layout="centered", page_icon="🎓")

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

# Custom CSS for professional colors and fonts
st.markdown("""
    <style>
    body, .css-18e3th9 {
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        background-color: #f0f4f8;
        color: #1e293b;
    }
    .stButton>button {
        background-color: #2563eb;
        color: white;
        font-weight: 600;
        border-radius: 8px;
        padding: 10px 24px;
        border: none;
        transition: background-color 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #1e40af;
        cursor: pointer;
    }
    .stTextInput>div>input, .stSelectbox>div>div>div>select {
        border-radius: 6px;
        border: 1.5px solid #2563eb;
        padding: 6px;
        font-size: 14px;
    }
    h1, h2, h3, h4 {
        color: #0f172a;
        font-weight: 700;
    }
    </style>
""", unsafe_allow_html=True)

# Title and welcome message
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

        # Report HTML with print functionality
        report_html = f"""
        <style>
        @media print {{
            body * {{
                visibility: hidden;
            }}
            #printable-area, #printable-area * {{
                visibility: visible;
            }}
            #printable-area {{
                position: absolute;
                left: 0;
                top: 0;
                width: 100%;
                margin: 0;
                padding: 0;
                background-color: white;
            }}
        }}
        .page {{
            page-break-after: always;
            border: 2px solid #2563eb;
            padding: 20px;
            margin: 20px 0;
            background-color: white;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            color: #1e293b;
        }}
        h1, h2 {{
            color: #0f172a;
            text-align: center;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 10px;
        }}
        th, td {{
            border: 1px solid #2563eb;
            padding: 8px;
            text-align: center;
        }}
        th {{
            background-color: #2563eb;
            color: white;
        }}
        .watermark {{
            position: fixed;
            bottom: 10px;
            width: 100%;
            text-align: center;
            font-size: 10px;
            color: gray;
        }}
        </style>

        <div id="printable-area">
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
            report_html += f"""
            <div class="page">
                <h2>Semester {sem} Details</h2>
                {sem_data.to_html(index=False)}
            </div>
            """

        report_html += """
            <div class="watermark">Disclaimer! This CGPA was calculated based on data fed by student</div>
        </div>
        """

        st.markdown(report_html, unsafe_allow_html=True)

        st.markdown("""
        <button onclick="printDiv('printable-area')" style="
            background-color:#2563eb;
            color:white;
            font-weight:600;
            border:none;
            padding:12px 28px;
            border-radius:8px;
            cursor:pointer;
            margin-top:20px;
        ">Print Report</button>

        <script>
        function printDiv(divId) {
            var printContents = document.getElementById(divId).innerHTML;
            var originalContents = document.body.innerHTML;
            document.body.innerHTML = printContents;
            window.print();
            document.body.innerHTML = originalContents;
            window.location.reload();
        }
        </script>
        """, unsafe_allow_html=True)
