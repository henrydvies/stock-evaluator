from dataclasses import dataclass
from datetime import datetime, timezone
from statistics import stdev
from typing import Any, List, Mapping

from app.providers.finnhub_client import (
    FinnhubClient,
    FinnhubClientError,
    HttpFinnhubClient,
    default_company_news_window,
)
from app.schemas.sentiment import SentimentResponse, SentimentStatus
from app.sentiment.vader_narrative import VaderNarrativeResult, analyze_company_news_vader
from app.utils.ticker import normalise_and_validate_ticker


def _coerce_int(value: Any) -> int | None:
    if value is None:
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def parse_analyst_recommendation_trends(
    rows: List[Mapping[str, Any]],
) -> dict[str, Any]:
    """
    Map Finnhub GET /stock/recommendation array to SentimentResponse analyst_* fields.
    Uses the latest period (lexicographic max on `period` string, valid for ISO dates).
    """
    empty: dict[str, Any] = {
        "analyst_recommendation_period": None,
        "analyst_recommendation_strong_buy": None,
        "analyst_recommendation_buy": None,
        "analyst_recommendation_hold": None,
        "analyst_recommendation_sell": None,
        "analyst_recommendation_strong_sell": None,
        "analyst_recommendation_total": None,
        "analyst_recommendation_bullish_pct": None,
        "analyst_recommendation_bearish_pct": None,
    }
    if not rows:
        return empty

    latest = max(rows, key=lambda r: str(r.get("period") or ""))
    period_raw = latest.get("period")
    period_str = str(period_raw).strip() if period_raw is not None else None

    sb = _coerce_int(latest.get("strongBuy", latest.get("strong_buy")))
    buy = _coerce_int(latest.get("buy"))
    hold = _coerce_int(latest.get("hold"))
    sell = _coerce_int(latest.get("sell"))
    ss = _coerce_int(latest.get("strongSell", latest.get("strong_sell")))

    total = sum(int(x or 0) for x in (sb, buy, hold, sell, ss))
    if total <= 0:
        return {**empty, "analyst_recommendation_period": period_str}

    bullish_n = int(sb or 0) + int(buy or 0)
    bearish_n = int(sell or 0) + int(ss or 0)
    return {
        "analyst_recommendation_period": period_str,
        "analyst_recommendation_strong_buy": sb,
        "analyst_recommendation_buy": buy,
        "analyst_recommendation_hold": hold,
        "analyst_recommendation_sell": sell,
        "analyst_recommendation_strong_sell": ss,
        "analyst_recommendation_total": total,
        "analyst_recommendation_bullish_pct": 100.0 * bullish_n / total,
        "analyst_recommendation_bearish_pct": 100.0 * bearish_n / total,
    }


def _narrative_status(n: int, compounds: tuple[float, ...]) -> SentimentStatus:
    if n == 0:
        return SentimentStatus.LOW_DATA
    if n < 3:
        return SentimentStatus.LOW_DATA
    if len(compounds) >= 3:
        sd = stdev(compounds)
        if sd > 0.55:
            return SentimentStatus.NOISY
    return SentimentStatus.OK


def _vader_to_response(
    vader: VaderNarrativeResult,
    analyst_fields: Mapping[str, Any],
) -> SentimentResponse:
    n = vader.narrative_headline_count
    status = _narrative_status(n, vader.compounds)
    titles = list(vader.narrative_headline_sample_titles) or None

    return SentimentResponse(
        narrative_news_score=vader.narrative_news_score if n > 0 else None,
        narrative_bullish_pct=vader.narrative_bullish_pct if n > 0 else None,
        narrative_bearish_pct=vader.narrative_bearish_pct if n > 0 else None,
        narrative_buzz=None,
        narrative_article_count_proxy=None,
        narrative_sector_news_score=None,
        narrative_vs_sector_news_score=None,
        narrative_confidence=vader.narrative_confidence,
        narrative_status=status,
        narrative_fetched_at=datetime.now(timezone.utc).isoformat(),
        narrative_provider="finnhub",
        narrative_headline_count=n,
        narrative_headline_distinct_sources=vader.narrative_headline_distinct_sources,
        narrative_headline_sample_titles=titles,
        **dict(analyst_fields),
    )


@dataclass
class SentimentService:
    """Company-news narrative sentiment via Finnhub + VADER."""

    finnhub: FinnhubClient
    news_window_days: int = 7

    async def get_sentiment_for_symbol(self, raw_symbol: str) -> SentimentResponse:
        symbol = normalise_and_validate_ticker(raw_symbol)
        date_from, date_to = default_company_news_window(self.news_window_days)
        articles: List[Mapping[str, Any]] = await self.finnhub.fetch_company_news(
            symbol, date_from, date_to
        )
        vader = analyze_company_news_vader(articles)

        try:
            rec_rows = await self.finnhub.fetch_recommendation_trends(symbol)
            analyst_fields = parse_analyst_recommendation_trends(rec_rows)
        except FinnhubClientError:
            analyst_fields = parse_analyst_recommendation_trends([])

        return _vader_to_response(vader, analyst_fields)


def get_sentiment_service() -> SentimentService:
    return SentimentService(finnhub=HttpFinnhubClient())
