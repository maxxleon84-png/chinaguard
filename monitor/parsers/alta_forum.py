from bs4 import BeautifulSoup

from parsers.base import ParsedPost, fetch_html
from keywords import match_keywords

FORUM_URL = "https://forum.alta.ru/viewforum.php?f=1"


async def parse_alta_forum() -> list[ParsedPost]:
    results = []
    html = await fetch_html(FORUM_URL)
    if not html:
        return results

    soup = BeautifulSoup(html, "html.parser")
    topics = soup.find_all("a", class_="topictitle")

    for topic in topics[:30]:
        title = topic.get_text(strip=True)
        link = topic.get("href", "")
        if not link.startswith("http"):
            link = "https://forum.alta.ru/" + link.lstrip("./")

        keyword = match_keywords(title)
        if keyword:
            results.append(ParsedPost(
                platform="alta_forum",
                url=link,
                title=title[:200],
                text=title,
            ))
    return results
