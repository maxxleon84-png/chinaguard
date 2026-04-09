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
