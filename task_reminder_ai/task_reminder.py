import json
from datetime import datetime
import os
from plyer import notification

TASK_FILE = "tasks.json"


# Load tasks
def load_tasks():
    if not os.path.exists(TASK_FILE):
        return []
    with open(TASK_FILE, "r") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []  # if file is empty/corrupted


# Save tasks
def save_tasks(tasks):
    with open(TASK_FILE, "w") as f:
        json.dump(tasks, f, indent=4)


# Add task
def add_task(task_name, deadline):
    try:
        datetime.strptime(deadline, "%Y-%m-%d")  # validate date
    except ValueError:
        print("❌ Invalid date format! Use YYYY-MM-DD.")
        return

    tasks = load_tasks()
    tasks.append({"task": task_name, "deadline": deadline})
    save_tasks(tasks)
    print(f"✅ Task '{task_name}' added with deadline {deadline}")


# Check reminders
def check_reminders():
    tasks = load_tasks()
    if not tasks:
        print("📭 No tasks found. Add one first!")
        return

    today = datetime.now().date()
    reminders_found = False

    for task in tasks:
        try:
            deadline = datetime.strptime(task["deadline"], "%Y-%m-%d").date()
        except ValueError:
            print(f"⚠️ Skipping invalid deadline for task '{task['task']}'")
            continue

        days_left = (deadline - today).days

        if days_left == 2:
            reminders_found = True
            show_notification(f"Reminder: {task['task']}", f"Deadline in 2 days: {deadline}")
        elif days_left == 0:
            reminders_found = True
            show_notification(f"ALERT: {task['task']}", f"Deadline is TODAY: {deadline}")
        elif days_left < 0:
            print(f"❌ Missed: '{task['task']}' (Deadline was {deadline})")

    if not reminders_found:
        print("👍 No upcoming deadlines within 2 days.")


# Desktop notification
def show_notification(title, message):
    notification.notify(
        title=title,
        message=message,
        timeout=10  # seconds
    )
    print(f"🔔 {title} - {message}")


# CLI menu
def main():
    while True:
        print("\n=== Task Reminder AI ===")
        print("1. Add Task")
        print("2. Daily Reminder Check")
        print("3. Exit")

        choice = input("Enter choice: ")

        if choice == "1":
            task_name = input("Enter task name: ")
            deadline = input("Enter deadline (YYYY-MM-DD): ")
            add_task(task_name, deadline)
        elif choice == "2":
            check_reminders()
        elif choice == "3":
            print("👋 Exiting Task Reminder AI. Stay productive!")
            break
        else:
            print("Invalid choice. Try again.")


if __name__ == "__main__":
    main()
