"""
PyUI Runner Bridge
File: pyui/runner_bridge.py

A command-line interface that allows external tools, test runners, and the web studio
to interact directly with Python's PyUI framework instances.
"""

import sys
import json
import unittest
from io import StringIO

import framework
import app as quiz_app
import counter_app


def handle_render(app_type):
    target_app = quiz_app.app if app_type == "quiz" else counter_app.app
    html_out = target_app.render_ui_html()
    print(json.dumps({
        "success": True,
        "html": html_out,
        "state": target_app.state,
        "tree": target_app.current_tree.to_dict() if target_app.current_tree else None
    }))


def handle_dispatch(app_type, target_id, event_type, state_json_str):
    target_app = quiz_app.app if app_type == "quiz" else counter_app.app
    
    # Restore provided state
    if state_json_str:
        try:
            target_app.state = json.loads(state_json_str)
        except Exception as e:
            pass

    # Ensure tree is built and event handlers registered
    target_app.render_ui_html()
    
    # Dispatch event
    result = target_app.dispatch_event(target_id, event_type)
    
    print(json.dumps({
        "success": True,
        "handled": result["handled"],
        "html": result["html"],
        "state": result["state"],
        "tree": target_app.current_tree.to_dict() if target_app.current_tree else None
    }))


def handle_tests():
    # Run unittest suite and capture output
    import test_framework
    suite = unittest.TestLoader().loadTestsFromModule(test_framework)
    stream = StringIO()
    runner = unittest.TextTestRunner(stream=stream, verbosity=2)
    res = runner.run(suite)
    
    output = stream.getvalue()
    print(json.dumps({
        "success": res.wasSuccessful(),
        "total": res.testsRun,
        "errors": len(res.errors),
        "failures": len(res.failures),
        "output": output
    }))


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(json.dumps({"error": "No command specified"}))
        sys.exit(1)

    command = sys.argv[1]

    if command == "render":
        app_type = sys.argv[2] if len(sys.argv) > 2 else "quiz"
        handle_render(app_type)
    elif command == "dispatch":
        app_type = sys.argv[2] if len(sys.argv) > 2 else "quiz"
        target_id = sys.argv[3] if len(sys.argv) > 3 else ""
        event_type = sys.argv[4] if len(sys.argv) > 4 else "click"
        state_json = sys.argv[5] if len(sys.argv) > 5 else "{}"
        handle_dispatch(app_type, target_id, event_type, state_json)
    elif command == "test":
        handle_tests()
    else:
        print(json.dumps({"error": f"Unknown command: {command}"}))
