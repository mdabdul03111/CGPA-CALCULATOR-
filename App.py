import streamlit as st
import pandas as pd
import re

st.set_page_config(page_title="CGPA Calculator", layout="centered")

if "user_submitted" not in st.session_state:
    st.session_state.user_submitted = False

# Grade calculator
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

# Email and mobile validators
def is_valid_email(email):
    return re.match(r"[^@]+@[^@]+\.[^@]+", email)

def is_valid_mobile(mobile):
    return re.match(r"^[6-9]\d{9}$", mobile)

# Step 1: User Details
if not st.session_state.user_submitted:
    st.title("Welcome to CGPA Calculator")
    st.markdown("### Please fill in your details:")

    name = st.text_input("Name")
    college = st.text_input("College")
    department = st.text_input("Department")
    mobile = st.text_input("Mobile Number")
    email = st.text_input("Email ID")

    if st.button("Submit"):
        if not all([name, college, department, mobile, email]):
            st.warning("Please fill all fields before proceeding.")
        elif not is_valid_mobile(mobile):
            st.warning("Enter a valid 10-digit Indian mobile number.")
        elif not is_valid_email(email):
            st.warning("Enter a valid email address.")
        else:
            st.session_state.user_data = {
                "Name": name,
                "College": college,
                "Department": department,
                "Mobile": mobile,
                "Email": email
            }
            st.session_state.user_submitted = True

# Step 2: CGPA Calculator
if st.session_state.user_submitted:
    st.title("CGPA Calculator")

    user = st.session_state.user_data
    st.info(f"**{user['Name']}**\n{user['College']} – {user['Department']}\nMobile: {user['Mobile']} | Email: {user['Email']}")

    total_semesters = st.number_input("Number of Semesters", min_value=1, step=1, value=2)

    records = []
    for sem in range(1, total_semesters + 1):
        with st.expander(f"Semester {sem}"):
            num_courses = st.number_input(f"Number of Courses in Semester {sem}", min_value=1, step=1, value=5, key=f"courses_{sem}")
            for course in range(1, num_courses + 1):
                col1, col2 = st.columns(2)
                with col1:
                    credit = st.selectbox(f"Course {course} Credit", [0, 1, 2, 3, 4], key=f"credit_{sem}_{course}")
                with col2:
                    score = st.selectbox(f"Course {course} Score", list(range(5, 11)), key=f"score_{sem}_{course}")
                records.append({"Semester": sem, "Course": course, "Credit": credit, "Score": score})

    if st.button("Calculate CGPA"):
        df = pd.DataFrame(records)
        df["Weighted"] = df["Credit"] * df["Score"]
        df["Grade"] = df["Score"].apply(get_grade)

        total_credits = df["Credit"].sum()
        total_weighted = df["Weighted"].sum()
        overall_cgpa = total_weighted / total_credits if total_credits > 0 else 0.0

        sem_stats = df.groupby("Semester").agg(Credits=("Credit", "sum"), WeightedScore=("Weighted", "sum")).reset_index()
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
                body {{
                    font-family: Arial;
                    border: 4px solid #000;
                    padding: 20px;
                    margin: 20px;
                }}
                h1, h2 {{
                    text-align: center;
                }}
                .info {{
                    font-size: 16px;
                    margin-bottom: 20px;
                }}
                table {{
                    width: 100%;
                    border-collapse: collapse;
                    margin-top: 15px;
                    font-size: 14px;
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
                    bottom: 100px;
                    width: 100%;
                    text-align: center;
                    opacity: 0.1;
                    font-size: 28px;
                    transform: rotate(-30deg);
                }}
                .disclaimer {{
                    text-align: center;
                    font-size: 12px;
                    color: gray;
                    margin-top: 20px;
                }}
                .page {{
                    page-break-after: always;
                }}
                .print-btn {{
                    text-align: center;
                    margin-top: 20px;
                }}
            </style>
        </head>
        <body>
            <div class="watermark">Disclaimer: CGPA was calculated based on the data feed by student</div>
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
            html += "</table></div>"

        html += """
            <div class="disclaimer">Disclaimer: CGPA was calculated based on the data feed by student</div>
            <div class="print-btn"><button onclick="window.print()">Print Report</button></div>
        </body>
        </html>
        """

        st.components.v1.html(html, height=1300, scrolling=True)
