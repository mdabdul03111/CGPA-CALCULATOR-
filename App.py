import streamlit as st
import pandas as pd

st.title("CGPA Calculator")

st.markdown(
    "Enter the number of semesters, then for each semester, specify the number of courses "
    "and input credit hours (0–4) and score (5–10)."
)

# Input number of semesters
total_semesters = st.number_input(
    "Number of semesters", min_value=1, step=1, value=2
)

# Collect course records
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

# Calculate CGPA on button click
if st.button("Calculate CGPA"):
    df = pd.DataFrame(records)
    df["Weighted"] = df["Credit"] * df["Score"]

    # Overall CGPA
    total_credits = df["Credit"].sum()
    total_weighted = df["Weighted"].sum()
    overall_cgpa = total_weighted / total_credits if total_credits > 0 else 0.0

    # Semester-wise GPA
    sem_stats = (
        df.groupby("Semester")
        .agg(Credits=("Credit", "sum"), WeightedScore=("Weighted", "sum"))
        .reset_index()
    )
    sem_stats["GPA"] = sem_stats["WeightedScore"] / sem_stats["Credits"]

    # Display results
    st.subheader("Overall Results")
    st.write(f"**Total Credits:** {total_credits}")
    st.write(f"**Overall CGPA:** {overall_cgpa:.2f}")

    st.subheader("Semester-wise GPA")
    st.dataframe(sem_stats[["Semester", "Credits", "GPA"]])

    st.subheader("Detailed Breakdown")
    st.dataframe(df)

    # Download results
    result_df = df.copy()
    result_df["Overall CGPA"] = overall_cgpa
    csv = result_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        "Download Detailed Results as CSV",
        data=csv,
        file_name="cgpa_by_semester.csv",
        mime="text/csv"
    )
