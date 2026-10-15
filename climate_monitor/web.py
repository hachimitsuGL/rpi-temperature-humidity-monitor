"""Flask web dashboard and read-only JSON endpoints."""

import socket

from flask import Flask, jsonify, render_template


def create_app(monitor_state, comfort_settings):
    app = Flask(__name__)

    @app.get("/")
    def index():
        return render_template("index.html")

    @app.get("/api/status")
    def api_status():
        state = monitor_state.current()
        state.update(vars(comfort_settings.snapshot()))
        return jsonify(state)

    @app.get("/api/history")
    def api_history():
        return jsonify(monitor_state.history())

    return app


def get_local_ip():
    """Determine the local outgoing IP without sending application data."""
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        try:
            sock.connect(("8.8.8.8", 80))
            return sock.getsockname()[0]
        except OSError:
            return "<raspberry-pi-ip>"
