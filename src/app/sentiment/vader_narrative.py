from __future__ import annotations

from dataclasses import dataclass
from math import log1p
from statistics import mean, stdev
from typing import Any, Mapping, Sequence

from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

_ANALYZER = SentimentIntensityAnalyzer()

# config vals for what counts as bullish v bearish
COMPOUND_BULLISH = 0.05
COMPOUND_BEARISH = -0.05
MAX_TEXT_LEN = 800
N_REF_FOR_CONFIDENCE = 25.0


@dataclass(frozen=True)
class VaderNarrativeResult:
    narrative_news_score: float
    narrative_bullish_pct: float
    narrative_bearish_pct: float
    narrative_headline_count: int
    narrative_headline_distinct_sources: int
    narrative_headline_sample_titles: tuple[str, ...]
    narrative_confidence: float
    compounds: tuple[float, ...]


def _dedupe_key(row: Mapping[str, Any]) -> tuple[str, str] | None:
    raw_id = row.get("id")
    if raw_id is not None and str(raw_id).strip():
        return ("id", str(raw_id).strip())
    src = (row.get("source") or "").strip().casefold()
    hl = (row.get("headline") or "").strip().casefold()
    if not hl and not (row.get("summary") or "").strip():
        return None
    return ("pair", f"{src}\u0000{hl}")


def _dedupe_articles(articles: Sequence[Mapping[str, Any]]) -> list[Mapping[str, Any]]:
    seen: set[tuple[str, str]] = set()
    out: list[Mapping[str, Any]] = []
    for row in articles:
        key = _dedupe_key(row)
        if key is None:
            continue
        if key in seen:
            continue
        seen.add(key)
        out.append(row)
    return out


def _article_datetime(row: Mapping[str, Any]) -> int:
    dt = row.get("datetime")
    if dt is None:
        return 0
    try:
        return int(dt)
    except (TypeError, ValueError):
        return 0


def _article_text(row: Mapping[str, Any], max_len: int = MAX_TEXT_LEN) -> str:
    h = (row.get("headline") or "").strip()
    s = (row.get("summary") or "").strip()
    if h and s:
        t = f"{h}. {s}"
    else:
        t = h or s
    if len(t) > max_len:
        return t[:max_len]
    return t


def _confidence(n: int, compounds: list[float]) -> float:
    if n <= 0:
        return 0.0
    base = min(1.0, log1p(n) / log1p(N_REF_FOR_CONFIDENCE))
    if n == 1:
        spread_factor = 1.0
    else:
        sd = stdev(compounds)
        spread_factor = max(0.3, 1.0 - min(1.0, sd))
    return max(0.0, min(1.0, base * spread_factor))


def analyze_company_news_vader(
    articles: Sequence[Mapping[str, Any]],
    *,
    max_articles: int = 200,
    sample_title_limit: int = 5,
) -> VaderNarrativeResult:
    deduped = _dedupe_articles(articles)
    ordered = sorted(deduped, key=_article_datetime, reverse=True)
    capped = ordered[: max(0, max_articles)]

    texts_and_rows: list[tuple[str, Mapping[str, Any]]] = []
    for row in capped:
        text = _article_text(row)
        if not text:
            continue
        texts_and_rows.append((text, row))

    if not texts_and_rows:
        return VaderNarrativeResult(
            narrative_news_score=0.0,
            narrative_bullish_pct=0.0,
            narrative_bearish_pct=0.0,
            narrative_headline_count=0,
            narrative_headline_distinct_sources=0,
            narrative_headline_sample_titles=(),
            narrative_confidence=0.0,
            compounds=(),
        )

    compounds: list[float] = []
    for text, _ in texts_and_rows:
        scores = _ANALYZER.polarity_scores(text)
        compounds.append(float(scores["compound"]))

    n = len(compounds)
    score = mean(compounds)
    bullish = sum(1 for c in compounds if c >= COMPOUND_BULLISH)
    bearish = sum(1 for c in compounds if c <= COMPOUND_BEARISH)
    bullish_pct = 100.0 * bullish / n
    bearish_pct = 100.0 * bearish / n

    sources = {(row.get("source") or "").strip() for _, row in texts_and_rows if (row.get("source") or "").strip()}
    distinct_sources = len(sources)

    titles: list[str] = []
    limit = max(0, sample_title_limit)
    for _, row in texts_and_rows:
        if limit <= 0:
            break
        hl = (row.get("headline") or "").strip()
        if hl:
            titles.append(hl)
            limit -= 1

    conf = _confidence(n, compounds)

    return VaderNarrativeResult(
        narrative_news_score=score,
        narrative_bullish_pct=bullish_pct,
        narrative_bearish_pct=bearish_pct,
        narrative_headline_count=n,
        narrative_headline_distinct_sources=distinct_sources,
        narrative_headline_sample_titles=tuple(titles),
        narrative_confidence=conf,
        compounds=tuple(compounds),
    )
