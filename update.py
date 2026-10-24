#!/usr/bin/env python3
"""Refresh data.js for the Freebie Board. Keyless sources: Epic free-games feed + GamerPower."""
import json, re, sys, urllib.request
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).parent
UA = {"User-Agent": "Mozilla/5.0 FreebieBoard"}
COUNTRY = "DE"  # Epic region


def get(url):
    req = urllib.request.Request(url, headers=UA)
    return json.loads(urllib.request.urlopen(req, timeout=30).read().decode("utf-8"))


def slug(s):
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")[:60]


def epic():
    url = ("https://store-site-backend-static.ak.epicgames.com/freeGamesPromotions"
           f"?locale=en-US&country={COUNTRY}&allowCountries={COUNTRY}")
    out = []
    for e in get(url)["data"]["Catalog"]["searchStore"]["elements"]:
        promos = e.get("promotions") or {}
        page = (e.get("offerMappings") or [{}])[0].get("pageSlug") or e.get("productSlug") or e.get("urlSlug")
        link = f"https://store.epicgames.com/en-US/p/{page}" if page else "https://store.epicgames.com/en-US/free-games"
        for key, upcoming in (("promotionalOffers", False), ("upcomingPromotionalOffers", True)):
            for block in promos.get(key) or []:
                for o in block.get("promotionalOffers") or []:
                    if o["discountSetting"]["discountPercentage"] != 0:
                        continue
                    d = {"title": e["title"], "store": "Epic", "kind": "game", "url": link,
                         "endsAt": o["endDate"].replace(".000Z", "Z")}
                    if upcoming:
                        d["startsAt"] = o["startDate"].replace(".000Z", "Z")
                    out.append(("epic-" + slug(e["title"]), d))
    return out


def gamerpower(skip_epic):
    out = []
    for g in get("https://www.gamerpower.com/api/giveaways?platform=pc"):
        if g.get("status") != "Active":
            continue
        m = re.search(r"\((.+?)\)\s*Giveaway\s*$", g["title"])
        store = m.group(1) if m else "Other"
        title = re.sub(r"\s*\(.+?\)\s*Giveaway\s*$", "", g["title"])
        if skip_epic and store.startswith("Epic"):
            continue
        store = {"Epic Games": "Epic", "Itch.io": "itch.io"}.get(store, store)
        kind = {"Game": "game", "DLC": "dlc", "Early Access": "playtest", "Other": "loot"}.get(g["type"], "game")
        d = {"title": title, "store": store, "kind": kind, "url": g["open_giveaway_url"]}
        if g.get("worth") not in (None, "", "N/A"):
            d["note"] = f"Worth {g['worth']}"
        if g.get("end_date") and g["end_date"] != "N/A":
            d["endsAt"] = g["end_date"].replace(" ", "T") + "Z"
            d["endsApprox"] = True
        out.append(("gp-%s" % g["id"], d))
    return out


def main():
    items, notes, epic_ok = {}, [], False
    try:
        for k, d in epic():
            items[k] = d
        epic_ok = True
        notes.append("Epic ok")
    except Exception as ex:
        notes.append(f"Epic failed: {ex}")
    try:
        for k, d in gamerpower(epic_ok):
            items[k] = d
        notes.append("GamerPower ok")
    except Exception as ex:
        notes.append(f"GamerPower failed: {ex}")
    if not items:
        sys.exit("Nothing fetched; keeping the old data.js. " + "; ".join(notes))
    extra = HERE / "extra.json"
    if extra.exists():
        for i, d in enumerate(json.loads(extra.read_text(encoding="utf-8"))):
            items[f"extra-{i}"] = d
    norm = lambda t: re.sub(r"[^a-z0-9]+", " ", t.lower()).strip()
    extra_titles = {norm(d["title"]) for k, d in items.items() if k.startswith("extra-")}
    items = {k: d for k, d in items.items() if k.startswith("extra-") or norm(d["title"]) not in extra_titles}
    for k, d in items.items():
        d["id"] = k
    data = {"updatedAt": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "note": "; ".join(notes), "items": list(items.values())}
    (HERE / "data.js").write_text("window.FREEBIES=" + json.dumps(data, ensure_ascii=False) + ";\n", encoding="utf-8")
    print(f"{len(items)} offers. " + "; ".join(notes))


main()
