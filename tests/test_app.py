from typing import Dict, Any
from fastapi.testclient import TestClient


def test_root_redirect(client: TestClient):
    resp = client.get("/", allow_redirects=False)
    assert resp.status_code in (302, 307)
    assert resp.headers.get("location") == "/static/index.html"


def test_get_activities(client: TestClient):
    resp = client.get("/activities")
    assert resp.status_code == 200
    data: Dict[str, Dict[str, Any]] = resp.json()
    # Expect multiple activities and known keys
    assert isinstance(data, dict)
    assert "Chess Club" in data
    chess = data["Chess Club"]
    assert set(["description", "schedule", "max_participants", "participants"]) <= set(chess.keys())
    assert isinstance(chess["participants"], list)


def test_signup_then_duplicate_then_unregister_flow(client: TestClient):
    activity = "Chess Club"
    email = "testuser+pytest@mergington.edu"

    # Sign up
    r1 = client.post(f"/activities/{activity}/signup", params={"email": email})
    assert r1.status_code == 200
    assert f"Signed up {email} for {activity}" in r1.json().get("message", "")

    # Duplicate signup should fail
    r2 = client.post(f"/activities/{activity}/signup", params={"email": email})
    assert r2.status_code == 400
    assert r2.json()["detail"] == "Student is already signed up"

    # Unregister should succeed
    r3 = client.delete(f"/activities/{activity}/unregister", params={"email": email})
    assert r3.status_code == 200
    assert f"Unregistered {email} from {activity}" in r3.json().get("message", "")

    # Unregister again should fail
    r4 = client.delete(f"/activities/{activity}/unregister", params={"email": email})
    assert r4.status_code == 400
    assert r4.json()["detail"] == "Student is not signed up for this activity"


def test_activity_not_found_errors(client: TestClient):
    activity = "Totally Nonexistent Activity"
    email = "nobody@mergington.edu"

    r1 = client.post(f"/activities/{activity}/signup", params={"email": email})
    assert r1.status_code == 404
    assert r1.json()["detail"] == "Activity not found"

    r2 = client.delete(f"/activities/{activity}/unregister", params={"email": email})
    assert r2.status_code == 404
    assert r2.json()["detail"] == "Activity not found"
