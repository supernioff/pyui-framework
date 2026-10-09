"""
PyUI — A Mini UI Framework Built in Pure Python
File: pyui/framework.py

A beginner-friendly UI framework created for learning how UI frameworks work under the hood.
Includes:
- Component Tree (Text, Button, Container, Input, Heading, Badge)
- Python HTML Renderer
- State Management
- Event Registry & Dispatcher
- Built-in Lightweight HTTP Server (Python Standard Library - No external packages needed!)
"""

import json
import html
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse
import os


# ==============================================================================
# 1. BASE COMPONENT
# ==============================================================================

class Component:
    """
    Base class for all PyUI components.
    Every UI element in PyUI inherits from this class.
    """
    _counter = 0

    def __init__(self, id=None, class_name="", style="", children=None):
        # Auto-generate a unique ID if developer did not provide one
        if id:
            self.id = str(id)
        else:
            Component._counter += 1
            self.id = f"pyui-{Component._counter}"

        self.class_name = class_name
        self.style = style
        self.children = children if children is not None else []
        self.on_click = None

    def render(self, context=None):
        """
        Render this component and all its children into HTML string.
        Must be implemented by subclasses.
        """
        raise NotImplementedError("Subclasses of Component must implement render()")

    def _render_children(self, context=None):
        """Helper to render all child components recursively."""
        return "".join(child.render(context) for child in self.children)

    def _style_attr(self):
        """Helper to build HTML style attribute."""
        return f' style="{html.escape(self.style)}"' if self.style else ""

    def _class_attr(self):
        """Helper to build HTML class attribute."""
        return f' class="{html.escape(self.class_name)}"' if self.class_name else ""

    def to_dict(self):
        """
        Convert component tree to a dictionary representation for debugging
        and tree inspection.
        """
        return {
            "type": self.__class__.__name__,
            "id": self.id,
            "class_name": self.class_name,
            "children": [c.to_dict() for c in self.children]
        }


# ==============================================================================
# 2. CORE COMPONENTS
# ==============================================================================

class Container(Component):
    """
    Container component for grouping and layout (renders as <div> or semantic tag).
    Accepts children to form a nested UI tree.
    """
    def __init__(self, children=None, tag="div", id=None, class_name="", style=""):
        super().__init__(id=id, class_name=class_name, style=style, children=children)
        self.tag = tag

    def render(self, context=None):
        inner_html = self._render_children(context)
        return (
            f'<{self.tag} id="{html.escape(self.id)}"'
            f'{self._class_attr()}{self._style_attr()}>'
            f'{inner_html}'
            f'</{self.tag}>'
        )


class Text(Component):
    """
    Text component for displaying readable content.
    Escapes text for security (prevents XSS).
    """
    def __init__(self, text="", tag="p", id=None, class_name="", style=""):
        super().__init__(id=id, class_name=class_name, style=style)
        self.text = str(text)
        self.tag = tag

    def render(self, context=None):
        safe_text = html.escape(self.text)
        return (
            f'<{self.tag} id="{html.escape(self.id)}"'
            f'{self._class_attr()}{self._style_attr()}>'
            f'{safe_text}'
            f'</{self.tag}>'
        )

    def to_dict(self):
        data = super().to_dict()
        data["text"] = self.text
        return data


class Heading(Component):
    """
    Heading component (h1, h2, h3, h4) for titles.
    """
    def __init__(self, text="", level=1, id=None, class_name="", style=""):
        super().__init__(id=id, class_name=class_name, style=style)
        self.text = str(text)
        self.level = max(1, min(6, int(level)))

    def render(self, context=None):
        tag = f"h{self.level}"
        safe_text = html.escape(self.text)
        return (
            f'<{tag} id="{html.escape(self.id)}"'
            f'{self._class_attr()}{self._style_attr()}>'
            f'{safe_text}'
            f'</{tag}>'
        )


class Button(Component):
    """
    Button component for user interactions.
    Accepts an on_click Python function callback.
    """
    def __init__(self, label="", on_click=None, id=None, class_name="", style="", disabled=False):
        super().__init__(id=id, class_name=class_name, style=style)
        self.label = str(label)
        self.on_click = on_click
        self.disabled = disabled

    def render(self, context=None):
        # Register the callback in the App's event dispatcher if context is provided
        if context and self.on_click:
            context.register_event(self.id, "click", self.on_click)

        disabled_attr = " disabled" if self.disabled else ""
        safe_label = html.escape(self.label)
        
        # data-pyui-event tells our minimal frontend JS to capture clicks on this button
        return (
            f'<button id="{html.escape(self.id)}"'
            f' data-pyui-event="click"'
            f'{self._class_attr()}{self._style_attr()}{disabled_attr}>'
            f'{safe_label}'
            f'</button>'
        )

    def to_dict(self):
        data = super().to_dict()
        data["label"] = self.label
        data["has_on_click"] = self.on_click is not None
        data["disabled"] = self.disabled
        return data


class Input(Component):
    """
    Input component for user text entry.
    """
    def __init__(self, placeholder="", value="", input_type="text", on_change=None, id=None, class_name="", style=""):
        super().__init__(id=id, class_name=class_name, style=style)
        self.placeholder = str(placeholder)
        self.value = str(value)
        self.input_type = input_type
        self.on_change = on_change

    def render(self, context=None):
        if context and self.on_change:
            context.register_event(self.id, "change", self.on_change)

        return (
            f'<input id="{html.escape(self.id)}"'
            f' type="{html.escape(self.input_type)}"'
            f' placeholder="{html.escape(self.placeholder)}"'
            f' value="{html.escape(self.value)}"'
            f' data-pyui-event="change"'
            f'{self._class_attr()}{self._style_attr()} />'
        )


class Badge(Component):
    """
    Visual indicator badge.
    """
    def __init__(self, text="", variant="default", id=None, class_name="", style=""):
        super().__init__(id=id, class_name=class_name, style=style)
        self.text = str(text)
        self.variant = variant

    def render(self, context=None):
        safe_text = html.escape(self.text)
        variant_class = f"badge badge-{self.variant}"
        full_class = f"{variant_class} {self.class_name}".strip()
        return (
            f'<span id="{html.escape(self.id)}"'
            f' class="{html.escape(full_class)}"{self._style_attr()}>'
            f'{safe_text}'
            f'</span>'
        )


# ==============================================================================
# 3. RENDERER
# ==============================================================================

class Renderer:
    """
    Renders a PyUI Component Tree into clean HTML.
    All rendering logic lives strictly in Python.
    """
    @staticmethod
    def render(component_tree, app_context=None):
        """
        Traverse the component tree and generate the complete HTML string.
        """
        if component_tree is None:
            return "<!-- Empty PyUI Component -->"
        return component_tree.render(context=app_context)


# ==============================================================================
# 4. APP & STATE MANAGEMENT & EVENT DISPATCHER
# ==============================================================================

class App:
    """
    The core PyUI Application manager.
    Responsible for:
    1. Managing application state (Python dict)
    2. Registering event listeners from Python components
    3. Dispatching incoming events to Python callbacks
    4. Re-rendering the UI tree when state changes
    5. Serving the app over HTTP
    """
    def __init__(self, build_fn, initial_state=None, title="PyUI Application"):
        self.build_fn = build_fn
        self.initial_state = initial_state.copy() if initial_state else {}
        self.state = initial_state.copy() if initial_state else {}
        self.title = title
        
        # Registry: { "button-id:click": python_callback_function }
        self._event_handlers = {}
        
        # Cache current tree
        self.current_tree = None

    def register_event(self, component_id, event_type, callback):
        """Registers a Python callback for a component ID and event type."""
        key = f"{component_id}:{event_type}"
        self._event_handlers[key] = callback

    def build_tree(self):
        """
        Calls the user-provided build function passing current state.
        Returns the root Component.
        """
        # Clear event handlers before rebuild
        self._event_handlers.clear()
        self.current_tree = self.build_fn(self.state)
        return self.current_tree

    def render_ui_html(self):
        """
        Builds the component tree and renders it to inner HTML.
        """
        tree = self.build_tree()
        return Renderer.render(tree, app_context=self)

    def dispatch_event(self, component_id, event_type="click", payload=None):
        """
        Event Dispatcher:
        1. Finds the Python callback registered to this component and event.
        2. Calls the callback, allowing it to modify self.state.
        3. Re-renders the UI tree with the updated state.
        4. Returns the fresh HTML and updated state.
        """
        key = f"{component_id}:{event_type}"
        handler = self._event_handlers.get(key)
        
        handled = False
        if handler:
            # Call the user callback. Pass state and optional payload.
            # Handles callbacks with 1 arg (state) or 2 args (state, payload)
            import inspect
            sig = inspect.signature(handler)
            if len(sig.parameters) >= 2:
                handler(self.state, payload)
            else:
                handler(self.state)
            handled = True

        # Re-render with newly modified state
        new_html = self.render_ui_html()
        return {
            "handled": handled,
            "html": new_html,
            "state": self.state
        }

    def reset_state(self):
        """Reset state back to initial state and re-render."""
        self.state = self.initial_state.copy()
        return self.render_ui_html()

    def get_full_page_html(self):
        """
        Produces the full HTML document containing our rendered component tree,
        external stylesheet link, and the minimal frontend event helper.
        """
        ui_html = self.render_ui_html()
        
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{html.escape(self.title)}</title>
    <link rel="stylesheet" href="/static/style.css">
</head>
<body>
    <div id="pyui-app-mount">
        {ui_html}
    </div>

    <!-- 
      Minimal 25-line Frontend Event Forwarder:
      Captures browser DOM clicks and sends them to the Python backend.
      Does NOT contain UI logic or framework code.
    -->
    <script src="/static/client.js"></script>
</body>
</html>"""


# ==============================================================================
# 5. LIGHTWEIGHT BUILT-IN HTTP SERVER
# ==============================================================================

def create_request_handler(app_instance, static_dir=None):
    """
    Creates an HTTP request handler wired to the PyUI App instance.
    Uses Python's standard library http.server module.
    """
    class PyUIHTTPHandler(BaseHTTPRequestHandler):
        def log_message(self, format, *args):
            # Clean logging
            print(f"[PyUI Server] {self.command} {self.path} - {format % args}")

        def _send_response_data(self, status_code, content_type, data):
            self.send_response(status_code)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(data)))
            # Enable CORS for local testing
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
            self.send_header("Access-Control-Allow-Headers", "Content-Type")
            self.end_headers()
            self.wfile.write(data)

        def do_OPTIONS(self):
            self._send_response_data(204, "text/plain", b"")

        def do_GET(self):
            parsed_path = urllib.parse.urlparse(self.path).path

            # 1. Main Application Page
            if parsed_path == "/":
                full_html = app_instance.get_full_page_html()
                self._send_response_data(200, "text/html; charset=utf-8", full_html.encode("utf-8"))
                return

            # 2. Get Current State & HTML as JSON (for API clients)
            elif parsed_path == "/api/state":
                data = json.dumps({
                    "state": app_instance.state,
                    "html": app_instance.render_ui_html(),
                    "tree": app_instance.current_tree.to_dict() if app_instance.current_tree else None
                }).encode("utf-8")
                self._send_response_data(200, "application/json", data)
                return

            # 3. Static Files (style.css, client.js)
            elif parsed_path.startswith("/static/"):
                filename = parsed_path[len("/static/"):]
                resolved_static_dir = static_dir or os.path.join(os.path.dirname(__file__), "static")
                filepath = os.path.join(resolved_static_dir, filename)

                if os.path.exists(filepath) and os.path.isfile(filepath):
                    mime_type = "text/css" if filepath.endswith(".css") else "application/javascript"
                    with open(filepath, "rb") as f:
                        file_data = f.read()
                    self._send_response_data(200, mime_type, file_data)
                    return
                else:
                    self._send_response_data(404, "text/plain", b"Static file not found")
                    return

            self._send_response_data(404, "text/plain", b"Not Found")

        def do_POST(self):
            parsed_path = urllib.parse.urlparse(self.path).path

            # Event Dispatch Endpoint
            if parsed_path == "/api/event":
                content_length = int(self.headers.get("Content-Length", 0))
                body = self.rfile.read(content_length).decode("utf-8")
                
                try:
                    payload = json.loads(body) if body else {}
                except Exception:
                    payload = {}

                target_id = payload.get("id")
                event_type = payload.get("event", "click")
                event_data = payload.get("data")

                # Dispatch event through our Python framework
                result = app_instance.dispatch_event(target_id, event_type, event_data)
                
                response_json = json.dumps({
                    "success": True,
                    "handled": result["handled"],
                    "html": result["html"],
                    "state": result["state"]
                }).encode("utf-8")

                self._send_response_data(200, "application/json", response_json)
                return

            # Reset State Endpoint
            elif parsed_path == "/api/reset":
                new_html = app_instance.reset_state()
                response_json = json.dumps({
                    "success": True,
                    "html": new_html,
                    "state": app_instance.state
                }).encode("utf-8")
                self._send_response_data(200, "application/json", response_json)
                return

            self._send_response_data(404, "text/plain", b"Not Found")

    return PyUIHTTPHandler


def run_server(app_instance, host="0.0.0.0", port=8000, static_dir=None):
    """
    Starts the local HTTP server to run the PyUI application in the browser.
    """
    handler_class = create_request_handler(app_instance, static_dir=static_dir)
    server = HTTPServer((host, port), handler_class)
    print("=" * 60)
    print(f"🚀 PyUI Server is running at http://{host}:{port}")
    print("   Open your browser to see your Python-built UI live!")
    print("   Press Ctrl+C to stop the server.")
    print("=" * 60)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 PyUI Server stopped.")
        server.server_close()
