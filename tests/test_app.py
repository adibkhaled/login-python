import psycopg2
import pytest
from src.application import app  # Flask app object
import src.application as application  # module for execute_query, bcrypt, etc.
import src.dbhelper as dbhelper
import src.login as login

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
    monkeypatch.setattr(dbhelper, "execute_query", lambda *a, **k: ("fakehash",))
    # bypass bcrypt check
    monkeypatch.setattr(login.bcrypt, "checkpw", lambda pw, h: True)
    rv = client.post("/", data={"username": "adib", "password": "adib"})
    assert rv.status_code == 302
    assert rv.headers["Location"].endswith("/home")

def test_login_invalid_password(client, monkeypatch):
    monkeypatch.setattr(dbhelper, "execute_query", lambda *a, **k: ("fakehash",))
    monkeypatch.setattr(login.bcrypt, "checkpw", lambda pw, h: False)
    rv = client.post("/", data={"username": "adib", "password": "wrong"})
    assert rv.status_code == 200
    assert b"Invalid username or password" in rv.data
