"""How much banana are you? — orthologs between human and other species, from OMA.

Extends Arvind's earlier notebook (../../../banna_script.ipynb), which used the
`omadb` client. This version talks to the public OMA REST API directly
(https://omabrowser.org/api/), caches every download, and adds:

  1. % of human protein-coding genes (main isoforms) with >=1 ortholog in each
     comparison species (chimp ... banana ... E. coli)
  2. % amino-acid identity of every human-banana ortholog pair
     (global alignment, BLOSUM62, Biopython PairwiseAligner)
  3. a handful of "showcase" genes used on screen

Run (needs biopython; the r_py env has it):
    /Users/arvindiyer/micromamba/envs/r_py/bin/python code/oma_orthologs.py
Outputs: code/results/oma_*.csv|json, data/raw/oma/* (cache)
"""
from __future__ import annotations

import json
import time
from pathlib import Path

import numpy as np
import pandas as pd
import requests
from Bio import Align
from Bio.Align import substitution_matrices

ROOT = Path(__file__).resolve().parents[2]
CACHE = ROOT / "data" / "oma" / "cache"
RES = ROOT / "results" / "oma"
CACHE.mkdir(parents=True, exist_ok=True)
RES.mkdir(parents=True, exist_ok=True)
API = "https://omabrowser.org/api"

# comparison species (OMA 5-letter codes) and display names
SPECIES = [
    ("PANTR", "Chimpanzee"), ("MOUSE", "Mouse"), ("DANRE", "Zebrafish"),
    ("DROME", "Fruit fly"), ("CAEEL", "Nematode worm"), ("ARATH", "Arabidopsis"),
    ("MUSAM", "Banana"), ("YEAST", "Baker's yeast"), ("ECOLI", "E. coli"),
]

# genes shown on screen: (UniProt mnemonic in OMA, label)
SHOWCASE = [
    ("H31_HUMAN", "Histone H3.1"), ("UBB_HUMAN", "Ubiquitin B"), ("ACTB_HUMAN", "Actin, beta"),
    ("CYC_HUMAN", "Cytochrome c"), ("G3P_HUMAN", "GAPDH"), ("TBB5_HUMAN", "Tubulin beta"),
    ("INS_HUMAN", "Insulin"), ("HBB_HUMAN", "Haemoglobin beta"), ("KRT1_HUMAN", "Keratin 1"),
]

S = requests.Session()


def get_paged(url: str, cache_name: str) -> list:
    """Download every page of a paginated OMA list endpoint (cached as JSON)."""
    f = CACHE / cache_name
    if f.exists():
        return json.loads(f.read_text())
    out, page = [], 1
    while True:
        for attempt in range(5):
            r = S.get(url, params={"per_page": 1000, "page": page}, timeout=120)
            if r.ok:
                break
            time.sleep(3 * (attempt + 1))
        r.raise_for_status()
        data = r.json()
        out.extend(data)
        total = int(r.headers.get("x-total-count", len(out)))
        print(f"  {cache_name}: {len(out)}/{total}", flush=True)
        if len(out) >= total or not data:
            break
        page += 1
    f.write_text(json.dumps(out))
    return out


def slim_proteins(code: str) -> pd.DataFrame:
    """Protein list for a genome, reduced to the columns we need."""
    f = CACHE / f"{code}_proteins_slim.csv"
    if f.exists():
        return pd.read_csv(f)
    full = get_paged(f"{API}/genome/{code}/proteins/", f"{code}_proteins.json")
    df = pd.DataFrame([{"omaid": p["omaid"], "canonicalid": p["canonicalid"],
                        "is_main_isoform": p["is_main_isoform"], "length": p["sequence_length"]}
                       for p in full])
    df.to_csv(f, index=False)
    (CACHE / f"{code}_proteins.json").unlink()  # the full JSON is large; the slim CSV is enough
    return df


def pairs(a: str, b: str) -> pd.DataFrame:
    f = CACHE / f"pairs_{a}_{b}.csv"
    if f.exists():
        return pd.read_csv(f)
    raw = get_paged(f"{API}/pairs/{a}/{b}/", f"pairs_{a}_{b}.json")
    df = pd.DataFrame([{
        "id1": p["entry_1"]["omaid"], "can1": p["entry_1"]["canonicalid"],
        "main1": p["entry_1"]["is_main_isoform"], "len1": p["entry_1"]["sequence_length"],
        "id2": p["entry_2"]["omaid"], "can2": p["entry_2"]["canonicalid"],
        "main2": p["entry_2"]["is_main_isoform"], "len2": p["entry_2"]["sequence_length"],
        "rel_type": p["rel_type"], "pam_distance": p["distance"], "score": p["score"],
    } for p in raw])
    df.to_csv(f, index=False)
    (CACHE / f"pairs_{a}_{b}.json").unlink()
    return df


def sequences(ids: list[str]) -> dict[str, str]:
    """Fetch protein sequences via OMA bulk_retrieve (100 ids per request), cached."""
    f = CACHE / "sequences.json"
    have = json.loads(f.read_text()) if f.exists() else {}
    todo = [i for i in dict.fromkeys(ids) if i not in have]
    for k in range(0, len(todo), 100):
        chunk = todo[k:k + 100]
        for attempt in range(5):
            r = S.post(f"{API}/protein/bulk_retrieve/", json={"ids": chunk}, timeout=180)
            if r.ok:
                break
            time.sleep(3 * (attempt + 1))
        r.raise_for_status()
        for item in r.json():
            t = item.get("target")
            if t:
                have[item["query_id"]] = t["sequence"]
        if (k // 100) % 10 == 0:
            print(f"  sequences: {len(have)} cached", flush=True)
            f.write_text(json.dumps(have))
    f.write_text(json.dumps(have))
    return have


def aligner() -> Align.PairwiseAligner:
    al = Align.PairwiseAligner()
    al.substitution_matrix = substitution_matrices.load("BLOSUM62")
    al.open_gap_score, al.extend_gap_score = -11, -1
    al.mode = "global"
    return al


def identity(al, s1: str, s2: str) -> tuple[float, int]:
    """% identical positions over aligned (non-gap) columns, and number of such columns."""
    aln = al.align(s1, s2)[0]
    ident = aligned = 0
    for (a0, a1), (b0, b1) in zip(*aln.aligned):
        seg1, seg2 = s1[a0:a1], s2[b0:b1]
        aligned += len(seg1)
        ident += sum(x == y for x, y in zip(seg1, seg2))
    return (100.0 * ident / aligned if aligned else float("nan")), aligned


def main():
    print("1) human gene set")
    human = slim_proteins("HUMAN")
    human_main = set(human.loc[human.is_main_isoform, "omaid"])
    print(f"   human main-isoform proteins: {len(human_main)}")
    banana = slim_proteins("MUSAM")
    banana_main = set(banana.loc[banana.is_main_isoform, "omaid"])
    print(f"   banana main-isoform proteins: {len(banana_main)}")

    print("2) orthologs per species")
    rows = []
    for code, name in SPECIES:
        df = pairs("HUMAN", code)
        with_orth = set(df.loc[df.id1.isin(human_main), "id1"])
        rows.append({"code": code, "species": name, "pairs": len(df),
                     "human_genes_with_ortholog": len(with_orth),
                     "human_genes_total": len(human_main),
                     "pct_human_genes": round(100 * len(with_orth) / len(human_main), 1)})
        print(f"   {name:15s} {rows[-1]['pct_human_genes']:5.1f}%  ({len(with_orth)} genes)")
    summary = pd.DataFrame(rows)
    summary.to_csv(RES / "oma_percent_human_genes_with_ortholog.csv", index=False)

    # banana side: % of banana genes with a human ortholog
    hb = pairs("HUMAN", "MUSAM")
    ban_with = set(hb.loc[hb.id2.isin(banana_main), "id2"])
    ban_pct = 100 * len(ban_with) / len(banana_main)

    print("3) identity of human-banana ortholog pairs")
    hb_main = hb[hb.main1 & hb.main2].copy()
    seqs = sequences(list(hb_main.id1) + list(hb_main.id2))
    al = aligner()
    ids, alen = [], []
    t0 = time.time()
    for a, b in zip(hb_main.id1, hb_main.id2):
        if a in seqs and b in seqs:
            pid, n = identity(al, seqs[a], seqs[b])
        else:
            pid, n = float("nan"), 0
        ids.append(pid)
        alen.append(n)
    hb_main["pct_identity"] = ids
    hb_main["aligned_columns"] = alen
    print(f"   aligned {len(hb_main)} pairs in {time.time() - t0:.0f}s")
    hb_main.to_csv(RES / "oma_human_banana_pairs_identity.csv", index=False)

    # one value per human gene: its best-matching banana ortholog
    best = hb_main.sort_values("pct_identity", ascending=False).drop_duplicates("id1")
    stats = {
        "human_main_isoforms": len(human_main),
        "banana_main_isoforms": len(banana_main),
        "human_banana_pairs_all": len(hb),
        "human_banana_pairs_main_isoforms": len(hb_main),
        "human_genes_with_banana_ortholog": int(summary.set_index("code").loc["MUSAM", "human_genes_with_ortholog"]),
        "pct_human_genes_with_banana_ortholog": float(summary.set_index("code").loc["MUSAM", "pct_human_genes"]),
        "banana_genes_with_human_ortholog": len(ban_with),
        "pct_banana_genes_with_human_ortholog": round(ban_pct, 1),
        "rel_type_counts": hb.rel_type.value_counts().to_dict(),
        "identity_best_per_human_gene": {
            "n": int(best.pct_identity.notna().sum()),
            "median": round(float(best.pct_identity.median()), 1),
            "mean": round(float(best.pct_identity.mean()), 1),
            "q25": round(float(best.pct_identity.quantile(.25)), 1),
            "q75": round(float(best.pct_identity.quantile(.75)), 1),
            "pct_above_80": round(float((best.pct_identity > 80).mean() * 100), 1),
            "pct_below_40": round(float((best.pct_identity < 40).mean() * 100), 1),
        },
        "oma_api": API,
        "retrieved": time.strftime("%Y-%m-%d"),
    }
    best.to_csv(RES / "oma_human_banana_best_per_gene.csv", index=False)

    print("4) showcase genes")
    show = []
    # several OMA entries can share a canonical ID (isoforms; multi-copy genes such as
    # histone H3.1), so match on ALL main-isoform entries and keep the best-identity hit
    main_ids = human[human.is_main_isoform].groupby("canonicalid").omaid.apply(list).to_dict()
    for can, label in SHOWCASE:
        hids = main_ids.get(can, [])
        hit = best[best.id1.isin(hids)].sort_values("pct_identity", ascending=False)
        if len(hit):
            r = hit.iloc[0]
            show.append({"gene": label, "human": can, "banana": r.can2, "banana_omaid": r.id2,
                         "rel_type": r.rel_type, "pct_identity": round(float(r.pct_identity), 1),
                         "human_len": int(r.len1), "banana_len": int(r.len2)})
        else:
            show.append({"gene": label, "human": can, "banana": None, "banana_omaid": None,
                         "rel_type": None, "pct_identity": None, "human_len": None, "banana_len": None})
        print("  ", show[-1])
    pd.DataFrame(show).to_csv(RES / "oma_showcase_genes.csv", index=False)
    stats["showcase"] = show
    (RES / "oma_summary.json").write_text(json.dumps(stats, indent=1, default=str))
    print(json.dumps({k: v for k, v in stats.items() if k != "showcase"}, indent=1, default=str))


if __name__ == "__main__":
    main()
