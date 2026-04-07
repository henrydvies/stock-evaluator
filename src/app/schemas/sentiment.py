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


class AnalystRecommendationCounts(BaseModel):
    strong_buy: int = Field(..., description="Count of strong buy ratings in the latest recommendation row.")
    buy: int = Field(..., description="Count of buy ratings in the latest recommendation row.")
    hold: int = Field(..., description="Count of hold ratings in the latest recommendation row.")
    sell: int = Field(..., description="Count of sell ratings in the latest recommendation row.")
    strong_sell: int = Field(..., description="Count of strong sell ratings in the latest recommendation row.")


class SentimentResponse(BaseModel):
    """
    Market narrative sentiment.
    """
    ## Finnhub + VADER sourced
    narrative_news_score: Optional[float] = Field(
        None,
        description=(
            "Mean VADER compound score (~[-1, 1]) over analyzed company-news texts "
            "(headline + summary). Null when no articles had usable text after dedupe."
        ),
    )
    narrative_bullish_pct: Optional[float] = Field(
        None,
        description=(
            "Share of scored articles with VADER compound ≥ 0.05 (0–100). "
            "Null when no articles were scored."
        ),
    )
    narrative_bearish_pct: Optional[float] = Field(
        None,
        description=(
            "Share of scored articles with VADER compound ≤ -0.05 (0–100). "
            "Null when no articles were scored."
        ),
    )
    narrative_confidence: float = Field(
        ...,
        description=(
            "0–1 confidence from local aggregation only (not a Finnhub field): "
            "grows with the number of scored articles and is reduced when VADER "
            "compound scores disagree (higher spread across articles)."
        ),
    )
    narrative_status: SentimentStatus = Field(
        ...,
        description=(
            "Quality gate for the VADER-on-company-news portion only: ok, low_data, or noisy "
            "(from article count and compound spread). Other SentimentStatus values are reserved; "
            "Finnhub request failures surface as HTTP 502, not in this field."
        ),
    )
    narrative_fetched_at: str = Field(
        ...,
        description="ISO-8601 timestamp when this sentiment snapshot was assembled (news + analyst trends).",
    )
    narrative_provider: str = Field(
        ...,
        description=(
            "Upstream provider for Finnhub-sourced inputs (company news + analyst recommendation trends); "
            "VADER narrative scores are computed locally from article text."
        ),
    )

    narrative_headline_count: Optional[int] = Field(
        None,
        description=(
            "Count of company-news articles included in VADER scoring after dedupe, "
            "recency ordering, max-articles cap, and dropping rows with no headline/summary text."
        ),
    )
    narrative_headline_distinct_sources: Optional[int] = Field(
        None,
        description="Distinct non-empty `source` values among those scored articles.",
    )
    narrative_headline_sample_titles: Optional[List[str]] = Field(
        None,
        description="Sample headlines from scored articles (newest first); respect Finnhub ToS for display/redistribution.",
    )

    analyst_recommendation_period: Optional[str] = Field(
        None,
        description="Reporting period for the latest row from Finnhub recommendation trends (e.g. month-end date).",
    )
    analyst_recommendation_counts: Optional[AnalystRecommendationCounts] = Field(
        None,
        description="Grouped analyst recommendation counts from the latest Finnhub recommendation row.",
    )
    analyst_recommendation_total: Optional[int] = Field(
        None,
        description="Total analyst ratings in the latest row (sum of strong buy through strong sell).",
    )
    analyst_recommendation_bullish_pct: Optional[float] = Field(
        None,
        description="Share of analysts bullish (strong buy + buy) as 0–100; null if total is zero.",
    )
    analyst_recommendation_bearish_pct: Optional[float] = Field(
        None,
        description="Share of analysts bearish (sell + strong sell) as 0–100; null if total is zero.",
    )
    analyst_recommendation_neutral_pct: Optional[float] = Field(
        None,
        description="Share of analysts neutral (hold) as 0–100; null if total is zero.",
    )
    analyst_recommendation_net_score: Optional[float] = Field(
        None,
        description=(
            "Weighted analyst recommendation score normalized to [-1, 1], where "
            "strong_buy=+2, buy=+1, hold=0, sell=-1, strong_sell=-2."
        ),
    )