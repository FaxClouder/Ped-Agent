from __future__ import annotations

import argparse
from pathlib import Path

from ped_knowledge.storage.inventory import backup_sqlite, build_inventory


def main() -> int:
    parser = argparse.ArgumentParser(description="Create a read-only memPed asset inventory")
    parser.add_argument("--memped-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--catalog-backup", type=Path)
    args = parser.parse_args()
    build_inventory(args.memped_root, args.output)
    if args.catalog_backup:
        catalog = args.memped_root / "knowledge" / "knowledge.sqlite3"
        if catalog.exists():
            backup_sqlite(catalog, args.catalog_backup)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
