import pytest

from app.sentiment.vader_narrative import (
    COMPOUND_BEARISH,
    COMPOUND_BULLISH,
    VaderNarrativeResult,
    analyze_company_news_vader,
)


def _row(
    *,
    headline: str = "",
    summary: str = "",
    source: str = "Reuters",
    dt: int = 0,
    row_id: int | str | None = None,
) -> dict:
    d: dict = {
        "headline": headline,
        "summary": summary,
        "source": source,
        "datetime": dt,
    }
    if row_id is not None:
        d["id"] = row_id
    return d


def test_empty_articles_returns_zeros():
    r = analyze_company_news_vader([])
    assert r == VaderNarrativeResult(
        narrative_news_score=0.0,
        narrative_bullish_pct=0.0,
        narrative_bearish_pct=0.0,
        narrative_headline_count=0,
        narrative_headline_distinct_sources=0,
        narrative_headline_sample_titles=(),
        narrative_confidence=0.0,
        compounds=(),
    )


def test_skips_rows_with_no_usable_text():
    r = analyze_company_news_vader(
        [
            _row(headline="", summary=""),
            _row(headline="   ", summary=""),
        ]
    )
    assert r.narrative_headline_count == 0


def test_dedupes_by_id():
    articles = [
        _row(row_id=1, headline="Apple beats estimates", summary="Strong quarter.", dt=100),
        _row(row_id=1, headline="Duplicate id ignored", summary="Should not count.", dt=200),
        _row(row_id=2, headline="Second story", summary="More news.", dt=50),
    ]
    r = analyze_company_news_vader(articles)
    assert r.narrative_headline_count == 2


def test_dedupes_by_source_and_headline_when_no_id():
    articles = [
        _row(headline="Same headline", summary="A", source="X", dt=10),
        _row(headline="Same headline", summary="B duplicate", source="X", dt=20),
        _row(headline="Other", summary="C", source="X", dt=30),
    ]
    r = analyze_company_news_vader(articles)
    assert r.narrative_headline_count == 2


def test_max_articles_cap():
    articles = [
        _row(headline=f"H{i}", summary="neutral filler text here", dt=i) for i in range(10)
    ]
    r = analyze_company_news_vader(articles, max_articles=3)
    assert r.narrative_headline_count == 3


def test_sample_titles_newest_first_and_limited():
    articles = [
        _row(headline="Old", summary="s", dt=1),
        _row(headline="Mid", summary="s", dt=2),
        _row(headline="New", summary="s", dt=3),
    ]
    r = analyze_company_news_vader(articles, sample_title_limit=2)
    assert list(r.narrative_headline_sample_titles) == ["New", "Mid"]


def test_distinct_sources():
    articles = [
        _row(headline="A", summary="x", source="S1", dt=1),
        _row(headline="B", summary="x", source="S2", dt=2),
        _row(headline="C", summary="x", source="S1", dt=3),
    ]
    r = analyze_company_news_vader(articles)
    assert r.narrative_headline_distinct_sources == 2


def test_positive_batch_skews_positive():
    articles = [
        _row(
            headline="Stock surges on record profits and strong guidance",
            summary="Investors are thrilled with exceptional quarterly results.",
            dt=i,
        )
        for i in range(5)
    ]
    r = analyze_company_news_vader(articles)
    assert r.narrative_news_score > 0.2
    assert r.narrative_bullish_pct >= 80.0
    assert all(c >= COMPOUND_BULLISH for c in r.compounds)


def test_negative_batch_skews_negative():
    articles = [
        _row(
            headline="Company faces massive lawsuit and bleak outlook",
            summary="Losses mount as scandal deepens and shares collapse.",
            dt=i,
        )
        for i in range(5)
    ]
    r = analyze_company_news_vader(articles)
    assert r.narrative_news_score < -0.2
    assert r.narrative_bearish_pct >= 80.0
    assert all(c <= COMPOUND_BEARISH for c in r.compounds)


def test_mixed_batch_has_both_bull_and_bear_shares():
    articles = [
        _row(
            headline="Amazing earnings beat expectations",
            summary="Shares rally on outstanding growth.",
            dt=1,
        ),
        _row(
            headline="Terrible miss and guidance slashed",
            summary="Stock plunges on disappointing results.",
            dt=2,
        ),
    ]
    r = analyze_company_news_vader(articles)
    assert r.narrative_bullish_pct > 0
    assert r.narrative_bearish_pct > 0
    assert -0.5 < r.narrative_news_score < 0.5


def test_confidence_increases_with_more_articles():
    one = analyze_company_news_vader(
        [_row(headline="Solid quarter", summary="Revenue up modestly.", dt=1)]
    )
    many = analyze_company_news_vader(
        [
            _row(headline=f"News {i}", summary="Business update continues as expected.", dt=i)
            for i in range(30)
        ]
    )
    assert many.narrative_confidence > one.narrative_confidence
