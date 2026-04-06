from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field

# Enum for the status of sentiment analysis based on data availability and confidence.
class SentimentStatus(str, Enum):
    OK = "ok"
    LOW_DATA = "low_data"
    NOISY = "noisy"
    AMBIGUOUS_ENTITY = "ambiguous_entity"
    STALE = "stale"
    SOURCE_ERROR = "source_error"

class SentimentResponse(BaseModel):
    """
    Market narrative sentiment.
    """

    ## Finnhub sourced sentiment fields
    narrative_news_score: Optional[float] = Field(
        None,
        description="Finnhub companyNewsScore mapped to ~[-1, 1] when /news-sentiment is available; null if not licensed.",
    )
    narrative_bullish_pct: Optional[float] = Field(
        None,
        description="Share of sampled company news classified bullish (0–100) from /news-sentiment; null if unavailable.",
    )
    narrative_bearish_pct: Optional[float] = Field(
        None,
        description="Share of sampled company news classified bearish (0–100) from /news-sentiment; null if unavailable.",
    )
    narrative_buzz: Optional[float] = Field(
        None,
        description="Normalized buzz / attention from /news-sentiment when available; null on free-tier-only access.",
    )
    narrative_article_count_proxy: Optional[int] = Field(
        None,
        description="Article volume proxy from /news-sentiment buzz fields when available; on free tier use narrative_headline_count instead.",
    )
    narrative_sector_news_score: Optional[float] = Field(
        None,
        description="Sector average news score from /news-sentiment when provided.",
    )
    narrative_vs_sector_news_score: Optional[float] = Field(
        None,
        description="Company vs sector narrative gap when sector benchmark is present.",
    )

    narrative_confidence: float = Field(
        ...,
        description="0–1 confidence; on company-news-only tier, derive mainly from headline count/source diversity.",
    )
    narrative_status: SentimentStatus = Field(
        ...,
        description="Quality gate for narrative data (ok, low_data, noisy, source_error, etc.).",
    )
    narrative_fetched_at: str = Field(
        ...,
        description="ISO-8601 timestamp when narrative data was assembled.",
    )
    narrative_provider: str = Field(
        ...,
        description="Upstream provider id (e.g. finnhub).",
    )

    # --- Finnhub GET /company-news (usually available on free tier; date window) ---
    narrative_headline_count: Optional[int] = Field(
        None,
        description="Number of company-news items in the requested window.",
    )
    narrative_headline_distinct_sources: Optional[int] = Field(
        None,
        description="Distinct source count from company-news payload when derivable.",
    )
    narrative_headline_sample_titles: Optional[List[str]] = Field(
        None,
        description="Sample headlines; respect Finnhub ToS for display/redistribution.",
    )