import streamlit as st
import pandas as pd
import datetime
import os

# Load workout plan
excel_file = "Workout_Plan_Azerbaijan_June16.xlsx"
log_file = "workout_log.csv"

if not os.path.exists(excel_file):
    st.error("Workout plan not found. Please upload the Excel file to the repo.")
else:
    df = pd.read_excel(excel_file)
    df["Date"] = pd.to_datetime(df["Date"]).dt.date

    # Load logs if they exist
    if os.path.exists(log_file):
        logs = pd.read_csv(log_file)
        logs["Date"] = pd.to_datetime(logs["Date"]).dt.date
    else:
        logs = pd.DataFrame(columns=["Date", "Exercise", "Reps", "Weight", "RPE", "Sleep Hours", "Other Workout", "Notes"])

    # Find next uncompleted workout
    completed_dates = logs["Date"].unique() if not logs.empty else []
    next_workout_row = df[~df["Date"].isin(completed_dates)].head(1)

    if not next_workout_row.empty:
        today_workout = next_workout_row.iloc[0]
        workout_date = today_workout["Date"]
        st.title("🏋️ Wrestling Workout of the Day")
        st.subheader(f"{today_workout['Day']} – {today_workout['Focus']}")
        st.markdown(f"📅 **Date:** {workout_date.strftime('%A, %B %d')}")
        st.write(today_workout["Workout Plan"])

        # Parse exercises
        raw_plan = str(today_workout["Workout Plan"])
        exercises = [line.strip() for line in raw_plan.split("\n") if line.strip()]

        st.markdown("---")
        st.header("📒 Log Your Workout")

        with st.form("log_form"):
            st.markdown("### Exercise Log")
            logs_to_add = []
            for ex in exercises:
                st.markdown(f"**{ex}**")
                reps = st.text_input(f"Reps – {ex}", key=f"reps_{ex}")
                weight = st.text_input(f"Weight – {ex}", key=f"wt_{ex}")
                rpe = st.slider(f"RPE – {ex}", 1, 10, 7, key=f"rpe_{ex}")
                logs_to_add.append({
                    "Date": workout_date,
                    "Exercise": ex,
                    "Reps": reps,
                    "Weight": weight,
                    "RPE": rpe
                })

            st.markdown("### Additional Info")
            sleep = st.slider("Sleep Hours Last Night", 0, 12, 8)
            other = st.text_input("Other Workout (grappling, volleyball, etc.)")
            notes = st.text_area("General Notes")
            submitted = st.form_submit_button("Save Log")

        if submitted:
            for row in logs_to_add:
                row["Sleep Hours"] = sleep
                row["Other Workout"] = other
                row["Notes"] = notes

            new_log_df = pd.DataFrame(logs_to_add)
            logs = pd.concat([logs, new_log_df], ignore_index=True)
            logs.to_csv(log_file, index=False)
            st.success("✅ Workout logged!")

    else:
        st.info("✅ All workouts have been logged!")

    # Optional: RPE chart
    st.markdown("---")
    if st.checkbox("📊 Show RPE Over Time"):
        if not logs.empty:
            rpe_chart = logs.groupby(["Date", "Exercise"])["RPE"].mean().unstack()
            st.line_chart(rpe_chart)
        else:
            st.info("No logs found yet.")
