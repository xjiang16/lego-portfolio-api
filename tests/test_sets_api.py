SET_PAYLOAD = {
    "set_name": "Tiny Plants",
    "set_number": "10329",
    "theme": "Botanicals",
    "purchase_price": 49.99,
    "quantity": 1,
    "estimated_market_value": 49.99,
    "condition": "New",
    "is_sealed": True,
    "notes": "",
    "year": 2023,
    "num_parts": 758,
    "image_url": "https://example.com/img.jpg",
}


def test_get_all_sets_starts_empty(client):
    response = client.get("/sets")
    assert response.status_code == 200
    assert response.json() == []


def test_add_set_succeeds(client):
    response = client.post("/add-set", json=SET_PAYLOAD)
    assert response.status_code == 200
    assert "Tiny Plants" in response.json()["message"]

    sets = client.get("/sets").json()
    assert len(sets) == 1
    assert sets[0]["set_number"] == "10329"


def test_add_set_rejects_duplicate_set_number(client):
    client.post("/add-set", json=SET_PAYLOAD)
    response = client.post("/add-set", json=SET_PAYLOAD)

    assert response.status_code == 400
    assert "already in your collection" in response.json()["detail"]

    # Duplicate must not have been inserted alongside the original.
    assert len(client.get("/sets").json()) == 1


def test_delete_set_removes_it(client):
    client.post("/add-set", json=SET_PAYLOAD)
    set_id = client.get("/sets").json()[0]["id"]

    response = client.delete(f"/sets/{set_id}")

    assert response.status_code == 200
    assert "Tiny Plants" in response.json()["message"]
    assert client.get("/sets").json() == []


def test_delete_nonexistent_set_returns_404(client):
    response = client.delete("/sets/9999")

    assert response.status_code == 404
    assert "not found" in response.json()["detail"]


def test_update_retirement_date_succeeds(client):
    client.post("/add-set", json=SET_PAYLOAD)
    set_id = client.get("/sets").json()[0]["id"]

    response = client.patch(f"/sets/{set_id}/retirement-date", json={"retirement_date": "2027-06-01"})

    assert response.status_code == 200
    assert "Tiny Plants" in response.json()["message"]
    assert client.get("/sets").json()[0]["retirement_date"] == "2027-06-01"


def test_update_retirement_date_to_null_clears_it(client):
    client.post("/add-set", json=SET_PAYLOAD)
    set_id = client.get("/sets").json()[0]["id"]
    client.patch(f"/sets/{set_id}/retirement-date", json={"retirement_date": "2027-06-01"})

    response = client.patch(f"/sets/{set_id}/retirement-date", json={"retirement_date": None})

    assert response.status_code == 200
    assert client.get("/sets").json()[0]["retirement_date"] is None


def test_update_retirement_date_for_nonexistent_set_returns_404(client):
    response = client.patch("/sets/9999/retirement-date", json={"retirement_date": "2027-06-01"})

    assert response.status_code == 404
    assert "not found" in response.json()["detail"]
