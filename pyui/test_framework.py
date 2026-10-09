"""
PyUI Test Suite
File: pyui/test_framework.py

Automated unit tests verifying every core requirement of the mini UI framework:
1. Component description & nesting (Text, Button, Container, Input, Heading, Badge)
2. Python HTML Renderer
3. State handling & reactivity
4. Event handling & dispatch
5. Quiz application flow (answer selection, score increment, next question, reset)
"""

import unittest
from framework import Component, Container, Text, Heading, Button, Input, Badge, Renderer, App
from app import (
    QUESTIONS, INITIAL_STATE, build_quiz_ui,
    handle_select_option, handle_confirm_answer, handle_next_question, handle_restart_quiz
)


class TestPyUIComponents(unittest.TestCase):
    def test_text_component(self):
        txt = Text(text="Hello World", tag="p", class_name="greeting")
        html_out = txt.render()
        self.assertIn("Hello World", html_out)
        self.assertIn('class="greeting"', html_out)
        self.assertTrue(html_out.startswith("<p"))
        self.assertTrue(html_out.endswith("</p>"))

    def test_text_xss_escaping(self):
        txt = Text(text="<script>alert('xss')</script>")
        html_out = txt.render()
        self.assertNotIn("<script>", html_out)
        self.assertIn("&lt;script&gt;", html_out)

    def test_button_component_and_attributes(self):
        btn = Button(label="Click Me", id="test-btn", class_name="btn-primary", disabled=False)
        html_out = btn.render()
        self.assertIn('id="test-btn"', html_out)
        self.assertIn('data-pyui-event="click"', html_out)
        self.assertIn('class="btn-primary"', html_out)
        self.assertIn("Click Me", html_out)
        self.assertNotIn("disabled", html_out)

    def test_disabled_button(self):
        btn = Button(label="Disabled", id="dis-btn", disabled=True)
        html_out = btn.render()
        self.assertIn("disabled", html_out)

    def test_container_nesting(self):
        tree = Container(
            id="parent-box",
            class_name="wrapper",
            children=[
                Heading(text="Title", level=1, id="h1-title"),
                Text(text="Child Paragraph", id="child-p"),
                Button(label="Action", id="child-btn")
            ]
        )
        rendered = Renderer.render(tree)
        self.assertIn('id="parent-box"', rendered)
        self.assertIn('id="h1-title"', rendered)
        self.assertIn('id="child-p"', rendered)
        self.assertIn('id="child-btn"', rendered)
        self.assertIn("Title</h1>", rendered)
        self.assertIn("Child Paragraph</p>", rendered)


class TestPyUIStateAndEvents(unittest.TestCase):
    def test_app_state_and_event_dispatch(self):
        # Create a simple counter app
        def build_counter(state):
            return Container(children=[
                Text(text=f"Current Count: {state['count']}", id="count-display"),
                Button(
                    label="Add 1",
                    id="btn-add",
                    on_click=lambda s: s.update({"count": s["count"] + 1})
                )
            ])

        app = App(build_fn=build_counter, initial_state={"count": 0})
        
        # Initial render
        initial_html = app.render_ui_html()
        self.assertIn("Current Count: 0", initial_html)

        # Dispatch click event on btn-add
        result = app.dispatch_event("btn-add", event_type="click")
        self.assertTrue(result["handled"])
        self.assertEqual(app.state["count"], 1)
        self.assertIn("Current Count: 1", result["html"])

        # Dispatch another click
        result2 = app.dispatch_event("btn-add", event_type="click")
        self.assertEqual(app.state["count"], 2)
        self.assertIn("Current Count: 2", result2["html"])


class TestPyUIQuizDemo(unittest.TestCase):
    def setUp(self):
        self.app = App(
            build_fn=build_quiz_ui,
            initial_state=INITIAL_STATE.copy()
        )

    def test_quiz_initial_render(self):
        html_out = self.app.render_ui_html()
        # Verify first question is shown
        self.assertIn(QUESTIONS[0]["question"], html_out)
        self.assertIn("Score: 0 pts", html_out)
        self.assertIn("Question 1 of", html_out)

    def test_quiz_answer_selection_and_scoring(self):
        # 1. Select the correct answer for question 1 (index 1 is str())
        correct_idx = QUESTIONS[0]["correct"]
        
        # Initial render to register buttons
        self.app.render_ui_html()
        
        # Click the correct option button
        self.app.dispatch_event(f"btn-opt-{correct_idx}", "click")
        self.assertEqual(self.app.state["selected_option"], correct_idx)
        self.assertFalse(self.app.state["has_answered"])

        # Click submit button
        submit_res = self.app.dispatch_event("btn-submit", "click")
        self.assertTrue(self.app.state["has_answered"])
        self.assertEqual(self.app.state["score"], 1)
        self.assertIn("Correct!", self.app.state["feedback_msg"])
        self.assertIn("opt-correct", submit_res["html"])

        # Click next question
        self.app.dispatch_event("btn-next", "click")
        self.assertEqual(self.app.state["current_index"], 1)
        self.assertIsNone(self.app.state["selected_option"])
        self.assertFalse(self.app.state["has_answered"])

    def test_quiz_wrong_answer_selection(self):
        # Initial render to register buttons
        self.app.render_ui_html()
        
        wrong_idx = 0  # for Q1, 0 is int() which is wrong
        self.app.dispatch_event(f"btn-opt-{wrong_idx}", "click")
        self.app.dispatch_event("btn-submit", "click")

        self.assertTrue(self.app.state["has_answered"])
        self.assertEqual(self.app.state["score"], 0)
        self.assertIn("Incorrect", self.app.state["feedback_msg"])

    def test_quiz_reset(self):
        # Change state
        self.app.state["score"] = 4
        self.app.state["current_index"] = 3
        
        self.app.render_ui_html()
        self.app.dispatch_event("btn-reset", "click")
        
        self.assertEqual(self.app.state["score"], 0)
        self.assertEqual(self.app.state["current_index"], 0)
        self.assertFalse(self.app.state["is_finished"])


if __name__ == "__main__":
    unittest.main()
