#!/usr/bin/env python3
"""sim-post CLI - inspect FEA/CFD result files and the stored case database.

The loader, statistics and section-cut code runs on the standard library only,
so the analysis subcommands work on a bare interpreter.  "cases" reads the
project's SQLite file directly, and "serve" is the only subcommand that imports
Flask, lazily inside the function, which keeps `python cli.py --help` usable
without the web dependencies installed.
"""

from __future__ import annotations

import argparse
import json
import os
import sqlite3

from . import paths

ROOT = str(paths.PROJECT_ROOT)
VERSION = "0.1.0"
DEFAULT_DB = str(paths.INSTANCE_DIR / "simpost.db")


def _load(path: str, fmt: str) -> dict:
    from .post.loader import load_csv, load_vtk

    fmt = fmt or ("vtk" if path.lower().endswith(".vtk") else "csv")
    return load_csv(path) if fmt == "csv" else load_vtk(path)


def cmd_stats(args) -> int:
    from .post.fields import normalize, stats

    case = _load(args.file, args.format)
    print(f"{args.file}: {len(case['nodes'])} nodes, fields: {', '.join(case['fields']) or 'none'}")
    print(f"{'field':<14} {'min':>10} {'max':>10} {'mean':>10}")
    rows = []
    for name, values in case["fields"].items():
        st = stats(values)
        print(f"{name:<14} {st['min']:>10.4g} {st['max']:>10.4g} {st['mean']:>10.4g}")
        rows.append({"name": name, **st, "normalized_head": normalize(values)[:3]})
    if args.json:
        print(json.dumps(rows, indent=2))
    return 0


def cmd_section(args) -> int:
    from .post.sections import section_cut

    case = _load(args.file, args.format)
    pts = section_cut(case, args.axis, args.value)
    print(f"section {args.axis}={args.value}: {len(pts)} point(s)")
    for p in pts[: args.limit or len(pts)]:
        print(f"  x={p[0]:<9.4g} y={p[1]:<9.4g} value={p[2]:.4g}")
    return 0


def cmd_probe(args) -> int:
    from .post.sections import probe

    case = _load(args.file, args.format)
    out = probe(case, args.x, args.y, args.z)
    print(f"nearest node to ({args.x}, {args.y}, {args.z}): {out['node']}")
    for key, value in out.items():
        if key != "node":
            print(f"  {key:<14} {value:.6g}")
    return 0


def cmd_cases(args) -> int:
    db = args.db or os.environ.get("SIMPOST_DB", DEFAULT_DB)
    if not os.path.exists(db):
        print(f"no database at {db} (start the server or POST /api/cases first)")
        return 0
    con = sqlite3.connect(db)
    try:
        cols = [r[1] for r in con.execute("PRAGMA table_info(cases)")]
        if not cols:
            print(f"{db} has no cases table")
            return 0
        rows = list(
            con.execute("SELECT id, name, format, nodes, created_at FROM cases ORDER BY id")
        )
        print(f"{'id':>4} {'name':<20} {'fmt':<5} {'nodes':>7}  created")
        for r in rows:
            print(f"{r[0]:>4} {r[1]:<20} {r[2]:<5} {r[3]:>7}  {r[4]}")
        for (case_id,) in con.execute("SELECT id FROM cases ORDER BY id"):
            fields = list(
                con.execute("SELECT name, min, max, mean FROM fields WHERE case_id = ?", (case_id,))
            )
            for name, lo, hi, mean in fields:
                print(f"       {name:<14} min={lo:<12.4g} max={hi:<12.4g} mean={mean:.4g}")
    finally:
        con.close()
    return 0


def cmd_serve(args) -> int:
    from ._app import app

    app.run(host=args.host, port=args.port, debug=False)
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="sim-post", description="FEA/CFD post-processor: field stats, sections, probes."
    )
    p.add_argument("--version", action="version", version=f"sim-post {VERSION}")
    sub = p.add_subparsers(dest="command", required=True)

    s = sub.add_parser("stats", help="min/max/mean per field of a result file")
    s.add_argument("file", help="CSV (x,y,z,field...) or VTK result file")
    s.add_argument("--format", choices=["csv", "vtk"], help="default: by file extension")
    s.add_argument("--json", action="store_true", help="also print the stats as JSON")
    s.set_defaults(func=cmd_stats)

    c = sub.add_parser("section", help="cut the mesh with an axis-aligned plane")
    c.add_argument("file")
    c.add_argument("--axis", choices=["x", "y", "z"], default="z")
    c.add_argument("--value", type=float, default=0.0, help="plane offset (tolerance 0.05)")
    c.add_argument("--limit", type=int, default=0, help="print at most N points")
    c.add_argument("--format", choices=["csv", "vtk"])
    c.set_defaults(func=cmd_section)

    r = sub.add_parser("probe", help="field values at the node nearest a point")
    r.add_argument("file")
    r.add_argument("x", type=float)
    r.add_argument("y", type=float)
    r.add_argument("z", type=float)
    r.add_argument("--format", choices=["csv", "vtk"])
    r.set_defaults(func=cmd_probe)

    e = sub.add_parser("cases", help="list the cases stored in the SQLite database")
    e.add_argument("--db", help="database file (default: instance/simpost.db)")
    e.set_defaults(func=cmd_cases)

    v = sub.add_parser("serve", help="run the Flask post-processing UI")
    v.add_argument("--host", default="127.0.0.1")
    v.add_argument("--port", type=int, default=8000)
    v.set_defaults(func=cmd_serve)
    return p


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":  # pragma: no cover - manual entry point
    raise SystemExit(main())
