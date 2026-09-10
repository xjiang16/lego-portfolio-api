import model
from database import SessionLocal

SET_PAYLOAD = {
    "set_name": "Tiny Plants",
    "set_number": "10329",
    "theme": "Botanicals",
    "purchase_price": 50.00,
    "quantity": 2,
    "estimated_market_value": 50.00,
    "condition": "New",
    "is_sealed": True,
    "notes": "",
}


def test_stats_with_no_sets(client):
    stats = client.get("/portfolio/stats").json()
    assert stats["total_sets"] == 0
    assert stats["summary"]["total_investment"] == "$0.00"
    assert stats["summary"]["roi_percentage"] == "0.00%"


def test_stats_computes_investment_value_and_roi(client, monkeypatch):
    monkeypatch.setattr("main.market.get_market_price", lambda set_number: 75.00)

    client.post("/add-set", json=SET_PAYLOAD)
    stats = client.get("/portfolio/stats").json()

    # 2 sets purchased at $50 each = $100 invested; mocked market price of $75 * 2 = $150 value.
    # total_sets counts physical sets owned (quantity), not distinct rows.
    assert stats["total_sets"] == 2
    assert stats["summary"]["total_investment"] == "$100.00"
    assert stats["summary"]["current_market_value"] == "$150.00"
    assert stats["summary"]["net_profit"] == "$50.00"
    assert stats["summary"]["roi_percentage"] == "50.00%"


def test_total_sets_sums_quantity_across_multiple_rows(client, monkeypatch):
    monkeypatch.setattr("main.market.get_market_price", lambda set_number: 10.0)

    client.post("/add-set", json=SET_PAYLOAD)  # quantity=2
    client.post("/add-set", json={**SET_PAYLOAD, "set_name": "Succulents", "set_number": "10309", "quantity": 3})

    stats = client.get("/portfolio/stats").json()
    assert stats["total_sets"] == 5


def test_history_empty_by_default(client):
    assert client.get("/portfolio/history").json() == []


def test_history_returns_snapshots_ordered_by_time(client):
    db = SessionLocal()
    try:
        db.add(model.PriceHistory(set_number="10329", price=50.0))
        db.add(model.PriceHistory(set_number="10329", price=55.0))
        db.commit()
    finally:
        db.close()

    history = client.get("/portfolio/history").json()
    assert [h["price"] for h in history] == [50.0, 55.0]
