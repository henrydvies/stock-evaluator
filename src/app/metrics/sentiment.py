from typing import Any, Dict, Optional

from .base import BaseMetric
from app.core.sentiment_service import SentimentService, get_sentiment_service


class StockSentimentMetric(BaseMetric):
    """Narrative sentiment from Finnhub company news scored with VADER."""

    name = "sentiment"

    def __init__(self, service: Optional[SentimentService] = None) -> None:
        self.service = service or get_sentiment_service()

    async def compute(self, ticker: str) -> Dict[str, Any]:
        res = await self.service.get_sentiment_for_symbol(ticker)
        counts = res.analyst_recommendation_counts
        return {
            "sentiment.narrative_news_score": res.narrative_news_score,
            "sentiment.narrative_bullish_pct": res.narrative_bullish_pct,
            "sentiment.narrative_bearish_pct": res.narrative_bearish_pct,
            "sentiment.narrative_confidence": res.narrative_confidence,
            "sentiment.narrative_status": res.narrative_status.value,
            "sentiment.narrative_fetched_at": res.narrative_fetched_at,
            "sentiment.narrative_provider": res.narrative_provider,
            "sentiment.narrative_headline_count": res.narrative_headline_count,
            "sentiment.narrative_headline_distinct_sources": res.narrative_headline_distinct_sources,
            "sentiment.narrative_headline_sample_titles": res.narrative_headline_sample_titles,
            "sentiment.analyst_recommendation_period": res.analyst_recommendation_period,
            "sentiment.analyst_recommendation_counts": counts.model_dump() if counts else None,
            "sentiment.analyst_recommendation_total": res.analyst_recommendation_total,
            "sentiment.analyst_recommendation_bullish_pct": res.analyst_recommendation_bullish_pct,
            "sentiment.analyst_recommendation_bearish_pct": res.analyst_recommendation_bearish_pct,
            "sentiment.analyst_recommendation_neutral_pct": res.analyst_recommendation_neutral_pct,
            "sentiment.analyst_recommendation_net_score": res.analyst_recommendation_net_score,
        }
