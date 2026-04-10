import asyncio
import json

from dotenv import load_dotenv

load_dotenv()

from app.providers.finnhub_client import (
    FinnhubForbiddenError,
    HttpFinnhubClient,
    default_company_news_window,
)


async def main():
    symbol = "AAPL"
    client = HttpFinnhubClient()

    date_from, date_to = default_company_news_window(days=7)

    print(f"symbol={symbol}")
    print("--- stock/recommendation (analyst trends) ---")
    try:
        recs = await client.fetch_recommendation_trends(symbol)
        print(f"periods={len(recs)}")
        for row in recs[:3]:
            print(json.dumps(row, indent=2, default=str))
    except FinnhubForbiddenError as e:
        print(f"skipped: {e}")

    print("\n--- company-news (GET /company-news) ---")
    headlines = await client.fetch_company_news(symbol, date_from, date_to)
    print(f"count={len(headlines)}")
    for item in headlines[:3]:
        print(json.dumps(item, indent=2, default=str))


if __name__ == "__main__":
    asyncio.run(main())
