from fastapi.testclient import TestClient
from .main import app

client = TestClient(app)

def test_home():
    response = client.get("/api/")
    assert response.status_code == 307
    # assert response.headers["location"] == "https://yura-platonov.github.io/Team-Chat/"

def test_reset():
    response = client.get("/api/reset")
    assert response.status_code == 200
    # assert "window_new_password.html" in response.text

def test_success_page():
    response = client.get("/api/success-page")
    assert response.status_code == 200
    # assert "success-page.html" in response.text

def test_privacy_policy():
    response = client.get("/api/privacy-policy")
    assert response.status_code == 307
    # assert response.headers["location"] == "https://yura-platonov.github.io/Team-Chat/#/PrivacyPolicy"

def test_contact_form():
    response = client.get("/api/contact-form")
    assert response.status_code == 200
    # assert "index.html" in response.text