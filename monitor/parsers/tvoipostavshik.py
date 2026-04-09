from bs4 import BeautifulSoup

from parsers.base import ParsedPost, fetch_html
from keywords import match_keywords

# Страница новых тем форума поставщиков
NEW_THREADS_URL = "https://forum.tvoipostavshik.ru/find-new/posts"


async def parse_tvoipostavshik() -> list[ParsedPost]:
    """Парсит новые сообщения на Форуме Поставщиков."""
    results = []

    html = await fetch_html(NEW_THREADS_URL)
    if not html:
        return results

    soup = BeautifulSoup(html, "html.parser")

    # XenForo: новые посты
    items = soup.find_all("li", class_="searchResult")
    if not items:
        items = soup.find_all("div", class_="structItem")

    for item in items[:30]:
        title_el = item.find("a", class_="contentTitle") or item.find("a", class_="structItem-title")
        if not title_el:
            title_el = item.find("h3")
            if title_el:
                title_el = title_el.find("a")
        if not title_el:
            continue

        title = title_el.get_text(strip=True)
        link = title_el.get("href", "")
        if not link.startswith("http"):
            link = "https://forum.tvoipostavshik.ru/" + link.lstrip("/")

        snippet_el = item.find("div", class_="contentRow-snippet") or item.find("div", class_="structItem-snippet")
        snippet = snippet_el.get_text(strip=True)[:500] if snippet_el else ""
        full_text = f"{title} {snippet}"

        keyword = match_keywords(full_text)
        if keyword:
            results.append(ParsedPost(
                platform="tvoipostavshik",
                url=link,
                title=title[:200],
                text=full_text[:1000],
            ))

    return results
