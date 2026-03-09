import streamlit as st
import pandas as pd
from datetime import datetime, time, timedelta
from task_manager import TaskManager
from scheduler import create_schedule
from visualization import plot_gantt_chart, plot_priority_distribution
from streamlit_calendar import calendar

# Configure the Streamlit page
st.set_page_config(page_title="Task Manager & Scheduler", page_icon="📝", layout="wide")

# Initialize Task Manager (cached to avoid reloading on every interaction)
@st.cache_resource
def get_task_manager():
    return TaskManager('tasks.csv')

tm = get_task_manager()

st.title("📝 Task Manager & Scheduler")
st.markdown("Manage your tasks and generate optimal schedules based on priority and deadlines.")

# Metrics Row
tasks = tm.get_tasks()
total_tasks = len(tasks)
if total_tasks > 0 and 'status' in tasks.columns:
    completed_tasks = len(tasks[tasks['status'] == 'Completed'])
    pending_tasks = total_tasks - completed_tasks
    
    # Check for overdue
    now = pd.Timestamp.now()
    overdue_tasks = len(tasks[(pd.to_datetime(tasks['deadline']) < now) & (tasks['status'] != 'Completed')])
    
    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric("Total Tasks", total_tasks)
    m2.metric("Completed", completed_tasks)
    m3.metric("Pending/In Progress", pending_tasks)
    m4.metric("⚠️ Overdue", overdue_tasks, delta_color="inverse")
    
    avg_progress = tasks['progress'].mean() if 'progress' in tasks.columns else 0
    m5.metric("Avg Progress", f"{avg_progress:.0f}%")
else: # Added else block for the info message
    st.info("No tasks available to show metrics.")

# Create a modern navigation menu at the top
st.markdown("---")
page = st.radio(
    "Navigation",
    options=["Task List", "Gantt Chart", "Calendar View", "Analytics"],
    format_func=lambda x: {
        "Task List": "📋 Task List",
        "Gantt Chart": "🕒 Gantt Chart",
        "Calendar View": "📅 Calendar View",
        "Analytics": "📊 Analytics"
    }[x],
    label_visibility="collapsed",
    horizontal=True
)
st.markdown("---")

if page == "Task List":
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("Add New Task")
        with st.form("add_task_form", clear_on_submit=True):
            name = st.text_input("Task Name")
            duration = st.number_input("Duration (hours)", min_value=0.5, value=1.0, step=0.5)
            priority = st.selectbox("Priority (1 = Highest, 5 = Lowest)", options=[1, 2, 3, 4, 5])
            
            # Use columns for date and time
            date_col, time_col = st.columns(2)
            with date_col:
                deadline_date = st.date_input("Deadline Date")
            with time_col:
                deadline_time = st.time_input("Deadline Time", value=time(17, 0)) # Default 5 PM
                
            # Additional features
            adv_col1, adv_col2 = st.columns(2)
            with adv_col1:
                recurring = st.selectbox("Recurrence", options=["None", "Daily", "Weekly", "Monthly"])
                
            with adv_col2:
                # Get current tasks to populate dependency dropdown
                current_tasks = tm.get_tasks()
                if not current_tasks.empty:
                    dep_options = ["None"] + current_tasks['id'].astype(str).tolist()
                    depends_on_str = st.selectbox("Depends On (Task ID)", options=dep_options)
                    depends_on = None if depends_on_str == "None" else int(depends_on_str)
                else:
                    st.selectbox("Depends On", options=["None"], disabled=True)
                    depends_on = None
                
            submitted = st.form_submit_button("Add Task")
            
            if submitted:
                if name:
                    # Combine date and time
                    deadline_dt = datetime.combine(deadline_date, deadline_time)
                    tm.add_task(name, duration, priority, deadline_dt.strftime("%Y-%m-%d %H:%M"), recurring, depends_on)
                    st.success(f"Task '{name}' added successfully!")
                    st.rerun()
                else:
                    st.error("Please enter a task name.")

    with col2:
        st.subheader("Current Tasks")
        tasks = tm.get_tasks()
        
        # Search & Filtering
        with st.expander("🔍 Search & Filter", expanded=False):
            sf_col1, sf_col2, sf_col3 = st.columns(3)
            with sf_col1:
                search_term = st.text_input("Search by Name")
            with sf_col2:
                filter_status = st.multiselect("Filter Status", options=["Pending", "In Progress", "Completed"], default=["Pending", "In Progress", "Completed"])
            with sf_col3:
                filter_priority = st.multiselect("Filter Priority", options=[1,2,3,4,5], default=[1,2,3,4,5])
        
        if not tasks.empty:
            st.markdown("*Edit tasks directly in the table below!*")
            display_df = tasks.copy()
            
            # Apply Filters
            if search_term:
                display_df = display_df[display_df['name'].str.contains(search_term, case=False, na=False)]
            display_df = display_df[display_df['status'].isin(filter_status)]
            display_df = display_df[display_df['priority'].isin(filter_priority)]
            
            # Identify overdue tasks to highlight them (optional visual hint in df not strictly possible natively without styling, but we'll ensure they are clear)
            now = pd.Timestamp.now()
            
            # Configure column types for the data editor
            column_config = {
                "id": st.column_config.NumberColumn("ID", disabled=True),
                "name": st.column_config.TextColumn("Task Name", required=True),
                "duration_hours": st.column_config.NumberColumn("Duration (hrs)", min_value=0.5, step=0.5),
                "priority": st.column_config.SelectboxColumn("Priority", options=[1, 2, 3, 4, 5], required=True),
                "deadline": st.column_config.DatetimeColumn("Deadline", format="YYYY-MM-DD HH:mm", required=True),
                "status": st.column_config.SelectboxColumn("Status", options=["Pending", "In Progress", "Completed"], required=True),
                "recurring": st.column_config.SelectboxColumn("Recurring", options=["None", "Daily", "Weekly", "Monthly"], required=True),
                "depends_on": st.column_config.NumberColumn("Depends On", min_value=1, step=1, disabled=False),
                "progress": st.column_config.ProgressColumn("Progress", min_value=0, max_value=100, format="%d%%")
            }
            
            # Ensure deadline is datetime exactly for editor
            display_df['deadline'] = pd.to_datetime(display_df['deadline'])
            
            # Styling for overdue tasks
            def highlight_overdue(row):
                if pd.notna(row['deadline']) and row['deadline'] < now and row['status'] != 'Completed':
                    return ['background-color: rgba(255, 75, 75, 0.2)'] * len(row)
                return [''] * len(row)

            styled_df = display_df.style.apply(highlight_overdue, axis=1)
            
            edited_df = st.data_editor(styled_df, use_container_width=True, hide_index=True, column_config=column_config, key="task_editor")
            
            # If the user made changes, save them automatically
            if not edited_df.equals(display_df):
                tm.update_tasks(edited_df)
                st.success("Task updates saved!")
                st.rerun()
            
            # Task Removal
            st.markdown("---")
            st.subheader("Remove Task")
            remove_col1, remove_col2 = st.columns([3, 1])
            with remove_col1:
                task_to_remove = st.selectbox("Select task to remove:", 
                                            options=tasks['id'].tolist(),
                                            format_func=lambda x: f"[{x}] {tasks[tasks['id'] == x]['name'].iloc[0]}")
            with remove_col2:
                # Add some vertical spacing to align with the selectbox
                st.write("")
                st.write("")
                if st.button("Remove Selected Task", type="primary"):
                    tm.remove_task(task_to_remove)
                    st.success("Task removed!")
                    st.rerun()
        else:
            st.info("No tasks added yet. Use the form on the left to add your first task!")

elif page == "Gantt Chart":
    st.subheader("Schedule Visualizer")
    tasks = tm.get_tasks()
    
    if not tasks.empty:
        col1, col2 = st.columns([1, 3])
        with col1:
            st.info("""
            **How scheduling works:**
            The algorithm scores tasks based on two factors:
            1. Priority (1 is highest)
            2. Proximity to deadline
            
            Tasks with the lowest score are scheduled first.
            """)
            if st.button("Generate/Refresh Schedule", type="primary"):
                st.rerun()
                
        with col2:
            scheduled_df = create_schedule(tasks)
            if not scheduled_df.empty:
                fig = plot_gantt_chart(scheduled_df)
                if fig:
                    st.plotly_chart(fig, use_container_width=True)
                
                # Add ability to export the schedule
                csv = scheduled_df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="📥 Download Schedule as CSV",
                    data=csv,
                    file_name='task_schedule.csv',
                    mime='text/csv',
                )
                
                with st.expander("Show detailed schedule table"):
                    schedule_display = scheduled_df[['name', 'priority', 'duration_hours', 'scheduled_start', 'scheduled_end']].copy()
                    schedule_display['scheduled_start'] = pd.to_datetime(schedule_display['scheduled_start']).dt.strftime('%Y-%m-%d %H:%M')
                    schedule_display['scheduled_end'] = pd.to_datetime(schedule_display['scheduled_end']).dt.strftime('%Y-%m-%d %H:%M')
                    st.dataframe(schedule_display, use_container_width=True, hide_index=True)
    else:
        st.warning("Add some tasks in the 'Task List' tab first to generate a schedule.")

elif page == "Calendar View":
    st.subheader("Calendar View")
    tasks = tm.get_tasks()
    
    if not tasks.empty:
        # We'll map the raw tasks based on their deadline for a general view,
        # but also try to generate the schedule to show exact blocks.
        col1, col2 = st.columns([1, 3])
        
        with col1:
            st.info("This calendar shows when tasks are mathematically scheduled to occur based on priority and deadlines.")
            
        with col2:
            schedule = create_schedule(tasks)
            events = []
            
            # Map priorities to colors
            color_map = {
                1: "#FF4B4B", # Red
                2: "#FF8C00", # Orange
                3: "#FFCE56", # Yellow
                4: "#36A2EB", # Blue
                5: "#4BC0C0"  # Teal
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
                    
            calendar_options = {
                "headerToolbar": {
                    "left": "today prev,next",
                    "center": "title",
                    "right": "dayGridMonth,timeGridWeek,timeGridDay",
                },
                "initialView": "timeGridWeek",
                "slotMinTime": "06:00:00",
                "slotMaxTime": "22:00:00",
            }
            
            calendar(events=events, options=calendar_options, key="task_calendar")
    else:
        st.warning("Add tasks to view them on the calendar.")

elif page == "Analytics":
    st.subheader("Priority Distribution")
    tasks = tm.get_tasks()
    
    if not tasks.empty:
        fig = plot_priority_distribution(tasks)
        if fig:
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Add some tasks to see analytics.")
