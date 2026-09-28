from app.core.sentiment_service import parse_analyst_recommendation_trends


def test_parse_analyst_empty():
    r = parse_analyst_recommendation_trends([])
    assert r["analyst_recommendation_total"] is None
    assert r["analyst_recommendation_period"] is None


def test_parse_analyst_latest_period_and_pcts():
    rows = [
        {
            "period": "2024-01-01",
            "strongBuy": 1,
            "buy": 2,
            "hold": 3,
            "sell": 4,
            "strongSell": 0,
        },
        {
            "period": "2024-06-01",
            "strongBuy": 0,
            "buy": 10,
            "hold": 0,
            "sell": 0,
            "strongSell": 0,
        },
    ]
    r = parse_analyst_recommendation_trends(rows)
    assert r["analyst_recommendation_period"] == "2024-06-01"
    assert r["analyst_recommendation_total"] == 10
    assert r["analyst_recommendation_bullish_pct"] == 100.0
    assert r["analyst_recommendation_bearish_pct"] == 0.0


def test_parse_analyst_snake_case_keys():
    rows = [
        {
            "period": "2024-03-01",
            "strong_buy": 1,
            "buy": 1,
            "hold": 1,
            "sell": 1,
            "strong_sell": 1,
        }
    ]
    r = parse_analyst_recommendation_trends(rows)
    assert r["analyst_recommendation_total"] == 5
    assert r["analyst_recommendation_bullish_pct"] == 40.0
    assert r["analyst_recommendation_bearish_pct"] == 40.0
