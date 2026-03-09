import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os

class TaskManager:
    def __init__(self, filename='tasks.csv'):
        self.filename = filename
        self.columns = ['id', 'name', 'duration_hours', 'priority', 'deadline', 'status', 'recurring', 'depends_on', 'progress']
        self.load_tasks()

    def load_tasks(self):
        if os.path.exists(self.filename):
            self.df = pd.read_csv(self.filename, parse_dates=['deadline'])
            
            # Backward compatibility for old CSVs missing new columns
            needs_save = False
            if 'status' not in self.df.columns:
                self.df['status'] = 'Pending'
                needs_save = True
            if 'recurring' not in self.df.columns:
                self.df['recurring'] = 'None'
                needs_save = True
            if 'depends_on' not in self.df.columns:
                self.df['depends_on'] = None
                needs_save = True
            if 'progress' not in self.df.columns:
                self.df['progress'] = 0
                needs_save = True
                
            if needs_save:
                self.save_tasks()
        else:
            self.df = pd.DataFrame(columns=self.columns)
            
    def save_tasks(self):
        self.df.to_csv(self.filename, index=False)
        
    def add_task(self, name, duration_hours, priority, deadline_str, recurring='None', depends_on=None):
        # Priority: 1 (High) to 5 (Low)
        new_id = int(self.df['id'].max() + 1) if not self.df.empty else 1
        deadline = pd.to_datetime(deadline_str)
        
        new_task = pd.DataFrame([{
            'id': new_id,
            'name': name,
            'duration_hours': duration_hours,
            'priority': priority,
            'deadline': deadline,
            'status': 'Pending',
            'recurring': recurring,
            'depends_on': depends_on,
            'progress': 0
        }])
        
        self.df = pd.concat([self.df, new_task], ignore_index=True)
        self.save_tasks()
        print(f"Task '{name}' added successfully!")
        
    def remove_task(self, task_id):
        if task_id in self.df['id'].values:
            self.df = self.df[self.df['id'] != task_id]
            self.save_tasks()
            print(f"Task {task_id} removed.")
        else:
            print("Task not found.")
            
    def update_tasks(self, edited_df):
        """Replates the current tasks dataframe with a newly edited one (e.g., from Streamlit data editor)"""
        # Ensure correct types before saving
        edited_df['id'] = edited_df['id'].astype(int)
        edited_df['deadline'] = pd.to_datetime(edited_df['deadline'])
        
        # Check for newly completed recurring tasks to spawn
        if not self.df.empty and not edited_df.empty:
            for idx, row in edited_df.iterrows():
                if row['status'] == 'Completed' and row['recurring'] != 'None':
                    # Find old status to ensure we only trigger on the transistion to Completed
                    old_row_matches = self.df[self.df['id'] == row['id']]
                    if not old_row_matches.empty and old_row_matches.iloc[0]['status'] != 'Completed':
                        # It just completed! Spawn the next one
                        new_id = int(edited_df['id'].max() + 1)
                        
                        # Calculate next deadline based on recurrence interval
                        old_dl = row['deadline']
                        if row['recurring'] == 'Daily':
                            next_dl = old_dl + timedelta(days=1)
                        elif row['recurring'] == 'Weekly':
                            next_dl = old_dl + timedelta(weeks=1)
                        elif row['recurring'] == 'Monthly':
                            # Rough month approximation
                            next_dl = old_dl + timedelta(days=30)
                            
                        spawned_task = pd.DataFrame([{
                            'id': new_id,
                            'name': row['name'],
                            'duration_hours': row['duration_hours'],
                            'priority': row['priority'],
                            'deadline': next_dl,
                            'status': 'Pending',
                            'recurring': row['recurring'],
                            'depends_on': row['depends_on'],
                            'progress': 0
                        }])
                        edited_df = pd.concat([edited_df, spawned_task], ignore_index=True)
                        
        self.df = edited_df
        self.save_tasks()

    def get_tasks(self):
        return self.df

