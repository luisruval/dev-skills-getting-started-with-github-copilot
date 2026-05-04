from urllib.parse import quote

from src.app import activities


def _activity_path(activity_name: str) -> str:
    return f"/activities/{quote(activity_name, safe='')}/signup"


def test_get_activities_returns_all_activities(client):
    response = client.get("/activities")

    assert response.status_code == 200
    payload = response.json()
    assert isinstance(payload, dict)
    assert "Chess Club" in payload


def test_signup_for_activity_succeeds(client):
    activity_name = "Chess Club"
    email = "new.student@mergington.edu"

    response = client.post(_activity_path(activity_name), params={"email": email})

    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {email} for {activity_name}"}
    assert email in activities[activity_name]["participants"]


def test_signup_for_unknown_activity_returns_404(client):
    response = client.post(_activity_path("Unknown Club"), params={"email": "student@mergington.edu"})

    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_signup_duplicate_participant_returns_400(client):
    activity_name = "Chess Club"
    existing_email = activities[activity_name]["participants"][0]

    response = client.post(_activity_path(activity_name), params={"email": existing_email})

    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"


def test_signup_for_full_activity_returns_400(client):
    activity_name = "Chess Club"
    activity = activities[activity_name]
    activity["max_participants"] = len(activity["participants"])

    response = client.post(_activity_path(activity_name), params={"email": "overflow@mergington.edu"})

    assert response.status_code == 400
    assert response.json()["detail"] == "Activity is full"


def test_unregister_from_activity_succeeds(client):
    activity_name = "Chess Club"
    email = "remove.me@mergington.edu"
    activities[activity_name]["participants"].append(email)

    response = client.delete(_activity_path(activity_name), params={"email": email})

    assert response.status_code == 200
    assert response.json() == {"message": f"Unregistered {email} from {activity_name}"}
    assert email not in activities[activity_name]["participants"]


def test_unregister_from_unknown_activity_returns_404(client):
    response = client.delete(_activity_path("Unknown Club"), params={"email": "student@mergington.edu"})

    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_unregister_non_participant_returns_404(client):
    response = client.delete(_activity_path("Chess Club"), params={"email": "absent@mergington.edu"})

    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found in this activity"