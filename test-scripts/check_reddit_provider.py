import asyncio

from app.providers.reddit import AsyncPrawRedditProvider
from dotenv import load_dotenv
load_dotenv()  # add this before the provider import


async def main():
    provider = AsyncPrawRedditProvider()
    mentions = await provider.fetch_mentions("NVDA", lookback_days=30)

    print(f"mentions={len(mentions)}")
    for item in mentions[:5]:
        print(item.subreddit, item.source_type, item.created_utc, item.text)


if __name__ == "__main__":
    asyncio.run(main())