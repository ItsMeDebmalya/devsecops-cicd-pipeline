"""Minimal Flask service used to exercise the DevSecOps pipeline.

The app itself is deliberately small; the point of this repository is the
security-gated CI/CD pipeline around it, not the application logic.
"""
from __future__ import annotations

import os

from flask import Flask, jsonify

app = Flask(__name__)


@app.get("/healthz")
def healthz():
    """Liveness probe."""
    return jsonify(status="ok"), 200


@app.get("/version")
def version():
    """Return the build version injected at container build time."""
    return jsonify(version=os.environ.get("APP_VERSION", "dev")), 200


@app.get("/add/<int:a>/<int:b>")
def add(a: int, b: int):
    """Tiny bit of business logic so there is something to unit-test."""
    return jsonify(result=a + b), 200


def create_app() -> Flask:
    return app


if __name__ == "__main__":  # pragma: no cover
    # Bind host/port from env; debug stays off (hardened default).
    port = int(os.environ.get("PORT", "8080"))
    app.run(host="0.0.0.0", port=port)
