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
    Market narrative sentiment backed primarily by Finnhub.
    """
    ## Reddit Based
    """
    reddit_score_7d: float = Field(..., description="Average sentiment score from Reddit posts mentioning the stock over the past 7 days.")
    reddit_score_30d: float = Field(..., description="Average sentiment score from Reddit posts mentioning the stock over the past 30 days.")
    reddit_confidence_7d: float = Field(..., description="Confidence level of the Reddit sentiment score over the past 7 days.")
    reddit_confidence_30d: float = Field(..., description="Confidence level of the Reddit sentiment score over the past 30 days.")
    reddit_mentions_7d: int = Field(..., description="Number of mentions of the stock on Reddit over the past 7 days.")
    reddit_mentions_30d: int = Field(..., description="Number of mentions of the stock on Reddit over the past 30 days.")
    reddit_sources_7d: int = Field(..., description="Number of unique Reddit sources mentioning the stock over the past 7 days.")
    reddit_sources_30d: int = Field(..., description="Number of unique Reddit sources mentioning the stock over the past 30 days.")
    reddit_status_7d: SentimentStatus = Field(..., description="Status of the Reddit sentiment analysis over the past 7 days.")
    reddit_status_30d: SentimentStatus = Field(..., description="Status of the Reddit sentiment analysis over the past 30 days.")
    """

    ## Finnhub based
    narrative_news_score: float = Field(
        ...,
        description="Normalized composite news sentiment for the company (~[-1, 1] or [0, 1]; map from Finnhub companyNewsScore and document scale in service code).",
    )
    narrative_bullish_pct: float = Field(
        ...,
        description="Share of sampled company news classified bullish (from Finnhub sentiment object; 0–100).",
    )
    narrative_bearish_pct: float = Field(
        ...,
        description="Share of sampled company news classified bearish (from Finnhub sentiment object; 0–100).",
    )
    narrative_buzz: float = Field(
        ...,
        description="Normalized attention / buzz index from Finnhub buzz metrics (exact formula in service; higher = more news flow vs baseline).",
    )
    narrative_article_count_proxy: int = Field(
        ...,
        description="Proxy for volume of recent company news (e.g. articles-in-window from Finnhub buzz or related fields).",
    )
    narrative_sector_news_score: Optional[float] = Field(
        None,
        description="Sector average news score from Finnhub when provided; for relative context.",
    )
    narrative_vs_sector_news_score: Optional[float] = Field(
        None,
        description="Derived gap between company and sector narrative (e.g. company score minus sector average).",
    )

    narrative_confidence: float = Field(
        ...,
        description="0–1 confidence in narrative fields; rises with article volume/buzz, falls when ambiguous or sparse.",
    )
    narrative_status: SentimentStatus = Field(
        ...,
        description="Quality gate for narrative data (ok, low_data, noisy, source_error, etc.).",
    )
    narrative_fetched_at: str = Field(
        ...,
        description="ISO-8601 timestamp when narrative data was fetched from the provider.",
    )
    narrative_provider: str = Field(
        ...,
        description="Identifier for upstream provider (e.g. finnhub).",
    )


    narrative_headline_count: Optional[int] = Field(
        None,
        description="Number of company-news items returned for the requested window; strengthens confidence when high.",
    )
    narrative_headline_distinct_sources: Optional[int] = Field(
        None,
        description="Count of distinct news sources in that window when derivable from company-news payload.",
    )
    narrative_headline_sample_titles: Optional[List[str]] = Field(
        None,
        description="Up to N recent headlines for context or debugging; omit or empty if ToS/display rules forbid redistribution.",
    )

    social_bullish_pct: Optional[float] = Field(
        None,
        description="From stock/social-sentiment: bullish share or analogous metric (0–100) when the API provides it.",
    )
    social_bearish_pct: Optional[float] = Field(
        None,
        description="From stock/social-sentiment: bearish share or analogous metric (0–100) when the API provides it.",
    )
    social_attention_score: Optional[float] = Field(
        None,
        description="From stock/social-sentiment: normalized volume/attention when available (platform-dependent).",
    )
    social_net_score: Optional[float] = Field(
        None,
        description="Derived single scalar from social sentiment payload (~[-1, 1]); null if insufficient data.",
    )
    narrative_social_divergence: Optional[float] = Field(
        None,
        description="Optional derived gap between news tilt and social tilt; large absolute values flag media vs crowd mismatch.",
    )
