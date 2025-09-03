from fastapi import APIRouter, Response
from db import fetch_last_posts
from utils import rfc2822

router = APIRouter()

@router.get("/rss.xml")
async def rss_xml():
    posts = await fetch_last_posts()
    items = []

    for p in posts:
        enclosure = f'\n<enclosure url="{p["lead_image"]}" type="image/jpeg" />' if p["lead_image"] else ""
        items.append(f"""
<item>
  <title>{p['title']}</title>
  <link>{p['link']}</link>
  <guid isPermaLink="false">{p['channel_id']}-{p['id']}</guid>
  <pubDate>{rfc2822(p['date_ts'])}</pubDate>
  <description><![CDATA[{p['content_html']}]]></description>{enclosure}
</item>""")

    xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
<channel>
  <title>NDZONE: Telegram → Dzen</title>
  <link>https://ndzone.ru</link>
  <description>Автоимпорт постов</description>
  {''.join(items)}
</channel>
</rss>"""

    return Response(content=xml, media_type="application/rss+xml; charset=utf-8")
