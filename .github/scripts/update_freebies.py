#!/usr/bin/env python3
"""抓免費情報站 RSS，合併寫入 data/auto-freebies.json。

去重（以 url 為 key），保留最新 30 筆。供 GitHub Actions 每日執行。
"""
import json
import os

import feedparser

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = os.path.join(REPO, "data", "auto-freebies.json")

FEEDS = {
    "Hip2Save": "https://hip2save.com/category/freebies/feed/",
    "Freeflys": "https://freeflys.com/feed/",
}

MAX_ITEMS = 30


def main():
    old = []
    if os.path.exists(OUT):
        try:
            with open(OUT, encoding="utf-8") as f:
                old = json.load(f)
        except (json.JSONDecodeError, OSError):
            old = []
    seen = {it.get("url") for it in old if it.get("url")}
    items = list(old)

    for source, url in FEEDS.items():
        try:
            d = feedparser.parse(url)
        except Exception as e:  # noqa: BLE001
            print(f"[warn] {source}: fetch failed: {e}")
            continue
        if d.bozo and not d.entries:
            print(f"[warn] {source}: parse failed: {d.bozo_exception}")
            continue
        # entries 是新到舊；反轉後 append 讓整串維持舊到新
        for e in list(d.entries[:30])[::-1]:
            link = (e.get("link") or "").strip()
            title = (e.get("title") or "").strip()
            if not link or not title or link in seen:
                continue
            seen.add(link)
            items.append(
                {
                    "title": title,
                    "url": link,
                    "source": source,
                    "published": e.get("published", ""),
                }
            )

    items = items[-MAX_ITEMS:]
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(items, f, ensure_ascii=False, indent=1)
    print(f"wrote {len(items)} items to {OUT}")


if __name__ == "__main__":
    main()
