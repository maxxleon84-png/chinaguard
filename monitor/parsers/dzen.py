from bs4 import BeautifulSoup

from parsers.base import ParsedPost, fetch_html
from keywords import match_keywords

DZEN_SEARCH_QUERIES = [
    "поставщик Китай обманул",
    "ВЭД Китай проблемы",
    "договор с Китаем риски",
    "импорт из Китая брак",
]


async def parse_dzen() -> list[ParsedPost]:
    results = []
    for query in DZEN_SEARCH_QUERIES:
        url = f"https://dzen.ru/search?text={query.replace(' ', '+')}"
        html = await fetch_html(url)
        if not html:
            continue

        soup = BeautifulSoup(html, "html.parser")
        articles = soup.find_all("a", attrs={"data-testid": True})

        for article in articles[:10]:
            title = article.get_text(strip=True)
            link = article.get("href", "")
            if not link.startswith("http"):
                link = "https://dzen.ru" + link

            keyword = match_keywords(title)
            if keyword:
                results.append(ParsedPost(
                    platform="dzen",
                    url=link,
                    title=title[:200],
                    text=title,
                ))
    return results
