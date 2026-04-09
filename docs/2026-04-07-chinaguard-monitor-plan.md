# ChinaGuard Monitor — План реализации

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Построить бота-мониторинга, который парсит 5 площадок по 60 ключевым словам, генерирует AI-черновики ответов и присылает уведомления в Telegram.

**Architecture:** Python asyncio приложение — парсеры (requests + BeautifulSoup) проверяют площадки каждые 30 мин, Telethon слушает Telegram-чаты в реальном времени, AITunnel генерирует черновики, aiogram-бот присылает уведомления админу с inline-кнопками.

**Tech Stack:** Python 3.11+, aiogram 3, aiohttp, BeautifulSoup4, feedparser, Telethon, aiosqlite, AITunnel API (GPT-4o mini).

---

## Файловая структура

```
chinaguard/
└── monitor/
    ├── main.py              # Точка входа: запуск бота + планировщик + Telethon
    ├── config.py            # Конфигурация из env
    ├── keywords.py          # Список ключевых слов + функция проверки совпадения
    ├── db.py                # SQLite: таблица posts, CRUD, дедупликация
    ├── ai.py                # Генерация черновиков через AITunnel
    ├── bot.py               # Telegram-бот: уведомления + кнопки + команды
    ├── parsers/
    │   ├── __init__.py      # Экспорт всех парсеров
    │   ├── base.py          # Базовый класс парсера
    │   ├── vc.py            # Парсер vc.ru
    │   ├── pikabu.py        # Парсер Pikabu
    │   ├── alta_forum.py    # Парсер forum.alta.ru
    │   ├── dzen.py          # Парсер Дзен
    │   └── telegram_chats.py # Слушатель Telegram-чатов (Telethon)
    └── requirements.txt
```

---

### Task 1: Конфигурация и зависимости

**Files:**
- Create: `chinaguard/monitor/config.py`
- Create: `chinaguard/monitor/requirements.txt`

- [ ] **Step 1: Создать директорию и __init__**

```bash
mkdir -p C:/Users/DEXP/chinaguard/monitor/parsers
touch C:/Users/DEXP/chinaguard/monitor/parsers/__init__.py
```

- [ ] **Step 2: Создать requirements.txt**

Создать `chinaguard/monitor/requirements.txt`:
```
aiogram==3.4.1
aiosqlite==0.20.0
aiohttp==3.9.5
beautifulsoup4==4.12.3
feedparser==6.0.11
Telethon==1.36.0
```

- [ ] **Step 3: Создать config.py**

Создать `chinaguard/monitor/config.py`:
```python
import os

# Бот-мониторинг (отдельный от ChinaGuard)
MONITOR_BOT_TOKEN = os.environ.get("MONITOR_BOT_TOKEN", "")
ADMIN_ID = int(os.environ.get("CHINAGUARD_ADMIN_ID", "0"))

# AITunnel
AITUNNEL_API_KEY = os.environ.get("AITUNNEL_API_KEY", "")
AITUNNEL_BASE_URL = "https://api.aitunnel.ru/v1"
AI_MODEL = "openai/gpt-4o-mini"

# Telethon (для мониторинга Telegram-чатов)
TELEGRAM_API_ID = int(os.environ.get("TELEGRAM_API_ID", "0"))
TELEGRAM_API_HASH = os.environ.get("TELEGRAM_API_HASH", "")

# Интервал проверки (секунды)
CHECK_INTERVAL = 1800  # 30 минут

# Путь к БД
DB_PATH = os.path.join(os.path.dirname(__file__), "monitor.db")
```

- [ ] **Step 4: Коммит**

```bash
cd C:/Users/DEXP/chinaguard
git add monitor/
git commit -m "feat(monitor): project structure and config"
```

---

### Task 2: Ключевые слова

**Files:**
- Create: `chinaguard/monitor/keywords.py`

- [ ] **Step 1: Создать модуль ключевых слов**

Создать `chinaguard/monitor/keywords.py`:
```python
KEYWORDS = [
    # 1. Обман и мошенничество
    "обманули китайский поставщик",
    "кинули китайцы",
    "мошенники из Китая",
    "поставщик пропал с предоплатой",
    "фейковая фабрика Китай",
    "подделка документов Китай",
    "несуществующий завод Китай",
    "развод китайский поставщик",
    "схема обмана поставщик Китай",
    # 2. Проблемы с качеством
    "брак из Китая что делать",
    "товар не соответствует образцу",
    "приехал не тот товар из Китая",
    "рекламация китайскому поставщику",
    "дефект товар Китай",
    "несоответствие качества Китай",
    "возврат бракованного товара Китай",
    "инспекция товара Китай",
    # 3. Договоры и контракты
    "договор с Китаем",
    "контракт китайский поставщик",
    "договор поставки Китай риски",
    "арбитражная оговорка Китай",
    "как составить контракт с Китаем",
    "условия договора КНР",
    "проверить договор с Китаем",
    "внешнеторговый контракт Китай",
    # 4. Правовые вопросы
    "ГК КНР",
    "китайское право",
    "арбитраж КНР",
    "спор с китайским партнером",
    "суд в Китае",
    "CIETAC",
    "иск к китайской компании",
    "взыскание долга Китай",
    "форс-мажор китайское право",
    "изменение обстоятельств ГК КНР",
    # 5. ВЭД и таможня
    "ВЭД Китай проблемы",
    "таможня задержала груз из Китая",
    "сертификация товара из Китая",
    "таможенное оформление Китай",
    "валютный контроль Китай",
    "оплата юань проблемы",
    "перевод денег Китай",
    "платёж поставщику Китай",
    # 6. Маркетплейсы и селлеры
    "wildberries поставщик Китай",
    "ozon закупка Китай",
    "селлер Китай проблемы",
    "закупка товара 1688",
    "alibaba обман возврат",
    "1688 кинули",
    "поставщик 1688 обманул",
    "импорт для маркетплейса",
    # 7. Проверка контрагента
    "проверить китайскую компанию",
    "проверка контрагента Китай",
    "надёжность поставщика Китай",
    "как проверить фабрику в Китае",
    "верификация поставщика КНР",
    "due diligence Китай",
]


def match_keywords(text: str) -> str | None:
    """Проверяет текст на совпадение с ключевыми словами.
    Возвращает первое совпавшее ключевое слово или None."""
    text_lower = text.lower()
    for kw in KEYWORDS:
        if kw.lower() in text_lower:
            return kw
    return None
```

- [ ] **Step 2: Проверить импорт**

```bash
cd C:/Users/DEXP/chinaguard/monitor
python -c "from keywords import match_keywords; print(match_keywords('Меня обманули китайский поставщик'))"
```

Expected: `обманули китайский поставщик`

- [ ] **Step 3: Коммит**

```bash
cd C:/Users/DEXP/chinaguard
git add monitor/keywords.py
git commit -m "feat(monitor): 60 keywords with match function"
```

---

### Task 3: База данных

**Files:**
- Create: `chinaguard/monitor/db.py`

- [ ] **Step 1: Создать модуль базы данных**

Создать `chinaguard/monitor/db.py`:
```python
import aiosqlite
from config import DB_PATH


async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS posts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                platform TEXT NOT NULL,
                post_url TEXT UNIQUE NOT NULL,
                title TEXT,
                matched_keyword TEXT,
                draft_response TEXT,
                status TEXT NOT NULL DEFAULT 'new',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        await db.commit()


async def post_exists(post_url: str) -> bool:
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "SELECT 1 FROM posts WHERE post_url = ?", (post_url,)
        )
        return await cursor.fetchone() is not None


async def save_post(platform: str, post_url: str, title: str,
                    matched_keyword: str, draft_response: str) -> int:
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            """INSERT INTO posts (platform, post_url, title, matched_keyword, draft_response)
               VALUES (?, ?, ?, ?, ?)""",
            (platform, post_url, title, matched_keyword, draft_response)
        )
        await db.commit()
        return cursor.lastrowid


async def update_post_status(post_id: int, status: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "UPDATE posts SET status = ? WHERE id = ?", (status, post_id)
        )
        await db.commit()


async def get_stats() -> dict:
    async with aiosqlite.connect(DB_PATH) as db:
        stats = {}
        for period, sql in [
            ("today", "SELECT COUNT(*) FROM posts WHERE date(created_at) = date('now')"),
            ("week", "SELECT COUNT(*) FROM posts WHERE created_at >= datetime('now', '-7 days')"),
            ("month", "SELECT COUNT(*) FROM posts WHERE created_at >= datetime('now', '-30 days')"),
            ("total", "SELECT COUNT(*) FROM posts"),
        ]:
            cursor = await db.execute(sql)
            row = await cursor.fetchone()
            stats[period] = row[0]
        return stats
```

- [ ] **Step 2: Коммит**

```bash
cd C:/Users/DEXP/chinaguard
git add monitor/db.py
git commit -m "feat(monitor): SQLite database with deduplication"
```

---

### Task 4: AI-генерация черновиков

**Files:**
- Create: `chinaguard/monitor/ai.py`

- [ ] **Step 1: Создать модуль AI**

Создать `chinaguard/monitor/ai.py`:
```python
import aiohttp
from config import AITUNNEL_API_KEY, AITUNNEL_BASE_URL, AI_MODEL

SYSTEM_PROMPT = """Ты — эксперт по китайскому праву и ВЭД. Ты помогаешь российским предпринимателям решать проблемы с китайскими партнёрами.

Человек написал на форуме/в чате:
"{post_text}"

Напиши экспертный комментарий (3-5 предложений):
1. Кратко квалифицируй ситуацию по ГК КНР (укажи конкретную статью)
2. Дай практическую рекомендацию
3. Заверши фразой: "Для детальной проверки вашей ситуации — @chinaguard_bot"

Тон: профессиональный, уверенный, без воды. Не используй эмодзи. Пиши на русском."""


async def generate_draft(post_text: str) -> str:
    """Генерирует черновик экспертного ответа через AITunnel."""
    prompt = SYSTEM_PROMPT.replace("{post_text}", post_text[:1000])

    headers = {
        "Authorization": f"Bearer {AITUNNEL_API_KEY}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": AI_MODEL,
        "messages": [
            {"role": "system", "content": prompt},
            {"role": "user", "content": post_text[:1000]},
        ],
        "max_tokens": 500,
        "temperature": 0.7,
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{AITUNNEL_BASE_URL}/chat/completions",
                headers=headers,
                json=payload,
                timeout=aiohttp.ClientTimeout(total=30),
            ) as resp:
                if resp.status != 200:
                    error = await resp.text()
                    return f"[Ошибка AI: {resp.status}] {error[:200]}"
                data = await resp.json()
                return data["choices"][0]["message"]["content"]
    except Exception as e:
        return f"[Ошибка AI: {e}]"
```

- [ ] **Step 2: Коммит**

```bash
cd C:/Users/DEXP/chinaguard
git add monitor/ai.py
git commit -m "feat(monitor): AI draft generation via AITunnel"
```

---

### Task 5: Базовый парсер

**Files:**
- Create: `chinaguard/monitor/parsers/base.py`

- [ ] **Step 1: Создать базовый класс парсера**

Создать `chinaguard/monitor/parsers/base.py`:
```python
import aiohttp
from dataclasses import dataclass


@dataclass
class ParsedPost:
    platform: str
    url: str
    title: str
    text: str


async def fetch_html(url: str, timeout: int = 15) -> str:
    """Загружает HTML страницы."""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept-Language": "ru-RU,ru;q=0.9",
    }
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                url, headers=headers, timeout=aiohttp.ClientTimeout(total=timeout)
            ) as resp:
                if resp.status == 200:
                    return await resp.text()
    except Exception:
        pass
    return ""
```

- [ ] **Step 2: Коммит**

```bash
cd C:/Users/DEXP/chinaguard
git add monitor/parsers/base.py
git commit -m "feat(monitor): base parser with fetch_html"
```

---

### Task 6: Парсер vc.ru

**Files:**
- Create: `chinaguard/monitor/parsers/vc.py`

- [ ] **Step 1: Создать парсер vc.ru**

Создать `chinaguard/monitor/parsers/vc.py`:
```python
import feedparser
from bs4 import BeautifulSoup

from parsers.base import ParsedPost, fetch_html
from keywords import match_keywords


async def parse_vc() -> list[ParsedPost]:
    """Парсит vc.ru через RSS-ленту и поиск по ключевым словам."""
    results = []

    # RSS-лента последних публикаций
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
```

- [ ] **Step 2: Коммит**

```bash
cd C:/Users/DEXP/chinaguard
git add monitor/parsers/vc.py
git commit -m "feat(monitor): vc.ru parser via RSS"
```

---

### Task 7: Парсер Pikabu

**Files:**
- Create: `chinaguard/monitor/parsers/pikabu.py`

- [ ] **Step 1: Создать парсер Pikabu**

Создать `chinaguard/monitor/parsers/pikabu.py`:
```python
from bs4 import BeautifulSoup

from parsers.base import ParsedPost, fetch_html
from keywords import match_keywords

PIKABU_URLS = [
    "https://pikabu.ru/tag/%D0%9A%D0%B8%D1%82%D0%B0%D0%B9",  # тег Китай
    "https://pikabu.ru/tag/%D0%92%D0%AD%D0%94",  # тег ВЭД
    "https://pikabu.ru/tag/%D0%91%D0%B8%D0%B7%D0%BD%D0%B5%D1%81",  # тег Бизнес
]


async def parse_pikabu() -> list[ParsedPost]:
    """Парсит новые посты на Pikabu по тегам."""
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
```

- [ ] **Step 2: Коммит**

```bash
cd C:/Users/DEXP/chinaguard
git add monitor/parsers/pikabu.py
git commit -m "feat(monitor): Pikabu parser by tags"
```

---

### Task 8: Парсер forum.alta.ru

**Files:**
- Create: `chinaguard/monitor/parsers/alta_forum.py`

- [ ] **Step 1: Создать парсер таможенного форума**

Создать `chinaguard/monitor/parsers/alta_forum.py`:
```python
from bs4 import BeautifulSoup

from parsers.base import ParsedPost, fetch_html
from keywords import match_keywords

FORUM_URL = "https://forum.alta.ru/viewforum.php?f=1"


async def parse_alta_forum() -> list[ParsedPost]:
    """Парсит новые темы на таможенном форуме Альта-Софт."""
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
```

- [ ] **Step 2: Коммит**

```bash
cd C:/Users/DEXP/chinaguard
git add monitor/parsers/alta_forum.py
git commit -m "feat(monitor): forum.alta.ru parser"
```

---

### Task 9: Парсер Дзен

**Files:**
- Create: `chinaguard/monitor/parsers/dzen.py`

- [ ] **Step 1: Создать парсер Дзен**

Создать `chinaguard/monitor/parsers/dzen.py`:
```python
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
    """Парсит статьи Дзен через поисковую выдачу."""
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
```

- [ ] **Step 2: Коммит**

```bash
cd C:/Users/DEXP/chinaguard
git add monitor/parsers/dzen.py
git commit -m "feat(monitor): Dzen search parser"
```

---

### Task 10: Слушатель Telegram-чатов (Telethon)

**Files:**
- Create: `chinaguard/monitor/parsers/telegram_chats.py`

- [ ] **Step 1: Создать слушатель Telegram-чатов**

Создать `chinaguard/monitor/parsers/telegram_chats.py`:
```python
from telethon import TelegramClient, events
from keywords import match_keywords
from config import TELEGRAM_API_ID, TELEGRAM_API_HASH

# Список чатов для мониторинга (добавлять по мере нахождения)
# Можно указывать username или ID чата
MONITORED_CHATS = [
    # Примеры — заменить на реальные после поиска чатов:
    # "ved_china_chat",
    # "sellers_wb_china",
    # -1001234567890,
]

client = TelegramClient(
    "monitor_session",
    TELEGRAM_API_ID,
    TELEGRAM_API_HASH,
)


def setup_telegram_listener(on_match_callback):
    """Настраивает слушатель Telegram-чатов.
    
    on_match_callback(platform, url, title, text) — вызывается при совпадении.
    """
    if not TELEGRAM_API_ID or not TELEGRAM_API_HASH:
        print("Telethon: API_ID/API_HASH не заданы, Telegram-мониторинг отключён")
        return None

    if not MONITORED_CHATS:
        print("Telethon: нет чатов для мониторинга, пропускаем")
        return None

    @client.on(events.NewMessage(chats=MONITORED_CHATS))
    async def handler(event):
        text = event.message.text or ""
        if not text or len(text) < 20:
            return

        keyword = match_keywords(text)
        if keyword:
            chat = await event.get_chat()
            chat_name = getattr(chat, "title", "Telegram")
            msg_link = f"https://t.me/c/{chat.id}/{event.message.id}"

            await on_match_callback(
                platform=f"telegram:{chat_name}",
                url=msg_link,
                title=text[:100],
                text=text[:1000],
                keyword=keyword,
            )

    return client
```

- [ ] **Step 2: Коммит**

```bash
cd C:/Users/DEXP/chinaguard
git add monitor/parsers/telegram_chats.py
git commit -m "feat(monitor): Telegram chat listener via Telethon"
```

---

### Task 11: Экспорт парсеров

**Files:**
- Modify: `chinaguard/monitor/parsers/__init__.py`

- [ ] **Step 1: Обновить __init__.py**

Записать в `chinaguard/monitor/parsers/__init__.py`:
```python
from parsers.vc import parse_vc
from parsers.pikabu import parse_pikabu
from parsers.alta_forum import parse_alta_forum
from parsers.dzen import parse_dzen
from parsers.telegram_chats import setup_telegram_listener

ALL_PARSERS = [
    parse_vc,
    parse_pikabu,
    parse_alta_forum,
    parse_dzen,
]
```

- [ ] **Step 2: Коммит**

```bash
cd C:/Users/DEXP/chinaguard
git add monitor/parsers/__init__.py
git commit -m "feat(monitor): export all parsers"
```

---

### Task 12: Telegram-бот уведомлений

**Files:**
- Create: `chinaguard/monitor/bot.py`

- [ ] **Step 1: Создать бота уведомлений**

Создать `chinaguard/monitor/bot.py`:
```python
import asyncio
from aiogram import Bot, Dispatcher, Router, F
from aiogram.types import (
    Message, CallbackQuery,
    InlineKeyboardMarkup, InlineKeyboardButton,
)
from aiogram.filters import Command

from config import MONITOR_BOT_TOKEN, ADMIN_ID
from db import update_post_status, get_stats

router = Router()
bot = Bot(token=MONITOR_BOT_TOKEN) if MONITOR_BOT_TOKEN else None
dp = Dispatcher()
dp.include_router(router)

# Состояние паузы
_paused = False


async def send_notification(post_id: int, platform: str, url: str,
                            title: str, draft: str):
    """Отправляет уведомление админу о найденном посте."""
    if not bot or _paused:
        return

    text = (
        f"📌 {platform} — новый пост\n"
        f"━━━━━━━━━━━━━━━━━━\n\n"
        f"{title[:300]}\n\n"
        f"🔗 {url}\n\n"
        f"💬 Черновик ответа:\n"
        f"{draft[:800]}"
    )

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="📋 Скопировать ответ",
                callback_data=f"copy:{post_id}",
            ),
            InlineKeyboardButton(
                text="⏭ Пропустить",
                callback_data=f"skip:{post_id}",
            ),
        ]
    ])

    await bot.send_message(ADMIN_ID, text, reply_markup=keyboard)


@router.callback_query(F.data.startswith("copy:"))
async def on_copy(callback: CallbackQuery):
    post_id = int(callback.data.split(":")[1])
    # Извлекаем черновик из текста сообщения
    msg_text = callback.message.text or ""
    draft_start = msg_text.find("💬 Черновик ответа:\n")
    if draft_start != -1:
        draft = msg_text[draft_start + len("💬 Черновик ответа:\n"):]
        await callback.message.answer(f"```\n{draft}\n```", parse_mode="Markdown")
    await update_post_status(post_id, "copied")
    await callback.answer("Черновик отправлен для копирования")


@router.callback_query(F.data.startswith("skip:"))
async def on_skip(callback: CallbackQuery):
    post_id = int(callback.data.split(":")[1])
    await update_post_status(post_id, "skipped")
    await callback.answer("Пропущено")
    await callback.message.edit_reply_markup(reply_markup=None)


@router.message(Command("stats"))
async def cmd_stats(message: Message):
    if message.from_user.id != ADMIN_ID:
        return
    stats = await get_stats()
    await message.answer(
        f"📊 Статистика мониторинга\n\n"
        f"Сегодня: {stats['today']}\n"
        f"За неделю: {stats['week']}\n"
        f"За месяц: {stats['month']}\n"
        f"Всего: {stats['total']}"
    )


@router.message(Command("pause"))
async def cmd_pause(message: Message):
    if message.from_user.id != ADMIN_ID:
        return
    global _paused
    _paused = True
    await message.answer("⏸ Мониторинг приостановлен. /resume для продолжения.")


@router.message(Command("resume"))
async def cmd_resume(message: Message):
    if message.from_user.id != ADMIN_ID:
        return
    global _paused
    _paused = False
    await message.answer("▶️ Мониторинг возобновлён.")


@router.message(Command("keywords"))
async def cmd_keywords(message: Message):
    if message.from_user.id != ADMIN_ID:
        return
    from keywords import KEYWORDS
    chunks = [KEYWORDS[i:i+15] for i in range(0, len(KEYWORDS), 15)]
    for chunk in chunks:
        text = "\n".join(f"• {kw}" for kw in chunk)
        await message.answer(text)


def is_paused() -> bool:
    return _paused
```

- [ ] **Step 2: Коммит**

```bash
cd C:/Users/DEXP/chinaguard
git add monitor/bot.py
git commit -m "feat(monitor): notification bot with inline buttons and commands"
```

---

### Task 13: Точка входа (main.py)

**Files:**
- Create: `chinaguard/monitor/main.py`

- [ ] **Step 1: Создать main.py**

Создать `chinaguard/monitor/main.py`:
```python
import asyncio
import logging
import sys

from config import MONITOR_BOT_TOKEN, CHECK_INTERVAL, TELEGRAM_API_ID
from db import init_db, post_exists, save_post
from ai import generate_draft
from bot import bot, dp, send_notification, is_paused
from parsers import ALL_PARSERS, setup_telegram_listener

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    stream=sys.stdout,
)
log = logging.getLogger(__name__)


async def check_platforms():
    """Проверяет все площадки и отправляет уведомления."""
    if is_paused():
        return

    for parser_fn in ALL_PARSERS:
        try:
            posts = await parser_fn()
            log.info(f"{parser_fn.__name__}: найдено {len(posts)} совпадений")

            for post in posts:
                if await post_exists(post.url):
                    continue

                draft = await generate_draft(post.text)

                from keywords import match_keywords
                keyword = match_keywords(post.text) or "—"

                post_id = await save_post(
                    platform=post.platform,
                    post_url=post.url,
                    title=post.title,
                    matched_keyword=keyword,
                    draft_response=draft,
                )

                await send_notification(
                    post_id=post_id,
                    platform=post.platform,
                    url=post.url,
                    title=post.title,
                    draft=draft,
                )

                await asyncio.sleep(1)  # пауза между уведомлениями

        except Exception as e:
            log.error(f"Ошибка в {parser_fn.__name__}: {e}")


async def scheduler():
    """Запускает проверку площадок каждые CHECK_INTERVAL секунд."""
    while True:
        log.info("Запуск проверки площадок...")
        await check_platforms()
        log.info(f"Следующая проверка через {CHECK_INTERVAL // 60} мин")
        await asyncio.sleep(CHECK_INTERVAL)


async def on_telegram_match(platform: str, url: str, title: str,
                            text: str, keyword: str):
    """Callback для Telethon — вызывается при совпадении в Telegram-чатах."""
    if is_paused():
        return
    if await post_exists(url):
        return

    draft = await generate_draft(text)
    post_id = await save_post(
        platform=platform,
        post_url=url,
        title=title,
        matched_keyword=keyword,
        draft_response=draft,
    )
    await send_notification(
        post_id=post_id,
        platform=platform,
        url=url,
        title=title,
        draft=draft,
    )


async def main():
    if not MONITOR_BOT_TOKEN:
        print("ERROR: Set MONITOR_BOT_TOKEN environment variable")
        sys.exit(1)

    await init_db()
    log.info("ChinaGuard Monitor started")

    # Запускаем Telethon если настроен
    telethon_client = setup_telegram_listener(on_telegram_match)
    if telethon_client:
        await telethon_client.start()
        log.info("Telethon: подключён к Telegram-чатам")

    # Запускаем планировщик и бота параллельно
    await asyncio.gather(
        scheduler(),
        dp.start_polling(bot),
    )


if __name__ == "__main__":
    asyncio.run(main())
```

- [ ] **Step 2: Проверить что запускается (ожидаем ошибку без токена)**

```bash
cd C:/Users/DEXP/chinaguard/monitor
python main.py
```

Expected: `ERROR: Set MONITOR_BOT_TOKEN environment variable`

- [ ] **Step 3: Коммит**

```bash
cd C:/Users/DEXP/chinaguard
git add monitor/main.py
git commit -m "feat(monitor): main entry point with scheduler and Telethon"
```

---

### Task 14: Финальная проверка

- [ ] **Step 1: Проверить структуру файлов**

```bash
cd C:/Users/DEXP/chinaguard
find monitor/ -type f | sort
```

Expected:
```
monitor/ai.py
monitor/bot.py
monitor/config.py
monitor/db.py
monitor/keywords.py
monitor/main.py
monitor/parsers/__init__.py
monitor/parsers/alta_forum.py
monitor/parsers/base.py
monitor/parsers/dzen.py
monitor/parsers/pikabu.py
monitor/parsers/telegram_chats.py
monitor/parsers/vc.py
monitor/requirements.txt
```

- [ ] **Step 2: Пуш на GitHub**

```bash
cd C:/Users/DEXP/chinaguard
git push origin master
```
