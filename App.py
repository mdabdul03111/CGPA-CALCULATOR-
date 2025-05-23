import streamlit as st
import pandas as pd

# App title
st.set_page_config(page_title="CGPA Calculator", layout="centered")

if "user_submitted" not in st.session_state:
    st.session_state.user_submitted = False

# Step 1: User Details Page
if not st.session_state.user_submitted:
    st.title("Welcome to CGPA Calculator")

    st.markdown("### Please fill in your details:")

    name = st.text_input("Name")
    college = st.text_input("College")
    department = st.text_input("Department")
    mobile = st.text_input("Mobile Number")
    email = st.text_input("Email ID")

    if st.button("Submit"):
        if all([name, college, department, mobile, email]):
            st.session_state.user_data = {
                "Name": name,
                "College": college,
                "Department": department,
                "Mobile": mobile,
                "Email": email
            }
            st.session_state.user_submitted = True
        else:
            st.warning("Please fill all fields before proceeding.")

# Step 2: CGPA Calculator
if st.session_state.user_submitted:
    st.title("CGPA Calculator")

    user = st.session_state.user_data
    st.info(f"CGPA result will be shown for:\n\n**{user['Name']}**\n{user['College']} – {user['Department']}\nMobile: {user['Mobile']}\nEmail: {user['Email']}")

    # Get number of semesters
    total_semesters = st.number_input("Number of Semesters", min_value=1, step=1, value=2)

    records = []
    for sem in range(1, total_semesters + 1):
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

        result_df = df.copy()
        result_df["User"] = user["Name"]
        result_df["College"] = user["College"]
        result_df["Department"] = user["Department"]
        result_df["Mobile"] = user["Mobile"]
        result_df["Email"] = user["Email"]
        result_df["Overall CGPA"] = overall_cgpa

        csv = result_df.to_csv(index=False).encode("utf-8")
        st.download_button(
            "Download Result as CSV",
            data=csv,
            file_name="cgpa_results.csv",
            mime="text/csv"
        )
