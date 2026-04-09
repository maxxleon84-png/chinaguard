from bs4 import BeautifulSoup

from parsers.base import ParsedPost, fetch_html
from keywords import match_keywords

PIKABU_URLS = [
    "https://pikabu.ru/tag/%D0%9A%D0%B8%D1%82%D0%B0%D0%B9",
    "https://pikabu.ru/tag/%D0%92%D0%AD%D0%94",
    "https://pikabu.ru/tag/%D0%91%D0%B8%D0%B7%D0%BD%D0%B5%D1%81",
]


async def parse_pikabu() -> list[ParsedPost]:
    results = []
    for page_url in PIKABU_URLS:
        html = await fetch_html(page_url)
        if not html:
            continue

        soup = BeautifulSoup(html, "html.parser")
        stories = soup.find_all("article", class_="story")

        for story in stories[:20]:
            title_el = story.find("a", class_="story__title-link")
            if not title_el:
                continue

            title = title_el.get_text(strip=True)
            link = title_el.get("href", "")
            if not link.startswith("http"):
                link = "https://pikabu.ru" + link

            content_el = story.find("div", class_="story__content")
            text = content_el.get_text(strip=True)[:500] if content_el else ""
            full_text = f"{title} {text}"

            keyword = match_keywords(full_text)
            if keyword:
                results.append(ParsedPost(
                    platform="pikabu",
                    url=link,
                    title=title[:200],
                    text=full_text[:1000],
                ))
    return results
