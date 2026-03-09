import plotly.express as px
import plotly.graph_objects as go
import numpy as np

def plot_gantt_chart(scheduled_df):
    if scheduled_df.empty:
        return None
        
    # We want a modern interactive timeline
    fig = px.timeline(
        scheduled_df,
        x_start="scheduled_start",
        x_end="scheduled_end",
        y="name",
        color="priority",
        color_continuous_scale="RdBu", 
        hover_data=["duration_hours", "status"],
        title="Interactive Task Schedule Gantt Chart"
    )
    
    # Invert y-axis and update layout for slickness
    fig.update_yaxes(autorange="reversed")
    fig.update_layout(
        xaxis_title="Timeline",
        yaxis_title="Tasks",
        coloraxis_colorbar=dict(title="Priority (1=High)"),
    )
    
    return fig

def plot_priority_distribution(df):
    if df.empty:
        return None
        
    priority_counts = df['priority'].value_counts().reset_index()
    priority_counts.columns = ['priority', 'count']
    priority_counts['priority'] = priority_counts['priority'].astype(str)
    
    # Mapping colors to make priority 1 stand out
    color_map = {
        '1': '#FF4B4B', # Red
        '2': '#FF8C00', # Orange
        '3': '#FFCE56', # Yellow
        '4': '#36A2EB', # Blue
        '5': '#4BC0C0'  # Teal
    }
    
    fig = px.pie(
        priority_counts, 
        values='count', 
        names='priority',
        title="Task Priority Distribution",
        color='priority',
        color_discrete_map=color_map,
        hole=0.4 # Make it a donut chart for a modern feel
    )
    
    fig.update_traces(textposition='inside', textinfo='percent+label')
    return fig
