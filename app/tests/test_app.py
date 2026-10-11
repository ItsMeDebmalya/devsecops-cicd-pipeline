"""Unit tests for the sample service."""
from app.app import create_app


def client():
    app = create_app()
    app.testing = True
    return app.test_client()


def test_healthz():
    resp = client().get("/healthz")
    assert resp.status_code == 200
    assert resp.get_json() == {"status": "ok"}


def test_version_default():
    resp = client().get("/version")
    assert resp.status_code == 200
    assert "version" in resp.get_json()


def test_add():
    resp = client().get("/add/2/3")
    assert resp.status_code == 200
    assert resp.get_json() == {"result": 5}
