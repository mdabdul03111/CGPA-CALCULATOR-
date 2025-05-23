import streamlit as st
import pandas as pd
import streamlit.components.v1 as components

st.set_page_config(page_title="CGPA Calculator", layout="centered")
st.title("CGPA Calculator by Semester")

st.markdown(
    "Enter the number of semesters. For each semester, select credits (0–4) and scores (5–10)."
)

# Input number of semesters
total_semesters = st.number_input("Number of semesters", min_value=1, step=1, value=2)

# Collect data
records = []
for sem in range(1, total_semesters + 1):
    with st.expander(f"Semester {sem}"):
        num_courses = st.number_input(
            f"Courses in Semester {sem}",
            min_value=1,
            step=1,
            value=5,
            key=f"num_courses_{sem}"
        )
        for course in range(1, num_courses + 1):
            col1, col2 = st.columns(2)
            with col1:
                credit = st.selectbox(
                    f"Sem {sem} - Course {course} Credit Hours",
                    options=[0, 1, 2, 3, 4],
                    key=f"credit_{sem}_{course}"
                )
            with col2:
                score = st.selectbox(
                    f"Sem {sem} - Course {course} Score",
                    options=list(range(5, 11)),
                    key=f"score_{sem}_{course}"
                )
            records.append({"Semester": sem, "Credit": credit, "Score": score})

# Generate result and printable view
if st.button("Calculate CGPA"):
    df = pd.DataFrame(records)
    df["Weighted"] = df["Credit"] * df["Score"]
    total_credits = df["Credit"].sum()
    total_weighted = df["Weighted"].sum()
    overall_cgpa = total_weighted / total_credits if total_credits > 0 else 0.0

    st.success(f"Overall CGPA: {overall_cgpa:.2f}")
    
    sem_stats = (
        df.groupby("Semester")
        .agg(Credits=("Credit", "sum"), WeightedScore=("Weighted", "sum"))
        .reset_index()
    )
    sem_stats["GPA"] = sem_stats["WeightedScore"] / sem_stats["Credits"]

    # HTML Report for Print/PDF
    html = """
    <html>
    <head>
    <style>
        @media print {
            .pagebreak { page-break-before: always; }
        }
        body {
            font-family: Arial;
            margin: 40px;
        }
        .sheet {
            border: 2px solid black;
            padding: 20px;
        }
        h1 {
            text-align: center;
            font-size: 24px;
            margin-bottom: 30px;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 20px;
        }
        th, td {
            border: 1px solid #333;
            padding: 8px;
            text-align: center;
        }
        button {
            margin-top: 20px;
        }
    </style>
    </head>
    <body>
    """
    for sem in range(1, total_semesters + 1):
        sem_df = df[df["Semester"] == sem]
        html += f"""
        <div class="sheet">
            <h1>Score Sheet - Semester {sem}</h1>
            <table>
                <tr><th>Course</th><th>Credit</th><th>Score</th><th>Weighted</th></tr>
        """
        for i, row in sem_df.iterrows():
            html += f"<tr><td>{i+1}</td><td>{row['Credit']}</td><td>{row['Score']}</td><td>{row['Weighted']}</td></tr>"
        gpa = sem_stats[sem_stats["Semester"] == sem]["GPA"].values[0]
        html += f"""
            </table>
            <p><strong>Semester GPA:</strong> {gpa:.2f}</p>
        </div>
        <div class="pagebreak"></div>
        """

    html += f"""
    <div class="sheet">
        <h1>Overall Summary</h1>
        <p><strong>Total Credits:</strong> {total_credits}</p>
        <p><strong>Overall CGPA:</strong> {overall_cgpa:.2f}</p>
    </div>
    <br>
    <button onclick="window.print()">Print or Save as PDF</button>
    </body>
    </html>
    """

    components.html(html, height=1000, scrolling=True)
