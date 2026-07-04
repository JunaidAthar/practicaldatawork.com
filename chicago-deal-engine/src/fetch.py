"""Pull each configured open-data source to data/raw/<name>.csv."""
from __future__ import annotations

from datetime import datetime, timedelta
from pathlib import Path

import pandas as pd

from .socrata import SocrataClient, SocrataError


def _cutoff_iso(lookback_days: int) -> str:
    return (datetime.utcnow() - timedelta(days=lookback_days)).strftime("%Y-%m-%dT00:00:00")


def _build_where(src: dict, cutoff_iso: str) -> str | None:
    parts = []
    if src.get("date_field"):
        parts.append(f"{src['date_field']} >= '{cutoff_iso}'")
    if src.get("where"):
        parts.append(f"({src['where']})")
    return " AND ".join(parts) or None


def validate_sources(config: dict) -> dict:
    """Probe every enabled source; return {name: ok/error-message}."""
    results = {}
    for name, src in config["sources"].items():
        if not src.get("enabled", True):
            continue
        client = SocrataClient(src["domain"], page_size=1)
        try:
            client.probe(src["dataset_id"])
            results[name] = "ok"
        except SocrataError as e:
            results[name] = f"FAILED: {e}"
    return results


def fetch_source(name: str, src: dict, fetch_cfg: dict, raw_dir: Path) -> pd.DataFrame:
    client = SocrataClient(src["domain"], page_size=fetch_cfg["page_size"])
    where = _build_where(src, _cutoff_iso(fetch_cfg["lookback_days"]))
    rows = client.fetch_all(
        src["dataset_id"],
        select=src.get("select"),
        where=where,
        max_records=fetch_cfg["max_records_per_source"],
    )
    df = pd.DataFrame(rows)
    raw_dir.mkdir(parents=True, exist_ok=True)
    df.to_csv(raw_dir / f"{name}.csv", index=False)
    return df


def fetch_all(config: dict, raw_dir: Path, limit: int | None = None) -> dict:
    """Fetch every enabled source. Failures are logged, not fatal, so a stale
    dataset id in one source never sinks the whole run."""
    fetch_cfg = dict(config["fetch"])
    if limit:
        fetch_cfg["max_records_per_source"] = limit
    frames = {}
    for name, src in config["sources"].items():
        if not src.get("enabled", True):
            continue
        try:
            df = fetch_source(name, src, fetch_cfg, raw_dir)
            print(f"  [{name}] fetched {len(df):,} rows")
            frames[name] = df
        except SocrataError as e:
            print(f"  [{name}] SKIPPED — {e}")
    if not frames:
        raise SystemExit("No sources fetched. Check dataset IDs / network in config.yaml.")
    return frames
