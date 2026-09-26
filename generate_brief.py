#!/usr/bin/env python3
"""
Money Intelligence System – Daily Brief (V1)
Free • India-focused • Rule-based significance filter
"""

from datetime import datetime
from jugaad_data.nse import NSELive
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

REL_THRESHOLD = 1.3  # relative move vs Nifty to trigger investigation

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

def build_brief(indices):
    today = datetime.now().strftime("%d %b %Y")
    lines = [f"Money Brief | {today}", ""]

    nifty = indices.get("NIFTY 50", {})
    vix = indices.get("INDIA VIX", {})
    nifty_chg = nifty.get("pchange", 0.0)

    lines.append("Market")
    lines.append(f"Nifty 50: {nifty_chg:+.2f}%")
    if vix:
        lines.append(f"India VIX: {vix.get('last', 0):.2f} ({vix.get('pchange', 0):+.1f}%)")
    lines.append("")

    notable = []
    for full, short in SECTORS.items():
        sec = indices.get(full)
        if not sec:
            continue
        chg = sec["pchange"]
        rel = chg - nifty_chg
        if abs(rel) >= REL_THRESHOLD:
            notable.append((short, rel, chg))

    lines.append("Notable moves (vs Nifty)")
    if notable:
        for short, rel, chg in sorted(notable, key=lambda x: abs(x[1]), reverse=True):
            direction = "outperformed" if rel > 0 else "underperformed"
            lines.append(f"{short}: {chg:+.2f}% (rel {rel:+.2f}%) → {direction}")
    else:
        lines.append("None ≥ 1.3% relative")
    lines.append("")

    if notable:
        lines.append("Investigation prompts")
        for i, (short, rel, _) in enumerate(notable[:2], 1):
            lines.append(
                f"{i}. {short} moved meaningfully. "
                "What happened? Why? Who benefits? Who gets hurt? "
                "Temporary or structural? What evidence could prove my thesis wrong?"
            )
    else:
        lines.append("No strong sector signals today.")

    lines.append("")
    lines.append("Sources: NSE")
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
