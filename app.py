import streamlit as st
import pandas as pd
import os
import csv
from datetime import datetime, timedelta
import matplotlib.pyplot as plt

# --- Constants ---
HABITS = [
    "Exercise",
    "Meditation",
    "Reading",
    "Healthy Eating",
    "Sleep 7+ hours",
]

DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)

# --- Helper functions ---

def get_user_filename(username):
    safe_username = username.strip().replace(" ", "_").lower()
    return os.path.join(DATA_DIR, f"{safe_username}_logs.csv")

def initialize_file(user_file):
    if not os.path.exists(user_file):
        with open(user_file, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["Date", "Mood", "Reason", "Intention", "Reflection"] + HABITS)

def save_entry(user_file, date, mood, reason, intention, reflection, habits_done):
    with open(user_file, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([date, mood, reason, intention, reflection] + habits_done)

def load_entries(user_file):
    if not os.path.exists(user_file):
        return pd.DataFrame()
    df = pd.read_csv(user_file, parse_dates=["Date"])
    return df

def plot_summary(df, period='weekly'):
    if df.empty:
        st.write("No data to show yet.")
        return

    df = df.copy()
    df["Date"] = pd.to_datetime(df["Date"])
    today = pd.Timestamp(datetime.today().date())
    
    if period == 'weekly':
        start_date = today - timedelta(days=7)
        df_period = df[df["Date"] >= start_date]
        title = "Last 7 Days Mood & Habits"
    else:  # monthly
        start_date = today - timedelta(days=30)
        df_period = df[df["Date"] >= start_date]
        title = "Last 30 Days Mood & Habits"

    if df_period.empty:
        st.write(f"No {period} data to show yet.")
        return

    # Plot average mood by day
    mood_map = {"😞": 1, "😐": 2, "😊": 3, "😄": 4, "🤩": 5}
    df_period["Mood_Score"] = df_period["Mood"].map(mood_map).fillna(0)

    mood_by_date = df_period.groupby("Date")["Mood_Score"].mean()

    fig, ax = plt.subplots(figsize=(10, 4))
    mood_by_date.plot(kind='bar', ax=ax)
    ax.set_ylabel("Average Mood Score (1-5)")
    ax.set_ylim(0,5)
    ax.set_title(title)
    plt.xticks(rotation=45)
    st.pyplot(fig)

    # Plot habit completion rate
    habits_data = df_period[HABITS].astype(int)
    habit_means = habits_data.mean().sort_values(ascending=False)

    st.write("Habit completion rate:")
    st.bar_chart(habit_means)

# --- Streamlit app start ---

st.title("Daily Mood & Habit Tracker")

username = st.text_input("Enter your username")

if username:
    user_file = get_user_filename(username)
    initialize_file(user_file)

    df = load_entries(user_file)

    st.header("Log today's mood")

    # Date default today
    today_str = datetime.today().strftime("%Y-%m-%d")
    date = st.date_input("Date", value=datetime.today())

    mood = st.selectbox("How do you feel today?", ["😞", "😐", "😊", "😄", "🤩"])
    reason = st.text_area("What is the main reason for your mood?")
    intention = st.text_area("What is your positive intention or goal for tomorrow?")
    reflection = st.text_area("Any reflection or notes about today?")

    st.write("Select habits you did today:")
    habits_done = []
    for habit in HABITS:
        done = st.checkbox(habit)
        habits_done.append(1 if done else 0)

    if st.button("Save Entry"):
        # Check if date already logged
        if not df.empty and (df["Date"] == pd.Timestamp(date)).any():
            st.warning("You already logged data for this date!")
        else:
            save_entry(user_file, date.strftime("%Y-%m-%d"), mood, reason, intention, reflection, habits_done)
            st.success("Entry saved! Refresh to see updated data.")

    # Show past logs
    st.header("Your past logs")
    if df.empty:
        st.info("No logs yet.")
    else:
        df_display = df.sort_values("Date", ascending=False)
        df_display[HABITS] = df_display[HABITS].astype(int)
        st.dataframe(df_display)

    # Reports section
    st.header("Weekly & Monthly Insights")

    st.subheader("Weekly Summary")
    plot_summary(df, period="weekly")

    st.subheader("Monthly Summary")
    plot_summary(df, period="monthly")

else:
    st.info("Please enter your username to start tracking.")

