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

    # Find the next available workout including today
    upcoming_workouts = df[df["Date"] >= today]

    if not upcoming_workouts.empty:
        today_workout = upcoming_workouts.iloc[0]
        st.title("🏋️ Wrestling Workout of the Day")
        st.subheader(f"{today_workout['Day']} – {today_workout['Focus']}")
        st.write(today_workout["Workout Plan"])
    else:
        st.warning("No upcoming workouts found.")

    # Workout logging section
    st.markdown("---")
    st.header("📒 Log Your Workout")
    st.markdown("""
    **RPE (Rate of Perceived Exertion)**  
    - 1–4: Easy effort (could’ve done many more)  
    - 5–6: Moderate effort (challenging but manageable)  
    - 7–8: Hard effort (few reps left in tank)  
    - 9–10: Max effort (failure or near failure)
    """)

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

        # Load or create log file
        if os.path.exists("workout_log.csv"):
            logs = pd.read_csv("workout_log.csv")
            logs = pd.concat([logs, pd.DataFrame([log])], ignore_index=True)
        else:
            logs = pd.DataFrame([log])

        logs.to_csv("workout_log.csv", index=False)
        st.success("Workout logged!")

        # Progression logic based on RPE
        if upcoming_workouts.shape[0] > 1:
            next_workout_index = upcoming_workouts.index[1]
            if "Workout Plan" in df.columns:
                current_plan = df.at[next_workout_index, "Workout Plan"]
                if isinstance(current_plan, str) and any(char.isdigit() for char in current_plan):
                    if rpe < 5:
                        df.at[next_workout_index, "Workout Plan"] = current_plan + " (↑5% load)"
                    elif rpe > 7:
                        df.at[next_workout_index, "Workout Plan"] = current_plan + " (↓5% load)"
                    else:
                        df.at[next_workout_index, "Workout Plan"] = current_plan + " (maintain load)"

    # View logs
    if st.checkbox("📋 Show Past Logs"):
        if os.path.exists("workout_log.csv"):
            logs = pd.read_csv("workout_log.csv")
            st.dataframe(logs)
        else:
            st.info("No logs found yet.")
