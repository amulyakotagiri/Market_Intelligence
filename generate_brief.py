#!/usr/bin/env python3
"""
Money Intelligence System – Daily Brief (Real News V1.3)
Short • Live headlines • Fits 4x4 widget • Free
"""

from datetime import datetime
from jugaad_data.nse import NSELive
import feedparser
import traceback

SECTORS = {
    "NIFTY IT": "IT",
    "NIFTY BANK": "Bank",
    "NIFTY PHARMA": "Pharma",
    "NIFTY AUTO": "Auto",
    "NIFTY FMCG": "FMCG",
    "NIFTY METAL": "Metal",
    "NIFTY ENERGY": "Energy",
    "NIFTY REALTY": "Realty",
    "NIFTY FINANCIAL SERVICES": "Financials",
}

REL_THRESHOLD = 1.3

# Free RSS feeds (Moneycontrol)
RSS_FEEDS = [
    "https://www.moneycontrol.com/rss/latestnews.xml",
    "https://www.moneycontrol.com/rss/marketreports.xml",
]

def safe_float(v, default=0.0):
    try:
        return float(v)
    except (TypeError, ValueError):
        return default

def get_indices(nse):
    try:
        raw = nse.all_indices()
        data = {}
        for item in raw.get("data", []):
            name = item.get("index", "")
            data[name] = {
                "last": safe_float(item.get("last")),
                "pchange": safe_float(item.get("percentChange")),
            }
        return data
    except Exception as e:
        print("Index fetch error:", e)
        return {}

def get_top_headlines(max_items=2):
    """Fetch top market-related headlines from free RSS"""
    headlines = []
    keywords = ["bank", "strike", "nifty", "sensex", "rbi", "crude", "yield", "fii", "market", "rate"]

    for url in RSS_FEEDS:
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries[:8]:
                title = entry.get("title", "").strip()
                if not title:
                    continue
                # Prefer market-related headlines
                if any(k in title.lower() for k in keywords):
                    # Keep it short
                    short = title[:70] + "..." if len(title) > 70 else title
                    if short not in headlines:
                        headlines.append(short)
                if len(headlines) >= max_items:
                    return headlines
        except Exception as e:
            print(f"RSS error ({url}):", e)
            continue

    # Fallback if no good headlines found
    if not headlines:
        headlines = ["No major market headlines fetched"]
    return headlines[:max_items]

def build_brief(indices):
    today = datetime.now().strftime("%d %b %Y")
    lines = [f"Money Brief | {today}", ""]

    nifty = indices.get("NIFTY 50", {})
    vix = indices.get("INDIA VIX", {})
    nifty_chg = nifty.get("pchange", 0.0)
    vix_level = vix.get("last", 0.0)
    vix_chg = vix.get("pchange", 0.0)

    # Compact market line
    lines.append(f"Nifty {nifty_chg:+.2f}% | VIX {vix_level:.2f} ({vix_chg:+.1f}%)")

    # Sector dispersion
    notable = []
    for full, short in SECTORS.items():
        sec = indices.get(full)
        if not sec:
            continue
        chg = sec["pchange"]
        rel = chg - nifty_chg
        if abs(rel) >= REL_THRESHOLD:
            notable.append(f"{short} {rel:+.1f}%")

    if notable:
        lines.append("Moves: " + ", ".join(notable[:2]))
    else:
        lines.append("Low dispersion")
    lines.append("")

    # Real headlines
    lines.append("Key drivers")
    headlines = get_top_headlines(2)
    for h in headlines:
        lines.append(f"• {h}")

    lines.append("")
    lines.append("You form the hypothesis.")

    return "\n".join(lines)

def main():
    try:
        nse = NSELive()
        indices = get_indices(nse)
        brief = build_brief(indices) if indices else "Data fetch failed today."
        with open("brief.txt", "w", encoding="utf-8") as f:
            f.write(brief)
        print(brief)
    except Exception:
        err = traceback.format_exc()
        with open("brief.txt", "w", encoding="utf-8") as f:
            f.write("Error generating brief\n" + err)
        raise

if __name__ == "__main__":
    main()
