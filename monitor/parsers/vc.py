import feedparser
from bs4 import BeautifulSoup

from parsers.base import ParsedPost, fetch_html
from keywords import match_keywords


async def parse_vc() -> list[ParsedPost]:
    results = []
    html = await fetch_html("https://vc.ru/rss/all")
    if not html:
        return results

    feed = feedparser.parse(html)
    for entry in feed.entries[:50]:
        title = entry.get("title", "")
        summary = entry.get("summary", "")
        link = entry.get("link", "")
        text = f"{title} {summary}"

        keyword = match_keywords(text)
        if keyword:
            results.append(ParsedPost(
                platform="vc.ru",
                url=link,
                title=title[:200],
                text=text[:1000],
            ))
    return results
