from pydantic import BaseModel, Field
from enum import Enum

# Enum for the status of sentiment analysis based of data availability and confidence.
class SentimentStatus(str, Enum):
    OK = "ok"
    LOW_DATA = "low_data"
    NOISY = "noisy"
    AMBIGUOUS_ENTITY = "ambiguous_entity"
    STALE = "stale"
    SOURCE_ERROR = "source_error"

class SentimentResponse(BaseModel):
    ## Reddit Based
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
    
    ## Other sources