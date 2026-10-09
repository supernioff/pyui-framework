"""
PyUI — Demo Quiz Application Built Entirely in Python
File: pyui/app.py

This application demonstrates that:
1. The UI is completely constructed with Python components (Container, Heading, Text, Button, Badge).
2. All application state is stored and manipulated in Python.
3. Every button click invokes a Python callback function that modifies state and triggers a re-render.
4. No React, Vue, or frontend UI frameworks are involved.
"""

import os
from framework import App, Container, Heading, Text, Button, Badge, run_server

# ==============================================================================
# 1. QUIZ DATA
# ==============================================================================

QUESTIONS = [
    {
        "id": 1,
        "question": "Which Python function converts an object into its string representation?",
        "options": ["int()", "str()", "len()", "type()"],
        "correct": 1,
        "explanation": "str() converts objects into readable string format."
    },
    {
        "id": 2,
        "question": "What is the primary role of a UI Renderer in our PyUI framework?",
        "options": [
            "To connect to a SQL database",
            "To translate the Python component tree into HTML",
            "To write JavaScript code automatically",
            "To compile Python into C++ binaries"
        ],
        "correct": 1,
        "explanation": "The PyUI Renderer walks the component tree and emits HTML strings."
    },
    {
        "id": 3,
        "question": "In PyUI, where does application state (like score and current question) live?",
        "options": [
            "In Python memory (server-side)",
            "Inside the browser's React state",
            "Inside a MySQL database",
            "Inside browser cookies only"
        ],
        "correct": 0,
        "explanation": "State is managed in Python as a simple dictionary that survives across user interactions."
    },
    {
        "id": 4,
        "question": "How does PyUI respond when a user clicks a button?",
        "options": [
            "Browser reloads the entire website from scratch",
            "A tiny event is sent to Python -> Python callback runs -> Python re-renders tree -> DOM updates",
            "React Virtual DOM diffs the components",
            "Nothing happens until server restarts"
        ],
        "correct": 1,
        "explanation": "Minimal JS forwards the click event to Python, which updates state and re-renders."
    },
    {
        "id": 5,
        "question": "What data structure in Python naturally represents a nested component tree?",
        "options": [
            "Objects containing a 'children' list of other objects",
            "A single flat integer",
            "A tuple of floats",
            "A FIFO queue of numbers"
        ],
        "correct": 0,
        "explanation": "A tree is formed when Container components hold child Component objects in a list."
    }
]

# ==============================================================================
# 2. INITIAL STATE
# ==============================================================================

INITIAL_STATE = {
    "current_index": 0,
    "selected_option": None,
    "score": 0,
    "has_answered": False,
    "is_finished": False,
    "feedback_msg": ""
}

# ==============================================================================
# 3. EVENT HANDLERS (PYTHON LOGIC)
# ==============================================================================

def handle_select_option(state, option_index):
    """
    Python event handler triggered when user clicks an answer choice.
    """
    if not state["has_answered"]:
        state["selected_option"] = option_index


def handle_confirm_answer(state):
    """
    Python event handler triggered when user submits their chosen answer.
    """
    if state["selected_option"] is None or state["has_answered"]:
        return

    curr_q = QUESTIONS[state["current_index"]]
    selected = state["selected_option"]
    correct = curr_q["correct"]

    state["has_answered"] = True
    if selected == correct:
        state["score"] += 1
        state["feedback_msg"] = f"✅ Correct! {curr_q['explanation']}"
    else:
        correct_text = curr_q["options"][correct]
        state["feedback_msg"] = f"❌ Incorrect. The right answer was: \"{correct_text}\". {curr_q['explanation']}"


def handle_next_question(state):
    """
    Python event handler to advance to the next question or final score screen.
    """
    if not state["has_answered"]:
        return

    next_idx = state["current_index"] + 1
    if next_idx < len(QUESTIONS):
        state["current_index"] = next_idx
        state["selected_option"] = None
        state["has_answered"] = False
        state["feedback_msg"] = ""
    else:
        state["is_finished"] = True


def handle_restart_quiz(state):
    """
    Python event handler to restart the quiz.
    """
    state["current_index"] = 0
    state["selected_option"] = None
    state["score"] = 0
    state["has_answered"] = False
    state["is_finished"] = False
    state["feedback_msg"] = ""


# ==============================================================================
# 4. COMPONENT TREE BUILDER (PYTHON UI DECLARATION)
# ==============================================================================

def build_quiz_ui(state):
    """
    This function takes the current application state and returns a complete
    Python Component Tree.
    
    Notice how clean and readable this is for a beginner:
    Everything is a Python object: Container, Heading, Text, Button, Badge!
    """
    total_q = len(QUESTIONS)
    curr_idx = state["current_index"]
    score = state["score"]
    
    # -------------------------------------------------------------
    # CASE A: FINAL SCORE SCREEN
    # -------------------------------------------------------------
    if state["is_finished"]:
        pct = round((score / total_q) * 100)
        grade = "Outstanding! 🌟" if pct >= 80 else ("Good effort! 👍" if pct >= 50 else "Keep practicing! 📚")
        
        return Container(
            class_name="pyui-card finish-card",
            children=[
                Badge(text="Quiz Complete", variant="success", class_name="mb-3"),
                Heading(text="Final Score", level=2, class_name="card-title"),
                Text(
                    text=f"You scored {score} out of {total_q} ({pct}%)",
                    class_name="score-big"
                ),
                Text(text=grade, class_name="grade-text"),
                Text(
                    text="This entire interface, scoring system, and state engine was rendered by PyUI in pure Python.",
                    class_name="summary-note"
                ),
                Container(
                    class_name="action-row mt-4",
                    children=[
                        Button(
                            label="🔄 Restart Quiz",
                            id="btn-restart",
                            class_name="btn btn-primary",
                            on_click=handle_restart_quiz
                        )
                    ]
                )
            ]
        )

    # -------------------------------------------------------------
    # CASE B: ACTIVE QUESTION SCREEN
    # -------------------------------------------------------------
    question_data = QUESTIONS[curr_idx]
    selected_opt = state["selected_option"]
    has_answered = state["has_answered"]
    
    # Generate buttons for each multiple-choice option
    option_buttons = []
    for idx, opt_text in enumerate(question_data["options"]):
        # Determine styling based on selection and answer submission
        btn_class = "btn-option"
        
        if has_answered:
            if idx == question_data["correct"]:
                btn_class += " opt-correct"
            elif idx == selected_opt:
                btn_class += " opt-wrong"
            else:
                btn_class += " opt-disabled"
        else:
            if idx == selected_opt:
                btn_class += " opt-selected"

        # Create a closure callback for this option index
        def make_select_callback(option_idx):
            return lambda s: handle_select_option(s, option_idx)

        option_buttons.append(
            Button(
                label=f"{chr(65 + idx)}.  {opt_text}",
                id=f"btn-opt-{idx}",
                class_name=btn_class,
                disabled=has_answered,
                on_click=make_select_callback(idx)
            )
        )

    # Bottom action buttons (Check Answer vs Next Question)
    action_buttons = []
    if not has_answered:
        action_buttons.append(
            Button(
                label="Submit Answer",
                id="btn-submit",
                class_name="btn btn-primary",
                disabled=(selected_opt is None),
                on_click=handle_confirm_answer
            )
        )
    else:
        next_label = "Finish Quiz 🏁" if (curr_idx + 1 == total_q) else "Next Question ➡️"
        action_buttons.append(
            Button(
                label=next_label,
                id="btn-next",
                class_name="btn btn-primary",
                on_click=handle_next_question
            )
        )

    action_buttons.append(
        Button(
            label="Reset",
            id="btn-reset",
            class_name="btn btn-secondary",
            on_click=handle_restart_quiz
        )
    )

    # Feedback container if answered
    feedback_children = []
    if state["feedback_msg"]:
        feedback_class = "feedback-box success" if "Correct" in state["feedback_msg"] else "feedback-box error"
        feedback_children.append(
            Text(text=state["feedback_msg"], class_name=feedback_class)
        )

    # Assemble the full question card tree
    return Container(
        class_name="pyui-card",
        children=[
            # Top Status Bar: Question Progress + Score Counter
            Container(
                class_name="card-header-bar",
                children=[
                    Badge(text=f"Question {curr_idx + 1} of {total_q}", variant="info"),
                    Badge(text=f"Score: {score} pts", variant="accent")
                ]
            ),
            
            # Question Text
            Heading(text=question_data["question"], level=3, class_name="question-text"),
            
            # Options Group
            Container(
                class_name="options-container",
                children=option_buttons
            ),

            # Feedback message (if any)
            Container(
                class_name="feedback-wrapper",
                children=feedback_children
            ),

            # Action Buttons Row
            Container(
                class_name="action-row",
                children=action_buttons
            )
        ]
    )


# ==============================================================================
# 5. APPLICATION INSTANCE
# ==============================================================================

app = App(
    build_fn=build_quiz_ui,
    initial_state=INITIAL_STATE,
    title="PyUI — Interactive Quiz App"
)

if __name__ == "__main__":
    static_folder = os.path.join(os.path.dirname(__file__), "static")
    run_server(app, host="0.0.0.0", port=8000, static_dir=static_folder)
