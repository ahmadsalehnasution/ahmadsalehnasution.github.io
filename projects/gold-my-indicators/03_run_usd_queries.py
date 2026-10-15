#!/usr/bin/env python3
"""Run the USD-decomposition queries (q09, q10) against the existing DuckDB and write their CSVs.

Run with the project venv: /data/.hermes/profiles/career/venv/bin/python 03_run_usd_queries.py
"""
import csv
import os

import duckdb

BASE = "/data/.hermes/profiles/career/home/tracker/proyek/P2 - Gold vs Household Indicators MY"
con = duckdb.connect(os.path.join(BASE, "gold_my.duckdb"), read_only=True)

for name in ("q09_usd_decomposition", "q10_fx_subperiods"):
    sql = open(os.path.join(BASE, "sql", f"{name}.sql")).read()
    cur = con.execute(sql)
    cols = [c[0] for c in cur.description]
    rows = cur.fetchall()
    out = os.path.join(BASE, "results", f"{name}.csv")
    with open(out, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(cols)
        w.writerows(rows)
    print(f"=== {name} -> {os.path.basename(out)} ({len(rows)} baris)")
    print("   " + " | ".join(cols))
    for r in rows:
        print("   " + " | ".join("" if v is None else str(v) for v in r))
    print()

con.close()
