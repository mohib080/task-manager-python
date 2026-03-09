from task_manager import TaskManager
from scheduler import create_schedule

tm = TaskManager('tasks.csv')
tasks = tm.get_tasks()
schedule = create_schedule(tasks)

events = []
color_map = {
    1: "#FF4B4B",
    2: "#FF8C00",
    3: "#FFCE56",
    4: "#36A2EB",
    5: "#4BC0C0"
}

if not schedule.empty:
    for idx, row in schedule.iterrows():
        events.append({
            "title": f"[{row['priority']}] {row['name']}",
            "start": row['scheduled_start'].isoformat(),
            "end": row['scheduled_end'].isoformat(),
            "backgroundColor": color_map.get(row['priority'], "#3788d8"),
            "borderColor": color_map.get(row['priority'], "#3788d8"),
        })

print(events)
