import streamlit as st
from streamlit_calendar import calendar

st.write("Before Calendar")

events = [
    {
        "title": "Test Event",
        "start": "2026-03-09T10:00:00",
        "end": "2026-03-09T12:00:00"
    }
]

calendar_options = {
    "headerToolbar": {
        "left": "today prev,next",
        "center": "title",
        "right": "dayGridMonth,timeGridWeek,timeGridDay",
    },
    "initialView": "timeGridWeek",
}

cal = calendar(events=events, options=calendar_options, key="test_cal")
st.write("After Calendar", cal)
