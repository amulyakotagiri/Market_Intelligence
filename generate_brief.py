#!/usr/bin/env python3
"""
Money Intelligence System – Daily Brief (Accurate News V1.4)
Short • Better live headlines • Fits 4x4 widget
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

# Better free RSS sources
RSS_FEEDS = [
    "https://www.moneycontrol.com/rss/latestnews.xml",
    "https://www.moneycontrol.com/rss/marketreports.xml",
    "https://economictimes.indiatimes.com/markets/rssfeeds/1977021501.cms",
]

# Strong market-related keywords
KEYWORDS = [
    "crude", "oil", "brent", "yield", "bond", "fii", "fpi", "foreign",
    "rbi", "rate", "inflation", "geopolitic", "iran", "us-", "trump",
    "strike", "bank", "nifty", "sensex", "market", "rupee", "dollar"
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
    """Fetch relevant market headlines"""
    headlines = []
    seen = set()

    for url in RSS_FEEDS:
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries[:12]:
                title = entry.get("title", "").strip()
                if not title:
                    continue

                title_lower = title.lower()
                if any(k in title_lower for k in KEYWORDS):
                    # Keep short
                    short = title[:65] + "..." if len(title) > 65 else title
                    if short not in seen:
                        headlines.append(short)
                        seen.add(short)

                if len(headlines) >= max_items:
                    return headadlines
           except Exception as e: #!/usr/bin/env python3
"""
Money Intelligence System – Daily Brief (Accurate News V1.4)
Short • Better live headlines • Fits 4x4 widget
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

# Better free RSS sources
RSS_FEEDS = [
    "https://www.moneycontrol.com/rss/latestnews.xml",
    "https://www.moneycontrol.com/rss/marketreports.xml",
    "https://economictimes.indiatimes.com/markets/rssfeeds/1977021501.cms",
]

# Strong market-related keywords
KEYWORDS = [
    "crude", "oil", "brent", "yield", "bond", "fii", "fpi", "foreign",
    "rbi", "rate", "inflation", "geopolitic", "iran", "us-", "trump",
    "strike", "bank", "nifty", "sensex", "market", "rupee", "dollar"
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
    """Fetch relevant market headlines"""
    headlines = []
    seen = set()

    for url in RSS_FEEDS:
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries[:12]:
                title = entry.get("title", "").strip()
                if not title:
                    continue

                title_lower = title.lower()
                if any(k in title_lower for k in KEYWORDS):
                    # Keep short
                    short = title[:65] + "..." if len(title) > 65 else title
                    if short not in seen:
                        headlines.append(short)
                        seen.add(short)

                if len(headlines) >= max_items:
                    return headlines
        except Exception as e:
            print(f"RSS error ({url}):", e)
            continue

    if not headlines:
        headlines = ["No strong market drivers found"]
    return headlines[:max_items]

def build_brief(indices):
    today = datetime.now().strftime("%d %b %Y")
    lines = [f"Money Brief | {today}", ""]

    nifty = indices.get("NIFTY 50", {})
    vix = indices.get("INDIA VIX", {})
    nifty_chg = nifty.get("pchange", 0.0)
    vix_level = vix.get("last", 0.0)
    vix_chg = vix.get("pchange", 0.0)

    lines.append(f"Nifty {nifty_chg:+.2f}% | VIX {vix_level:.2f} ({vix_chg:+.1f}%)")

    # Sector check
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

    # Real drivers
    lines.append("Key drivers")
    for h in get_top_headlines(2):
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
            print(f"RSS error ({url}):", e)
            continue

    if not headlines:
        headlines = ["No strong market drivers found"]
    return headlines[:max_items]

def build_brief(indices):
    today = datetime.now().strftime("%d %b %Y")
    lines = [f"Money Brief | {today}", ""]

    nifty = indices.get("NIFTY 50", {})
    vix = indices.get("INDIA VIX", {})
    nifty_chg = nifty.get("pchange", 0.0)
    vix_level = vix.get("last", 0.0)
    vix_chg = vix.get("pchange", 0.0)

    lines.append(f"Nifty {nifty_chg:+.2f}% | VIX {vix_level:.2f} ({vix_chg:+.1f}%)")

    # Sector check
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

    # Real drivers
    lines.append("Key drivers")
    for h in get_top_headlines(2):
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
