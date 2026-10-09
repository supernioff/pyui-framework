"""
PyUI — Minimal Counter Demo
File: pyui/counter_app.py

An ultra-compact demonstration of:
- State increment / decrement
- Direct button event dispatching
- Dynamic re-rendering of state in the UI
"""

import os
from framework import App, Container, Heading, Text, Button, run_server

# 1. State
INITIAL_STATE = {"count": 0}

# 2. Event Handlers
def increment(state):
    state["count"] += 1

def decrement(state):
    state["count"] -= 1

def reset(state):
    state["count"] = 0

# 3. Component Tree Builder
def build_counter_ui(state):
    count_val = state["count"]
    color = "#10b981" if count_val > 0 else ("#ef4444" if count_val < 0 else "#64748b")

    return Container(
        class_name="pyui-card text-center",
        children=[
            Heading(text="PyUI Counter Example", level=2),
            Text(
                text=f"{count_val}",
                class_name="counter-display",
                style=f"color: {color}; font-size: 3.5rem; font-weight: bold; margin: 1.5rem 0;"
            ),
            Container(
                class_name="action-row justify-center",
                children=[
                    Button(label="➖ Decrement", id="btn-dec", class_name="btn btn-secondary", on_click=decrement),
                    Button(label="🔄 Reset", id="btn-reset", class_name="btn btn-ghost", on_click=reset),
                    Button(label="➕ Increment", id="btn-inc", class_name="btn btn-primary", on_click=increment),
                ]
            )
        ]
    )

# 4. App Instance
app = App(build_fn=build_counter_ui, initial_state=INITIAL_STATE, title="PyUI — Counter Demo")

if __name__ == "__main__":
    static_folder = os.path.join(os.path.dirname(__file__), "static")
    run_server(app, host="0.0.0.0", port=8001, static_dir=static_folder)
