import aiosqlite
from pathlib import Path

DB_PATH = Path("data/posts.db")
DB_PATH.parent.mkdir(exist_ok=True, parents=True)

INIT_SQL = """
CREATE TABLE IF NOT EXISTS posts (
    id INTEGER PRIMARY KEY,
    channel_id INTEGER NOT NULL,
    date_ts INTEGER NOT NULL,
    title TEXT NOT NULL,
    link TEXT NOT NULL,
    content_html TEXT NOT NULL,
    lead_image TEXT,
    created_at INTEGER DEFAULT (strftime('%s','now'))
);
"""

async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.executescript(INIT_SQL)
        await db.commit()

async def upsert_post(id, channel_id, date_ts, title, link, content_html, lead_image):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            INSERT INTO posts (id, channel_id, date_ts, title, link, content_html, lead_image)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(id) DO NOTHING
        """, (id, channel_id, date_ts, title, link, content_html, lead_image))
        await db.commit()

async def fetch_last_posts(limit=50):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cur = await db.execute("SELECT * FROM posts ORDER BY date_ts DESC LIMIT ?", (limit,))
        return await cur.fetchall()
