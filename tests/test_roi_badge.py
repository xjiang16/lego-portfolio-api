SET_PAYLOAD = {
    "set_name": "Tiny Plants",
    "set_number": "10329",
    "theme": "Botanicals",
    "purchase_price": 50.00,
    "quantity": 1,
    "estimated_market_value": 50.00,
    "condition": "New",
    "is_sealed": True,
    "notes": "",
}


def test_badge_shows_na_with_no_sets(client):
    response = client.get("/badge/roi.svg")

    assert response.status_code == 200
    assert response.headers["content-type"] == "image/svg+xml"
    assert "n/a" in response.text


def test_badge_shows_positive_roi_in_green(client, monkeypatch):
    monkeypatch.setattr("main.market.get_market_price", lambda set_number: 75.00)
    client.post("/add-set", json=SET_PAYLOAD)

    response = client.get("/badge/roi.svg")

    assert "+50.0%" in response.text
    assert "#4c1" in response.text


def test_badge_shows_negative_roi_in_red(client, monkeypatch):
    monkeypatch.setattr("main.market.get_market_price", lambda set_number: 25.00)
    client.post("/add-set", json=SET_PAYLOAD)

    response = client.get("/badge/roi.svg")

    assert "-50.0%" in response.text
    assert "#e05d44" in response.text


def test_badge_sets_cache_control_header(client):
    response = client.get("/badge/roi.svg")
    assert response.headers["cache-control"] == "public, max-age=3600"
