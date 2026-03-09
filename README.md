# 📝 Task Manager & Scheduler

A full-featured, interactive **task management and scheduling dashboard** built with Python, Streamlit, Pandas, NumPy, Matplotlib, and Plotly.

---

## 🚀 Features

### Task Management
- **Add, Edit, Remove Tasks** – Create tasks with a name, duration, priority, and deadline directly in the UI.
- **Task Status Tracking** – Mark tasks as `Pending`, `In Progress`, or `Completed`.
- **Task Progress Bar** – Track 0–100% completion for each individual task.
- **Recurring Tasks** – Set tasks to recur `Daily`, `Weekly`, or `Monthly`. Completing a recurring task automatically spawns the next occurrence.
- **Task Dependencies** – Define which task must be completed before another can begin.
- **Search & Filter** – Instantly filter by task name, status, or priority.
- **Persistent Storage** – All tasks are saved to a local `tasks.csv` file.

### Smart Scheduling
- **Heuristic Scoring Algorithm** – Tasks are automatically ordered using a weighted score based on priority and deadline proximity.
- **Business Hours Scheduling** – Tasks are only scheduled Monday–Friday, 9 AM to 5 PM. Long tasks automatically roll over to the next business day.
- **Weekend Skipping** – The scheduler never assigns work on Saturdays or Sundays.
- **Dependency Resolution** – Dependent tasks are always placed after their prerequisite tasks in the schedule.

### Interactive Visualizations
- **Gantt Chart** – An interactive Plotly timeline showing the full scheduled order of tasks with color-coded priorities.
- **Calendar View** – A FullCalendar-powered week/month/day view showing when tasks are scheduled.
- **Priority Distribution Chart** – An interactive Plotly donut chart breaking down tasks by priority level.

### Dashboard UX
- **Metrics Row** – At-a-glance metrics for Total, Completed, Pending/In Progress, Overdue, and Average Progress.
- **Overdue Highlighting** – Overdue rows in the task list are automatically highlighted in red.
- **CSV Export** – Download the generated schedule as a CSV file with one click.
- **Horizontal Navigation** – Clean, modern top navigation bar to switch between views.

---

## 🛠️ Tech Stack

| Library | Purpose |
|---|---|
| `pandas` | Data management, task storage, and manipulation |
| `numpy` | Heuristic scoring calculations in the scheduler |
| `streamlit` | Interactive web application framework |
| `plotly` | Interactive Gantt chart and Priority Distribution chart |
| `streamlit-calendar` | FullCalendar integration for Calendar View |
| `matplotlib` | (Legacy) Static chart support |

---

## 📁 Project Structure

```
project_1/
├── app.py              # Main Streamlit application & UI
├── task_manager.py     # Task data model, CRUD, and CSV persistence
├── scheduler.py        # Scheduling algorithm with business hours & dependencies
├── visualization.py    # Plotly chart generators
├── main.py             # (Legacy) CLI entry point
├── requirements.txt    # Python dependencies
└── tasks.csv           # Auto-generated task data file (git-ignored)
```

---

## ⚙️ Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/mohib080/task-manager-python.git
   cd task-manager-python
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the application:
   ```bash
   streamlit run app.py
   ```

4. Open your browser and navigate to **[http://localhost:8501](http://localhost:8501)**

> ⚠️ **Note:** Do NOT run the app with `python app.py`. Streamlit applications must be started using the `streamlit run` command.

---

## 📸 Screenshots

_Coming soon._

---

## 📄 License

This project is open source and available under the [MIT License](LICENSE).
