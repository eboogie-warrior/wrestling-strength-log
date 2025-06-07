import streamlit as st
import pandas as pd
import datetime
import os

# Load the workout plan file
excel_file = "Workout_Plan_Azerbaijan_June16.xlsx"
if not os.path.exists(excel_file):
    st.error("Workout plan not found. Please upload the Excel file to the repo.")
else:
    df = pd.read_excel(excel_file)
    df["Date"] = pd.to_datetime(df["Date"]).dt.date

    # Get today's date
    today = datetime.date.today()

    # Try to match today's workout
    if today in df["Date"].values:
        today_workout = df[df["Date"] == today].iloc[0]

        st.title("🏋️ Wrestling Workout of the Day")
        st.subheader(f"{today_workout['Day']} – {today_workout['Focus']}")
        st.write(today_workout["Workout Plan"])
    else:
        st.warning("No workout scheduled for today.")

    # Workout logging section
    st.markdown("---")
    st.header("📒 Log Your Workout")
    with st.form("log_form"):
        reps = st.text_input("Reps Completed")
        weight = st.text_input("Weight Used (if any)")
        rpe = st.slider("Rate of Perceived Exertion (1–10)", 1, 10, 7)
        notes = st.text_area("Notes (optional)")
        submitted = st.form_submit_button("Save Log")

    if submitted:
        log = {
            "Date": str(today),
            "Reps": reps,
            "Weight": weight,
            "RPE": rpe,
            "Notes": notes
        }
        if os.path.exists("workout_log.csv"):
            logs = pd.read_csv("workout_log.csv")
            logs = pd.concat([logs, pd.DataFrame([log])], ignore_index=True)
        else:
            logs = pd.DataFrame([log])
        logs.to_csv("workout_log.csv", index=False)
        st.success("Workout logged!")

    # View logs
    if st.checkbox("📋 Show Past Logs"):
        if os.path.exists("workout_log.csv"):
            logs = pd.read_csv("workout_log.csv")
            st.dataframe(logs)
        else:
            st.info("No logs found yet.")
