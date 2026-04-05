import asyncio

from app.providers.reddit import AsyncPrawRedditProvider


async def main():
    provider = AsyncPrawRedditProvider()
    mentions = await provider.fetch_mentions("AAPL", lookback_days=7, limit=20)

    print(f"mentions={len(mentions)}")
    for item in mentions[:5]:
        print(item.subreddit, item.source_type, item.created_utc, item.text)


if __name__ == "__main__":
    asyncio.run(main())