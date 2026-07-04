"""Orchestrate: fetch -> normalize -> score -> ranked lead list."""
from __future__ import annotations

from pathlib import Path

import pandas as pd
import yaml

from . import fetch as fetch_mod
from .normalize import to_features
from .score import apply_buy_box, score

ROOT = Path(__file__).resolve().parent.parent


def load_config(path: str | Path = None) -> dict:
    path = Path(path) if path else ROOT / "config.yaml"
    with open(path) as fh:
        return yaml.safe_load(fh)


def run(config: dict = None, limit: int | None = None) -> pd.DataFrame:
    config = config or load_config()
    raw_dir = ROOT / "data" / "raw"
    out_dir = ROOT / config["output"]["dir"]
    out_dir.mkdir(parents=True, exist_ok=True)

    print("1/4  Fetching public open-data sources…")
    frames = fetch_mod.fetch_all(config, raw_dir, limit=limit)

    print("2/4  Normalizing + joining on address…")
    features = to_features(config, frames)
    print(f"     {len(features):,} distinct properties with a distress signal")

    print("3/4  Scoring motivated-seller propensity…")
    scored = score(features, config)
    ranked = apply_buy_box(scored, config)

    print("4/4  Writing outputs…")
    ranked_path = out_dir / config["output"]["ranked_file"]
    top_path = out_dir / config["output"]["shortlist_file"]
    ranked.to_csv(ranked_path, index=False)
    ranked.head(config["buy_box"]["top_n"]).to_csv(top_path, index=False)

    print(f"\n✓ {len(ranked):,} ranked leads  ->  {ranked_path}")
    print(f"✓ top {min(len(ranked), config['buy_box']['top_n'])}         ->  {top_path}")
    _print_top(ranked)
    return ranked


def _print_top(ranked: pd.DataFrame, n: int = 10) -> None:
    if ranked.empty:
        print("\n(no leads matched the buy-box)")
        return
    print(f"\nTop {min(n, len(ranked))} motivated-seller leads:")
    view = ranked.head(n)[["rank", "motivated_seller_score", "address", "signals", "suggested_action"]]
    with pd.option_context("display.max_colwidth", 44, "display.width", 160):
        print(view.to_string(index=False))
