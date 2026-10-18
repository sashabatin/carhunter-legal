"""Pick the "Top 3 deals this week" for the home page and save their photos.

Run from the repo root:  python _src/pick_deals.py [path-to-bot-repo] [--days 7]
with VISION_ENDPOINT and VISION_KEY set in the environment (the bot's plate OCR resource; never
write them into a file here, this repo is public). Without them it falls back to a weaker
heuristic and says so.
Reads the content queue of the private bot repo (branch origin/content-state, which an
Azure timer keeps fresh; the copy in main/develop is stale) and writes _src/deals.json plus
img/deals/<listing_id>.webp. Then run _src/build.py.

Only deals that were approved or posted count: "skipped" ones were turned down by a human.
Numbers come from the feed as they are, never typed by hand (memory:
no-invented-numbers-in-drafts). Photos are saved here because a myauto photo URL dies with
the listing, often within days.

⚠️ Look at every saved photo before you commit: the plate masker misses some plates, and a
plate that reaches this public repo stays in git history until the history is rewritten.

--auto is the weekly run with nobody looking (bot repo, .github/workflows/site-top3.yml). It is
stricter, because no one checks the photos: OCR must be on, and a deal counts only when a person's
boxes (plate_fix.json) or OCR found a plate. No plate found = skip the car, never the heuristic
(18.10 OCR found nothing on a Sienna whose plate was in plain view, edge-on).
"""
from __future__ import annotations

import argparse
import io
import json
import subprocess
import sys
import urllib.request
from datetime import UTC, datetime, timedelta
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
OUT_JSON = Path(__file__).resolve().parent / "deals.json"
IMG_DIR = ROOT / "img" / "deals"
PLATE_FIX = Path(__file__).resolve().parent / "plate_fix.json"
STATE = "origin/content-state:content_pipeline/state/"
TOP_N = 3
PHOTO_W = 720
# A shop window, not a raw feed: the biggest discount on its own picks the junk (18.10 it
# chose a $3000 "-62%" Fusion, a 1995 BMW and a Camry with 620 000 km). Same idea as the VIP
# channel price floor, set higher because three cars must carry the whole page.
MIN_PRICE_USD = 5000
MAX_AGE_YEARS = 15
MAX_OFF_PCT = 40          # above this a listing is usually broken, salvage or a phantom


def _git_json(repo: Path, name: str) -> list:
    raw = subprocess.run(["git", "-C", str(repo), "show", STATE + name],
                         check=True, capture_output=True).stdout
    return json.loads(raw.decode("utf-8"))


def candidates(repo: Path, days: int) -> list[dict]:
    since = (datetime.now(UTC) - timedelta(days=days)).date().isoformat()
    seen: dict[str, dict] = {}
    for it in _git_json(repo, "posted_log.json"):
        if it.get("pillar") == "P1_deal" and it.get("listing_id") and it.get("facts"):
            if (it.get("posted_at") or "")[:10] >= since:
                seen[it["listing_id"]] = {**it, "day": it["posted_at"][:10]}
    for it in _git_json(repo, "queue.json"):
        if (it.get("pillar") == "P1_deal" and it.get("state") == "approved"
                and it.get("listing_id") and it.get("facts")
                and (it.get("added") or "") >= since):
            seen.setdefault(it["listing_id"], {**it, "day": it["added"]})
    good = []
    for it in seen.values():
        f = it["facts"]
        if not all(f.get(k) for k in ("asking_usd", "market_usd", "discount_pct", "image_url",
                                       "title", "year", "specs")):
            continue
        if (f["asking_usd"] >= MIN_PRICE_USD and f["discount_pct"] <= MAX_OFF_PCT
                and int(f["year"]) >= datetime.now(UTC).year - MAX_AGE_YEARS
                and "km" in f["specs"]):
            good.append(it)
    return sorted(good, key=lambda i: (-i["facts"]["discount_pct"], i["day"]))


class NoPlate(Exception):
    """--auto: no trusted plate box for this photo, so the car is skipped."""


def plate_boxes(listing_id: str, raw: bytes, img: Image.Image, platefinder, plate_ocr,
                auto: bool = False):
    """Plate boxes as (x, y, w, h) photo fractions, and how they were found.

    Order: plate_fix.json (a person's boxes win) -> Azure Read OCR, the same call that masks the
    bot's channel and DM photos in prod (22/24 plates vs 13/24 for the heuristic on the 05.10
    bench, and it reads plates at an angle) -> the Pillow heuristic in recall mode, only when OCR
    is off or failed. 18.10 the heuristic alone smeared RAV4 wheels and missed a Sienna plate."""
    fix = json.loads(PLATE_FIX.read_text(encoding="utf-8")) if PLATE_FIX.exists() else {}
    if listing_id in fix:
        return [tuple(b) for b in fix[listing_id]], "manual"
    if plate_ocr.enabled():
        res = plate_ocr.read_plates(raw, timeout=30)
        # Boxes are fractions of the frame Azure read: a different size means an EXIF turn.
        if res.status == "ok" and (not res.size or tuple(res.size) == img.size):
            if auto and not res.regions:
                raise NoPlate("OCR found no plate")
            return res.regions, "ocr"
        if auto:
            raise NoPlate(f"OCR {res.status}")
        print(f"  OCR {res.status} on {listing_id}: heuristic instead, CHECK THIS PHOTO")
    else:
        print("  VISION_ENDPOINT / VISION_KEY not set: heuristic only, CHECK EVERY PHOTO")
    return platefinder.find_plates(img, recall=True), "heuristic"


def save_photo(listing_id: str, url: str, platefinder, plate_ocr, auto: bool = False) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=30) as r:  # nosec B310 - fixed https host from the feed
        raw = r.read()
    img = Image.open(io.BytesIO(raw)).convert("RGB")
    boxes, via = plate_boxes(listing_id, raw, img, platefinder, plate_ocr, auto)
    if boxes:
        img = platefinder.mask_regions(img, boxes)
    print(f"  {listing_id}: {len(boxes)} plate box(es) via {via}")
    if img.width > PHOTO_W:
        img = img.resize((PHOTO_W, round(img.height * PHOTO_W / img.width)), Image.LANCZOS)
    IMG_DIR.mkdir(parents=True, exist_ok=True)
    name = f"{listing_id}.webp"
    img.save(IMG_DIR / name, "WEBP", quality=78, method=6)
    return f"/img/deals/{name}"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("repo", nargs="?", default=str(ROOT.parent / "car_checker_ge"))
    ap.add_argument("--days", type=int, default=7)
    ap.add_argument("--auto", action="store_true", help="weekly run with nobody looking")
    args = ap.parse_args()
    repo = Path(args.repo)
    sys.path.insert(0, str(repo / "src"))
    from car_checker_ge import plate_ocr, platefinder
    if args.auto and not plate_ocr.enabled():
        raise SystemExit("--auto needs VISION_ENDPOINT and VISION_KEY: no unchecked heuristic")
    subprocess.run(["git", "-C", str(repo), "fetch", "origin", "content-state"], check=True)
    picked, out = candidates(repo, args.days), []
    for it in picked:
        if len(out) == TOP_N:
            break
        f = it["facts"]
        try:
            img = save_photo(it["listing_id"], f["image_url"], platefinder, plate_ocr, args.auto)
        except NoPlate as exc:
            print("skip", it["listing_id"], "plate:", exc)
            continue
        except Exception as exc:  # a dead photo = the listing is going away; take the next deal
            print("skip", it["listing_id"], "photo:", exc)
            continue
        city = (f.get("location") or "").split(",")[0].strip()
        km = next((p.strip() for p in (f.get("specs") or "").split("·") if "km" in p), "")
        out.append({
            "id": it["listing_id"], "day": it["day"],
            "car": f"{f['title']} {f['year']}", "city": city, "km": km.replace(" km", ""),
            "price_usd": f["asking_usd"], "market_usd": f["market_usd"],
            "off": f["discount_pct"], "img": img,
        })
    if len(out) < TOP_N:
        raise SystemExit(f"only {len(out)} usable deals in {args.days} days; widen --days")
    today = datetime.now(UTC).date()
    window = {"from": (today - timedelta(days=args.days)).isoformat(), "to": today.isoformat()}
    OUT_JSON.write_text(json.dumps({**window, "deals": out},
                                   ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    # Last week's photos go: the page shows three, and the repo should not grow by three a week.
    keep = {Path(d["img"]).name for d in out}
    for old in IMG_DIR.glob("*.webp"):
        if old.name not in keep:
            old.unlink()
    for d in out:
        print(f"{d['off']}%  {d['car']}  ${d['price_usd']} vs ${d['market_usd']}  {d['day']}")
    print("\nLOOK AT EACH PHOTO before commit (missed plate = public for good); fix boxes in "
          "_src/plate_fix.json and rerun:")
    for d in out:
        print("  " + str(ROOT / d["img"].lstrip("/")))


if __name__ == "__main__":
    main()
