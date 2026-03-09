import argparse
from datetime import datetime
from task_manager import TaskManager
from scheduler import create_schedule
from visualization import plot_gantt_chart, plot_priority_distribution

def display_menu():
    print("\n--- Task Manager & Scheduler ---")
    print("1. Add Task")
    print("2. Remove Task")
    print("3. View All Tasks")
    print("4. Generate Schedule & View Gantt Chart")
    print("5. View Priority Distribution Chart")
    print("6. Exit")
    print("--------------------------------")

def main():
    tm = TaskManager('tasks.csv')
    
    while True:
        display_menu()
        choice = input("Enter your choice (1-6): ")
        
        if choice == '1':
            name = input("Task name: ")
            try:
                duration = float(input("Duration (hours): "))
                priority = int(input("Priority (1-Highest, 5-Lowest): "))
                deadline = input("Deadline (YYYY-MM-DD HH:MM): ")
                # Just formatting check
                datetime.strptime(deadline, "%Y-%m-%d %H:%M")
                tm.add_task(name, duration, priority, deadline)
            except ValueError:
                print("Invalid input format. Ensure time is YYYY-MM-DD HH:MM. Please try again.")
                
        elif choice == '2':
            try:
                task_id = int(input("Task ID to remove: "))
                tm.remove_task(task_id)
            except ValueError:
                print("Invalid ID.")
                
        elif choice == '3':
            tasks = tm.get_tasks()
            if tasks.empty:
                print("No tasks found.")
            else:
                print("\nCurrent Tasks:")
                print(tasks.to_string(index=False))
                
        elif choice == '4':
            tasks = tm.get_tasks()
            if not tasks.empty:
                print("Generating schedule...")
                scheduled_df = create_schedule(tasks)
                print("\nScheduled Tasks:")
                print(scheduled_df[['name', 'priority', 'scheduled_start', 'scheduled_end']].to_string(index=False))
                print("\nOpening Gantt Chart...")
                plot_gantt_chart(scheduled_df)
            else:
                print("No tasks to schedule.")
                
        elif choice == '5':
            tasks = tm.get_tasks()
            if not tasks.empty:
                plot_priority_distribution(tasks)
            else:
                print("No tasks available.")
                
        elif choice == '6':
            print("Exiting...")
            break
        else:
            print("Invalid choice.")

if __name__ == "__main__":
    main()
