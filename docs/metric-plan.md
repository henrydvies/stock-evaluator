## Pricing
price.current
price.change_1d_pct
price.change_1w_pct

## Fundamentals
fundamentals.pe_ttm
fundamentals.pe_forward
fundamentals.market_cap
fundamentals.dividend_yield
fundamentals.return_on_invested_capital
fundamentals.fcf_yield
fundamentals.revenue_growth_5y

## Technical
technical.sma_50d   -   simple moving advantage
technical.sma_200d
technical.above_200d
technical.rsi_14d   -   rsi for past 14 days
technical.volatility_30    -    Standard deviation of the last 30 change in closes

## Sentiment

### Reddit 
sentiment.reddit_score_(7d, 30d) - Net score accross sentiment metrics
sentiment.reddit_confidence(7d, 30d) - confidence in the score quality in 0, 1 range, based on sample size/ relevance.
sentiment.reddit_mentions_(7d, 30d)
sentiment.reddit_sources(7d, 30d) - total sources on the topic (i.e how many posts/ comments checked)
sentiment.reddit_status(7d, 30d) - enum could be like ok, low-data, noisy, amiguous-ticker, stale?

## Scores
scores.overall  -   Attempt at a overall combination score