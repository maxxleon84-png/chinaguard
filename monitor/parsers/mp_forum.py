from bs4 import BeautifulSoup

from parsers.base import ParsedPost, fetch_html
from keywords import match_keywords

# Страница новых тем форума маркетплейсов
NEW_THREADS_URL = "https://mp-forum.ru/whats-new/posts/"


async def parse_mp_forum() -> list[ParsedPost]:
    """Парсит новые сообщения на Форуме продавцов маркетплейсов."""
    results = []

    html = await fetch_html(NEW_THREADS_URL)
    if not html:
        return results

    soup = BeautifulSoup(html, "html.parser")

    # XenForo: новые посты
    items = soup.find_all("div", class_="structItem")

    for item in items[:30]:
        title_el = item.find("a", attrs={"data-tp-primary": "on"})
        if not title_el:
            title_el = item.find("a", class_="structItem-title")
        if not title_el:
            continue

        title = title_el.get_text(strip=True)
        link = title_el.get("href", "")
        if not link.startswith("http"):
            link = "https://mp-forum.ru" + link

        snippet_el = item.find("div", class_="structItem-snippet")
        snippet = snippet_el.get_text(strip=True)[:500] if snippet_el else ""
        full_text = f"{title} {snippet}"

        keyword = match_keywords(full_text)
        if keyword:
            results.append(ParsedPost(
                platform="mp_forum",
                url=link,
                title=title[:200],
                text=full_text[:1000],
            ))

    return results
