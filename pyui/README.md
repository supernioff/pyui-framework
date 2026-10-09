# PyUI — A Mini UI Framework Built in Python

> **College Technical Assignment Project**  
> **Student Level:** First-Year Computer Science / Software Engineering  
> **Core Concept:** Building a declarative UI framework from scratch in Python without React, Vue, or third-party web frameworks.

---

## 1. Project Overview

**PyUI** is an educational, lightweight UI framework implemented entirely in Python. It allows developers to declare user interfaces using Python objects, handles application state updates, listens to user events, and renders the component tree into standard HTML.

Unlike ordinary websites where JavaScript or React owns the component hierarchy and state, **in PyUI every component, property, event handler, and state mutation lives in Python.**

---

## 2. Project Folder Structure

```text
pyui-framework/
│
├── framework.py           # Core Framework: Components, Renderer, State, Event Dispatcher & HTTP Server
├── app.py                 # Quiz Demo Application built using PyUI components
├── counter_app.py         # Minimal Counter Demo proving framework reusability
├── test_framework.py      # Automated Python unit test suite (10 unit tests)
├── requirements.txt       # Dependencies (uses Python Standard Library, 0 external packages needed)
├── README.md              # Documentation, architecture, viva prep & setup guide
│
└── static/
    ├── style.css          # Clean CSS styling for components, cards, and buttons
    └── client.js          # Minimal 30-line bridge that forwards DOM clicks to Python
```

---

## 3. How the Architecture Works

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                           BROWSER (FRONTEND)                                │
│                                                                             │
│   1. User clicks Option B Button                                            │
│   2. client.js intercepts click: { id: "btn-opt-1", event: "click" }       │
│   3. Sends HTTP POST /api/event to Python                                   │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │ HTTP POST
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                           PYTHON FRAMEWORK (BACKEND)                        │
│                                                                             │
│   4. app.dispatch_event("btn-opt-1", "click")                               │
│   5. Python invokes registered callback: handle_select_option(state, 1)     │
│   6. Python state is mutated: state["selected_option"] = 1                 │
│   7. Python re-runs build_fn(state) -> new Component Tree                   │
│   8. Renderer.render(tree) generates new HTML string                        │
│   9. Server returns JSON response: { html: "<div ...", state: {...} }       │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │ HTTP 200 JSON
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                           BROWSER (FRONTEND)                                │
│                                                                             │
│   10. client.js replaces innerHTML of #pyui-app-mount                       │
│   11. User sees option B highlighted with instant visual feedback!          │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Why is `client.js` needed?
Web browsers can only execute JavaScript inside the client browser engine. Because our component tree and state live in Python, `client.js` acts strictly as an event forwarding bridge. It contains **zero UI logic, zero state management, and zero templates**.

---

## 4. Key Framework Components

| Component | Description | Example Python Usage |
|-----------|-------------|----------------------|
| `Container` | Layout wrapper (renders `<div>` or semantic tags) | `Container(children=[...], class_name="card")` |
| `Heading` | Titles `<h1>` through `<h6>` | `Heading(text="Welcome", level=1)` |
| `Text` | Paragraphs and text nodes with auto XSS escaping | `Text(text="Score: 5", class_name="score")` |
| `Button` | Interactive button triggering a Python callback | `Button(label="Next", on_click=handle_next)` |
| `Badge` | Colored pill indicator | `Badge(text="Question 1 of 5", variant="info")` |
| `Input` | Text input capturing changes | `Input(placeholder="Your name", on_change=...)` |

---

## 5. Quick Start & Installation

### Prerequisites
- Python 3.8 or higher installed on your computer.
- No external packages needed! PyUI runs on Python's built-in standard library (`http.server`, `json`, `html`, `urllib`).

### Step-by-Step Commands

1. **Clone or navigate into project directory:**
   ```bash
   cd pyui
   ```

2. **Run the Automated Unit Tests:**
   ```bash
   python3 test_framework.py
   ```
   *Expected output:*
   ```text
   Ran 10 tests in 0.005s
   OK
   ```

3. **Start the Quiz Application:**
   ```bash
   python3 app.py
   ```
   *Expected output:*
   ```text
   🚀 PyUI Server is running at http://0.0.0.0:8000
   Open your browser to see your Python-built UI live!
   ```

4. **Open in your browser:**
   Open [http://localhost:8000](http://localhost:8000)

5. *(Optional)* **Run the Counter Demo:**
   ```bash
   python3 counter_app.py
   ```
   Open [http://localhost:8001](http://localhost:8001)

---

## 6. Verification & Test Checklist

Use this checklist during your evaluation to prove every requirement was met:

- [x] **Requirement A — Components in Python:**
  - Implemented `Text`, `Button`, `Container`, `Input`, `Heading`, `Badge` in `framework.py`.
  - Properties like `id`, `class_name`, `style`, `disabled`, and callbacks are supported.
  - Components support arbitrary nesting (`Container(children=[...])`).
- [x] **Requirement B — Python HTML Renderer:**
  - Implemented `Renderer.render(component_tree)`.
  - All rendering logic executes in Python.
  - HTML entities are safely escaped against XSS injection.
- [x] **Requirement C — State Handling:**
  - Managed by Python `App` instance via `state` dictionary.
  - State survives across interactions and drives the component tree.
- [x] **Requirement D — Event Handling:**
  - Buttons register Python callbacks (`on_click`).
  - Clicks trigger `app.dispatch_event()`, mutating state and triggering UI re-render.
- [x] **Requirement E — Quiz Application:**
  - Multiple-choice questions with answer selection.
  - Live score counter.
  - Submit & Next question buttons.
  - Final score report with percentages and restart button.
- [x] **Requirement F — Beginner-Friendly & Honest:**
  - Uses standard library, zero complex metaprogramming, documented functions.

---

## 7. Honest Technical Limitations

As an honest academic project, PyUI clearly acknowledges its educational design choices:

1. **Full-Tree Re-rendering (No Virtual DOM Diffing):**
   When state changes, PyUI re-renders the component tree into an HTML string and swaps the mount point. In contrast, production frameworks like React or Flutter use complex diffing algorithms to patch only specific DOM nodes.
2. **Server-Side Roundtrip:**
   Every event makes an HTTP POST request to Python. This works well locally and over low-latency networks, but production web frameworks compile down to WebAssembly or native JS for zero-latency client execution.
3. **Single Process In-Memory State:**
   State is stored in Python memory for the running process. In a multi-user cloud deployment, session cookies or Redis would be needed to isolate sessions per user.

---

## 8. GitHub Upload Instructions

Run these exact commands in your terminal to publish your repository:

```bash
# 1. Initialize git in the project root
git init

# 2. Add all files
git add .

# 3. Create initial commit
git commit -m "feat: complete PyUI mini Python UI framework with quiz demo"

# 4. Rename main branch
git branch -M main

# 5. Link to your GitHub repo (replace with your username/reponame)
git remote add origin https://github.com/<YOUR_USERNAME>/pyui-framework.git

# 6. Push code to GitHub
git push -u origin main
```

---

## 9. Demo Video Script (2-3 Minutes)

Here is a ready-to-read script for your demo video or presentation:

- **0:00 - 0:30 (Introduction):**  
  *"Hello, I'm presenting PyUI, a mini UI framework built in pure Python. The goal of this assignment is to prove that UI frameworks are not magic—they are just component trees, state stores, renderers, and event dispatchers. In PyUI, all of this logic is written in Python without React or Vue."*

- **0:30 - 1:15 (Architecture & Code Tour):**  
  *"In `framework.py`, we defined base `Component` and classes like `Container`, `Button`, and `Text`. Each component knows how to render itself into HTML. In `app.py`, our `build_quiz_ui` function takes the current Python state and returns a tree of components. Notice there is no HTML or JSX here—it's 100% Python."*

- **1:15 - 2:00 (Live Quiz Demonstration):**  
  *"Now let's open `http://localhost:8000`. Here is our Quiz. When I click option B, the minimal client bridge forwards the click ID to `/api/event`. Python calls `handle_select_option`, updates `state['selected_option']`, re-renders the tree, and updates the screen. When I submit, Python checks the answer, increments the score, and renders the next question. At the end, we get our final score and a restart button."*

- **2:00 - 2:30 (Tests & Conclusion):**  
  *"Finally, running `python3 test_framework.py` passes all 10 unit tests for component rendering, XSS escaping, event dispatching, and quiz state transitions. Thank you!"*
