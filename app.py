import streamlit as st
import pandas as pd
import datetime
import os

excel_file = "Workout_Plan_Azerbaijan_June16.xlsx"

# Load the workout plan
if not os.path.exists(excel_file):
    st.error("Workout plan not found. Please upload the Excel file to the repo.")
else:
    df = pd.read_excel(excel_file)
    df["Date"] = pd.to_datetime(df["Date"]).dt.date
    today = datetime.date.today()
    upcoming = df[df["Date"] >= today]

    if not upcoming.empty:
        today_workout = upcoming.iloc[0]
        st.title("🏋️ Wrestling Workout of the Day")
        st.subheader(f"{today_workout['Day']} – {today_workout['Focus']}")
        st.write(today_workout["Workout Plan"])

        # Parse exercises
        raw_plan = str(today_workout["Workout Plan"])
        exercises = [line.strip() for line in raw_plan.split("\n") if line.strip()]

        st.markdown("---")
        st.header("📒 Log Your Workout")

        with st.form("log_form"):
            st.markdown("### Exercise Log")
            logs = []
            for ex in exercises:
                st.markdown(f"**{ex}**")
                reps = st.text_input(f"Reps – {ex}", key=f"reps_{ex}")
                weight = st.text_input(f"Weight – {ex}", key=f"wt_{ex}")
                rpe = st.slider(f"RPE – {ex}", 1, 10, 7, key=f"rpe_{ex}")
                logs.append({"Date": str(today), "Exercise": ex, "Reps": reps, "Weight": weight, "RPE": rpe})

            st.markdown("### Additional Info")
            sleep = st.slider("Sleep Hours Last Night", 0, 12, 8)
            extra = st.text_input("Other Workout (grappling, volleyball, etc.)")
            notes = st.text_area("General Notes")

            submit = st.form_submit_button("Save Log")

        if submit:
            df_log = pd.DataFrame(logs)
            df_log["Sleep Hours"] = sleep
            df_log["Other Workout"] = extra
            df_log["Notes"] = notes

            if os.path.exists("workout_log.csv"):
                prev = pd.read_csv("workout_log.csv")
                df_log = pd.concat([prev, df_log], ignore_index=True)

            df_log.to_csv("workout_log.csv", index=False)
            st.success("✅ Workout logged!")

    else:
        st.warning("No upcoming workouts found.")

    # RPE Progress Chart
    if st.checkbox("📊 Show RPE Over Time"):
        if os.path.exists("workout_log.csv"):
            logs = pd.read_csv("workout_log.csv")
            logs["Date"] = pd.to_datetime(logs["Date"])
            chart = logs.groupby(["Date", "Exercise"])["RPE"].mean().unstack()
            st.line_chart(chart)
        else:
            st.info("No logs found yet.")
