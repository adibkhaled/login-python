import psycopg2
import pytest
import application

from application import app

@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client

def test_login_get(client):
    rv = client.get("/")
    assert rv.status_code == 200
    assert b"Login" in rv.data

def test_login_success(client, monkeypatch):
    # simulate DB returning stored password hash tuple
    monkeypatch.setattr(application, "execute_query", lambda *a, **k: ("fakehash",))
    # bypass bcrypt check
    monkeypatch.setattr(application.bcrypt, "checkpw", lambda pw, h: True)
    rv = client.post("/", data={"username": "adib", "password": "adib"})
    assert rv.status_code == 302
    assert rv.headers["Location"].endswith("/home")

def test_login_invalid_password(client, monkeypatch):
    monkeypatch.setattr(application, "execute_query", lambda *a, **k: ("fakehash",))
    monkeypatch.setattr(application.bcrypt, "checkpw", lambda pw, h: False)
    rv = client.post("/", data={"username": "adib", "password": "wrong"})
    assert rv.status_code == 200
    assert b"Invalid username or password" in rv.data