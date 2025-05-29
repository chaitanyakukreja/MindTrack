import csv, os
from datetime import datetime
from collections import Counter
import matplotlib.pyplot as plt

HABITS = ["Exercise", "Meditation", "Reading"]
DATA_FILE = "data/logs.csv"
CHART_DIR = "charts"

def initialize():
    os.makedirs("data", exist_ok=True)
    os.makedirs("charts", exist_ok=True)
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["Date", "Mood", "Reason", "Intention", "Reflection"] + HABITS)

def log_entry():
    date = datetime.now().strftime("%Y-%m-%d")
    intention = input("🌞 What's your intention today? ")
    mood = input("🙂 Mood today (happy, sad, stressed...)? ").lower()
    reason = input("💬 Reason for this mood? ")
    reflection = input("🌙 Reflection: What went well or could be better? ")

    habits_done = []
    for habit in HABITS:
        done = input(f"✔️ Did you do '{habit}' today? (yes/no): ").strip().lower()
        habits_done.append("yes" if done == "yes" else "no")

    with open(DATA_FILE, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([date, mood, reason, intention, reflection] + habits_done)

    print("\n✅ Entry saved!\n")

def monthly_report():
    now = datetime.now()
    this_month = now.strftime("%Y-%m")
    moods, reasons = [], []
    habits_summary = Counter()

    with open(DATA_FILE, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row["Date"].startswith(this_month):
                moods.append(row["Mood"])
                reasons.append(row["Reason"])
                for habit in HABITS:
                    if row[habit].lower() == "yes":
                        habits_summary[habit] += 1

    if not moods:
        print("⚠️ No entries this month.")
        return

    # Mood Pie Chart
    mood_counts = Counter(moods)
    plt.figure(figsize=(6, 6))
    plt.pie(mood_counts.values(), labels=mood_counts.keys(), autopct='%1.1f%%')
    plt.title(f"Mood Distribution - {this_month}")
    mood_chart_path = f"{CHART_DIR}/mood_{this_month}.png"
    plt.savefig(mood_chart_path)
    plt.close()

    # Habit Bar Chart
    plt.figure(figsize=(6, 4))
    plt.bar(habits_summary.keys(), habits_summary.values(), color='skyblue')
    plt.title(f"Habit Completion - {this_month}")
    plt.ylabel("Days Completed")
    plt.savefig(f"{CHART_DIR}/habits_{this_month}.png")
    plt.close()

    print(f"\n📊 Monthly Insights ({this_month})")
    print(f" - Mood entries: {len(moods)}")
    print(f" - Top 3 mood reasons: {Counter(reasons).most_common(3)}")
    print(f" - Habit Completion: {dict(habits_summary)}")
    print(f" - Charts saved in 'charts/' folder.\n")

def main():
    initialize()
    while True:
        print("\nWhat would you like to do?")
        print("1. Log Today")
        print("2. View Monthly Report")
        print("3. Exit")
        choice = input("Choose 1, 2, or 3: ")
        if choice == "1":
            log_entry()
        elif choice == "2":
            monthly_report()
        elif choice == "3":
            print("👋 Take care. Keep growing.")
            break
        else:
            print("❌ Invalid option.")

if __name__ == "__main__":
    main()
