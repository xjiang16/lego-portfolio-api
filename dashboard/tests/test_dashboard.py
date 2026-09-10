from datetime import date, timedelta
from unittest.mock import Mock, patch

from streamlit.testing.v1 import AppTest

STATS = {
    "user": "Xiaoqi Jiang",
    "total_sets": 2,
    "summary": {
        "total_investment": "$94.98",
        "current_market_value": "$113.49",
        "net_profit": "$18.51",
        "roi_percentage": "19.49%",
    },
    "note": "Market data currently provided by Mock Service",
}

SETS = [
    {
        "id": 1, "set_name": "Tiny Plants", "set_number": "10329", "theme": "Botanicals",
        "purchase_price": 49.99, "quantity": 1, "year": 2023, "num_parts": 758,
        "image_url": "https://example.com/a.jpg", "condition": "New", "is_sealed": True,
        "notes": None, "estimated_market_value": None, "retirement_date": None,
    },
    {
        "id": 2, "set_name": "Succulents", "set_number": "10309", "theme": "Succulents",
        "purchase_price": 44.99, "quantity": 1, "year": 2022, "num_parts": 771,
        "image_url": "https://example.com/b.jpg", "condition": "New", "is_sealed": True,
        "notes": None, "estimated_market_value": None, "retirement_date": None,
    },
]

# Tiny Plants (10329): current 54.99 vs purchase 49.99 -> profit 5.00
# Succulents (10309): current 58.50 vs purchase 44.99 -> profit 13.51
HISTORY = [
    {"id": 1, "set_number": "10329", "price": 54.99, "captured_at": "2026-01-01T00:00:00"},
    {"id": 2, "set_number": "10309", "price": 58.50, "captured_at": "2026-01-01T00:00:00"},
]


def _mock_response(json_data):
    resp = Mock()
    resp.status_code = 200
    resp.json.return_value = json_data
    return resp


def _fake_get(stats, sets, history):
    def fake_get(url, *args, **kwargs):
        if url.endswith("/portfolio/stats"):
            return _mock_response(stats)
        if url.endswith("/sets"):
            return _mock_response(sets)
        if url.endswith("/portfolio/history"):
            return _mock_response(history)
        raise AssertionError(f"Unexpected URL requested in test: {url}")
    return fake_get


def test_app_runs_without_exceptions():
    with patch("requests.get", side_effect=_fake_get(STATS, SETS, HISTORY)):
        at = AppTest.from_file("dashboard/dashboard.py")
        at.run(timeout=15)
        assert at.exception == []


def test_top_metrics_render_from_stats():
    with patch("requests.get", side_effect=_fake_get(STATS, SETS, HISTORY)):
        at = AppTest.from_file("dashboard/dashboard.py")
        at.run(timeout=15)

    values = [m.value for m in at.metric]
    assert "2" in values
    assert "$94.98" in values
    assert "$113.49" in values
    assert "$18.51" in values


def test_table_computes_current_value_and_profit_per_set():
    with patch("requests.get", side_effect=_fake_get(STATS, SETS, HISTORY)):
        at = AppTest.from_file("dashboard/dashboard.py")
        at.run(timeout=15)

    df = at.dataframe[0].value.set_index("set_name")
    assert df.loc["Tiny Plants", "current_value"] == 54.99
    assert df.loc["Tiny Plants", "profit"] == 5.00
    assert round(df.loc["Succulents", "profit"], 2) == 13.51


def test_table_falls_back_gracefully_with_no_price_history():
    with patch("requests.get", side_effect=_fake_get(STATS, SETS, history=[])):
        at = AppTest.from_file("dashboard/dashboard.py")
        at.run(timeout=15)

    assert at.exception == []
    df = at.dataframe[0].value
    assert df["current_value"].isna().all()
    assert df["profit"].isna().all()


def test_retiring_soon_flag_shows_for_near_retirement_dates():
    soon = (date.today() + timedelta(days=30)).isoformat()
    far = (date.today() + timedelta(days=200)).isoformat()
    sets_with_retirement = [
        {**SETS[0], "retirement_date": soon},
        {**SETS[1], "retirement_date": far},
    ]

    with patch("requests.get", side_effect=_fake_get(STATS, sets_with_retirement, HISTORY)):
        at = AppTest.from_file("dashboard/dashboard.py")
        at.run(timeout=15)

    df = at.dataframe[0].value.set_index("set_name")
    assert df.loc["Tiny Plants", "retirement_status"] == "🔥 Retiring soon"
    assert df.loc["Succulents", "retirement_status"] == ""


def test_theme_filter_narrows_table_but_not_top_metrics():
    with patch("requests.get", side_effect=_fake_get(STATS, SETS, HISTORY)):
        at = AppTest.from_file("dashboard/dashboard.py")
        at.run(timeout=15)
        at.multiselect[0].set_value(["Botanicals"]).run(timeout=15)

        df = at.dataframe[0].value
        assert df["set_name"].tolist() == ["Tiny Plants"]

        # Filtering the table must not change the portfolio-wide summary metrics.
        values = [m.value for m in at.metric]
        assert "$94.98" in values
