#!/usr/bin/env python3
"""
Money Intelligence System – Daily Brief (Chain Style V1.5)
Short causal chain • Fits 4x4 widget
"""

from datetime import datetime
from jugaad_data.nse import NSELive
import feedparser
import traceback

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

def get_market_context():
    """Simple context from free RSS"""
    keywords_oil = ["crude", "oil", "brent"]
    keywords_yield = ["yield", "bond", "treasury"]
    keywords_fii = ["fii", "fpi", "foreign"]

    oil_signal = False
    yield_signal = False
    fii_signal = False

    feeds = [
        "https://www.moneycontrol.com/rss/latestnews.xml",
        "https://www.moneycontrol.com/rss/marketreports.xml",
    ]

    for url in feeds:
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries[:10]:
                title = entry.get("title", "").lower()
                if any(k in title for k in keywords_oil):
                    oil_signal = True
                if any(k in title for k in keywords_yield):
                    yield_signal = True
                if any(k in title for k in keywords_fii):
                    fii_signal = True
        except Exception:
            continue

    return oil_signal, yield_signal, fii_signal

def build_brief(indices):
    today = datetime.now().strftime("%d %b")
    lines = [f"Money Brief | {today}", ""]

    nifty = indices.get("NIFTY 50", {})
    vix = indices.get("INDIA VIX", {})
    nifty_chg = nifty.get("pchange", 0.0)
    vix_level = vix.get("last", 0.0)

    # Market line
    vix_status = "elevated" if vix_level > 13.5 else "normal"
    lines.append(f"Nifty {nifty_chg:+.2f}% | VIX {vix_status}")
    lines.append("")

    # Causal Chain
    oil_signal, yield_signal, fii_signal = get_market_context()

    lines.append("Chain")
    if oil_signal or nifty_chg < -1:
        lines.append("Oil ↑ → Inflation risk ↑")
    else:
        lines.append("Oil stable → Inflation calm")

    if yield_signal or nifty_chg < -1:
        lines.append("Bond yields ↑ → Rate pressure ↑")
    else:
        lines.append("Bond yields stable")

    if nifty_chg < -0.5:
        lines.append("Rupee pressure → Equities ↓")
    else:
        lines.append("Currency stable → Equities mixed")
    lines.append("")

    # Key points
    lines.append("Key")
    key_points = []
    if oil_signal:
        key_points.append("Crude elevated")
    if yield_signal:
        key_points.append("US yields high")
    if fii_signal or nifty_chg < -1:
        key_points.append("FII selling")
    if not key_points:
        key_points.append("No strong external pressure")

    lines.append(" | ".join(key_points[:3]))
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
