#!/usr/bin/env python3
"""Chicago Deal Engine — CLI entry point.

  python run.py --validate     # check every source endpoint responds
  python run.py                # full pipeline -> ranked lead CSVs
  python run.py --limit 5000   # quick sample run (caps rows per source)
"""
import argparse

from src.fetch import validate_sources
from src.pipeline import load_config, run


def main() -> None:
    ap = argparse.ArgumentParser(description="Chicago motivated-seller deal engine")
    ap.add_argument("--validate", action="store_true", help="probe source endpoints and exit")
    ap.add_argument("--limit", type=int, default=None, help="cap rows per source (fast sample run)")
    ap.add_argument("--config", default=None, help="path to config.yaml")
    args = ap.parse_args()

    config = load_config(args.config)

    if args.validate:
        print("Validating sources…")
        for name, status in validate_sources(config).items():
            mark = "✓" if status == "ok" else "✗"
            print(f"  {mark} {name}: {status}")
        return

    run(config, limit=args.limit)


if __name__ == "__main__":
    main()
