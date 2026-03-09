import pandas as pd
import numpy as np
from datetime import datetime, timedelta, time

def create_schedule(df, start_time=None):
    if df.empty:
        return pd.DataFrame()
        
    if start_time is None:
        start_time = datetime.now()
        
    # We want to schedule tasks based on deadline and priority.
    # Simple heuristic: score tasks based on time until deadline and priority.
    # Lower score gets scheduled first.
    
    current_time = pd.Timestamp(start_time)
    df = df.copy()
    
    # Do not schedule completed tasks
    if 'status' in df.columns:
        df = df[df['status'] != 'Completed'].copy()
        
    if df.empty:
        return pd.DataFrame()
    
    # Vectorized operations with Pandas and Numpy
    time_to_deadline = (df['deadline'] - current_time).dt.total_seconds() / 3600.0
    
    # Score = Priority * Weight_Priority + Time_to_deadline * Weight_Deadline
    # priority 1 is highest priority, 5 is lowest
    priority_norm = df['priority'] / df['priority'].max()
    
    # avoid negative and zero division issues
    max_time = max(time_to_deadline.max(), 1)
    deadline_norm = np.where(time_to_deadline > 0, time_to_deadline / max_time, 0)
    
    # Weights for heuristic
    df['score'] = priority_norm * 0.6 + deadline_norm * 0.4
    
    # Dependency resolution sorting
    # We must ensure that a task doesn't appear in the schedule BEFORE its dependency.
    # While exact topological sort is complex with the scoring, we can do a simple 
    # multi-pass scheduling where we only consider tasks whose dependencies are met or not present.
    
    start_times = []
    end_times = []
    scheduled_task_ids = set()
    scheduled_task_ends = {} # Map ID -> end time
    
    current_dt = current_time
    # Align start time to working hours (9 AM - 5 PM, Mon-Fri)
    def align_to_working_hours(dt):
        # Skip weekends
        while dt.weekday() >= 5: # 5: Sat, 6: Sun
            dt = dt + timedelta(days=1)
            dt = dt.replace(hour=9, minute=0, second=0, microsecond=0)
            
        # Before 9 AM -> jump to 9 AM
        if dt.time() < time(9, 0):
            dt = dt.replace(hour=9, minute=0, second=0, microsecond=0)
        # After 5 PM -> jump to 9 AM next day
        elif dt.time() >= time(17, 0):
            dt = dt + timedelta(days=1)
            dt = dt.replace(hour=9, minute=0, second=0, microsecond=0)
            # Re-check weekend
            if dt.weekday() >= 5:
                dt = align_to_working_hours(dt)
        return dt
        
    current_dt = align_to_working_hours(current_dt)
    
    # We will build the schedule incrementally
    final_schedule_rows = []
    
    unscheduled = df.copy()
    
    while not unscheduled.empty:
        # Find candidates: tasks whose dependency is either None, or already scheduled
        candidates_mask = unscheduled.apply(
            lambda r: pd.isna(r.get('depends_on')) or r.get('depends_on') in scheduled_task_ids, 
            axis=1
        )
        candidates = unscheduled[candidates_mask]
        
        if candidates.empty:
            # We have a cyclic dependency or a missing dependency!
            # Just force the highest scoring remaining task to break deadlock
            candidates = unscheduled.iloc[[0]]
            
        # Take the top candidate
        task = candidates.iloc[0]
        
        # If it depends on something, current_dt must be >= the end time of the dependency
        dep_id = task.get('depends_on')
        if not pd.isna(dep_id) and dep_id in scheduled_task_ends:
            dep_end = scheduled_task_ends[dep_id]
            if current_dt < dep_end:
                current_dt = align_to_working_hours(dep_end)
                
        # Schedule the task, breaking it up if it exceeds 5 PM
        duration_left = task['duration_hours']
        
        task_start = current_dt
        task_end = current_dt
        
        while duration_left > 0:
            current_dt = align_to_working_hours(current_dt)
            # Find time until 5 PM
            end_of_day = current_dt.replace(hour=17, minute=0, second=0, microsecond=0)
            hours_until_cod = (end_of_day - current_dt).total_seconds() / 3600.0
            
            if duration_left <= hours_until_cod:
                # Can finish today
                task_end = current_dt + timedelta(hours=duration_left)
                current_dt = task_end
                duration_left = 0
            else:
                # Will spill over
                current_dt = end_of_day
                duration_left -= hours_until_cod
                current_dt = align_to_working_hours(current_dt)
                task_end = current_dt
                
        # Record it
        scheduled_task_ids.add(task['id'])
        scheduled_task_ends[task['id']] = task_end
        
        task_dict = task.to_dict()
        task_dict['scheduled_start'] = task_start
        task_dict['scheduled_end'] = task_end
        final_schedule_rows.append(task_dict)
        
        # Remove from unscheduled
        unscheduled = unscheduled[unscheduled['id'] != task['id']]
    
    return pd.DataFrame(final_schedule_rows)
