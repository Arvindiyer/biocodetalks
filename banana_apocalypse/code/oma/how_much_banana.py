"""How much banana are you?  (the short version you run on camera)

Asks the OMA orthology database which human genes have an ortholog in banana
(Musa acuminata, OMA code MUSAM). The full analysis, with other species and
protein identities, is code/oma_orthologs.py.

Run: python code/oma/how_much_banana.py
"""
import json
from pathlib import Path

import requests

API = "https://omabrowser.org/api"


def get_all(url):
    """OMA returns long lists in pages; collect them all."""
    items, page = [], 1
    while True:
        r = requests.get(url, params={"page": page, "per_page": 1000}, timeout=120)
        r.raise_for_status()
        items += r.json()
        if len(items) >= int(r.headers["x-total-count"]):
            return items
        page += 1


pairs = get_all(f"{API}/pairs/HUMAN/MUSAM/")          # every human-banana ortholog pair
human_hits = {p["entry_1"]["omaid"] for p in pairs
              if p["entry_1"]["is_main_isoform"]}      # one entry per human gene

# number of human protein-coding genes in OMA (main isoforms); cached by oma_orthologs.py
ROOT = Path(__file__).resolve().parents[2]
cache = ROOT / "results" / "oma" / "oma_summary.json"
n_human = json.loads(cache.read_text())["human_main_isoforms"]

print(f"ortholog pairs human-banana : {len(pairs):,}")
print(f"human genes with a banana ortholog: {len(human_hits):,} of {n_human:,}")
print(f"that is {100 * len(human_hits) / n_human:.1f}% of human genes")
