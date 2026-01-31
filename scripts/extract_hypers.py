#!/usr/bin/env python3
"""Extract all tables from .hyper files to CSV files.

Usage:
  python scripts/extract_hypers.py --src twbx/ExecutiveKPI_extracted/Data --dest samplepbipfolder/DataExtracts

Notes:
- Requires `tableauhyperapi` (install after Visual C++ Build Tools):
    python -m pip install --upgrade pip setuptools wheel
    python -m pip install tableauhyperapi
"""
from __future__ import annotations
import argparse
import csv
import json
import sys
from pathlib import Path

try:
    from tableauhyperapi import HyperProcess, Connection, Telemetry, TableName
except Exception:
    print("ERROR: the 'tableauhyperapi' package is required. Install with:\n  python -m pip install tableauhyperapi")
    sys.exit(1)


def extract_hyper(hyper_path: Path, dest_dir: Path):
    dest_dir.mkdir(parents=True, exist_ok=True)
    records = []

    with HyperProcess(telemetry=Telemetry.DO_NOT_SEND_USAGE_DATA_TO_TABLEAU) as hp:
        with Connection(hp.endpoint, database=str(hyper_path)) as conn:
            catalog = conn.catalog
            tables = catalog.get_table_names()
            for table in tables:
                schema = table.schema_name
                name = table.table_name
                safe_name = f"{hyper_path.stem}__{schema}__{name}".replace(' ', '_').replace('.', '_')
                out_file = dest_dir / f"{safe_name}.csv"

                # get column names from table definition
                table_def = catalog.get_table_definition(table)
                columns = [col.name for col in table_def.columns]

                row_count = 0
                with conn.execute_query(f'SELECT * FROM "{schema}"."{name}"') as result:
                    with out_file.open("w", newline="", encoding="utf-8") as f:
                        writer = csv.writer(f)
                        writer.writerow(columns)
                        for row in result:
                            writer.writerow(list(row))
                            row_count += 1

                records.append({
                    "hyper": str(hyper_path),
                    "schema": schema,
                    "table": name,
                    "csv": str(out_file),
                    "rows": row_count,
                    "columns": columns,
                })
                print(f"Extracted {row_count} rows: {out_file}")

    return records


def main():
    parser = argparse.ArgumentParser(description="Extract .hyper files to CSV")
    parser.add_argument("--src", required=True, help="Source folder to search for .hyper files")
    parser.add_argument("--dest", required=True, help="Destination folder for CSV files")
    args = parser.parse_args()

    src = Path(args.src)
    dest = Path(args.dest)

    if not src.exists():
        print(f"Source folder not found: {src}")
        sys.exit(1)

    hypers = list(src.rglob("*.hyper"))
    if not hypers:
        print(f"No .hyper files found under: {src}")
        sys.exit(1)

    manifest = []
    for h in hypers:
        print(f"Processing: {h}")
        manifest += extract_hyper(h, dest)

    manifest_path = dest / "extraction_manifest.json"
    with manifest_path.open("w", encoding="utf-8") as mf:
        json.dump(manifest, mf, indent=2)

    print(f"Done. Manifest written to: {manifest_path}")


if __name__ == "__main__":
    main()
