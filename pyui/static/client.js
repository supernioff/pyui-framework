/**
 * PyUI Client Bridge (Minimal Frontend Helper)
 * File: pyui/static/client.js
 * 
 * WHY IS THIS FILE HERE?
 * Web browsers execute HTML, CSS, and JavaScript. Because our UI framework,
 * component tree, state, and business logic run in Python on the server, we need
 * a lightweight bridge (~30 lines) to:
 * 
 * 1. Listen for user clicks on elements created by PyUI.
 * 2. Send the element ID to the Python backend via a quick HTTP POST request.
 * 3. Take the newly rendered HTML returned by Python and swap it into the webpage.
 * 
 * NOTE: This file contains NO UI components, NO state storage, and NO business logic.
 * All framework logic lives strictly in `framework.py` and `app.py`.
 */

document.addEventListener("DOMContentLoaded", () => {
    const mountPoint = document.getElementById("pyui-app-mount");
    if (!mountPoint) return;

    // Use event delegation on mount point to capture clicks even after DOM re-renders
    mountPoint.addEventListener("click", async (event) => {
        // Find if the clicked element or any parent is a PyUI actionable element
        const target = event.target.closest('[data-pyui-event="click"]');
        if (!target) return;

        const targetId = target.id;
        if (!targetId || target.disabled) return;

        // Visual feedback during request
        target.classList.add("pyui-loading");

        try {
            // Forward the event to the Python framework
            const response = await fetch("/api/event", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    id: targetId,
                    event: "click"
                })
            });

            if (!response.ok) {
                console.error("PyUI Event Error:", response.statusText);
                return;
            }

            const data = await response.json();

            // Replace current HTML with the freshly rendered HTML from Python
            if (data.html) {
                mountPoint.innerHTML = data.html;
                // Dispatch custom event for debuggers/inspectors
                window.dispatchEvent(new CustomEvent("pyui:updated", { detail: data }));
            }
        } catch (err) {
            console.error("Network error sending event to PyUI Python server:", err);
        }
    });

    // Handle input change events if any input element is present
    mountPoint.addEventListener("change", async (event) => {
        const target = event.target.closest('[data-pyui-event="change"]');
        if (!target) return;

        const targetId = target.id;
        const value = target.value;

        try {
            const response = await fetch("/api/event", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    id: targetId,
                    event: "change",
                    data: value
                })
            });

            const data = await response.json();
            if (data.html) {
                mountPoint.innerHTML = data.html;
                window.dispatchEvent(new CustomEvent("pyui:updated", { detail: data }));
            }
        } catch (err) {
            console.error("Error sending input change to PyUI:", err);
        }
    });
});
