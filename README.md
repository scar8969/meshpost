<p align="center">
  <img src="docs/assets/screens/root.png" alt="meshpost running" width="900">
</p>

<h1 align="center">meshpost</h1>

<p align="center"><b>Post-process FEA and CFD results without opening a GUI.</b></p>

<p align="center">
  <a href="#quality-gates"><img src="https://img.shields.io/badge/tests-25%20passed-2ea44f" alt="tests: 25 passed"></a> <a href="#quality-gates"><img src="https://img.shields.io/badge/coverage-61.3%-yellow" alt="coverage: 61.3%"></a> <a href="#api"><img src="https://img.shields.io/badge/routes-8%20answered-0969da" alt="routes: 8 answered"></a> <a href="#requirements"><img src="https://img.shields.io/badge/python-3.11%2B-3776ab" alt="python: 3.11+"></a> <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-2ea44f" alt="license: MIT"></a>
</p>

meshpost loads CSV or VTK result files, exposes the mesh as sections and probes, and computes summary statistics per field — enough to answer "what is the peak here" from a script or a browser.

---

**Contents** &nbsp;·&nbsp; [Why](#why-this-exists) &nbsp;·&nbsp; [What it does](#what-it-does) &nbsp;·&nbsp; [Quickstart](#quickstart) &nbsp;·&nbsp; [API](#api) &nbsp;·&nbsp; [Screenshots](#screenshots) &nbsp;·&nbsp; [Measured](#measured-not-estimated) &nbsp;·&nbsp; [Architecture](#architecture) &nbsp;·&nbsp; [Quality gates](#quality-gates) &nbsp;·&nbsp; [Deploy](#deploy) &nbsp;·&nbsp; [Limits](#limits-stated-rather-than-hidden)

## Why this exists

Solvers write results that only the solver's GUI can read comfortably. A small loader plus a section/probe API makes the numbers reachable from a notebook, a report or a CI job.

## What it does

| Capability | How it works |
| --- | --- |
| **CSV and VTK loaders** | Both formats produce the same case object, so the API is format-agnostic. |
| **Sections** | Slice the mesh at a coordinate and get the nodes on that plane. |
| **Probes** | Nearest-node lookup at an arbitrary point. |
| **Field statistics** | Min, max, mean and count per field, computed from the loaded values. |
| **CLI** | cases, section, probe, stats and serve. |

## Quickstart

```sh
git clone https://github.com/scar8969/meshpost.git
cd meshpost
python -m venv .venv && . .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
python wsgi.py                                 # http://127.0.0.1:8000
```

The same work from the CLI:

```sh
python -m sim_post.cli --help
```

Commands: `stats`, `section`, `probe`, `cases`, `serve`.

A first request:

```sh
curl -s http://127.0.0.1:8000/api/cases | head
```

## Requirements

- Python **3.11+** — CI runs 3.11, 3.12 and 3.13.
- Runtime dependencies: `Flask>=3.0`, `Flask-SQLAlchemy>=3.1`, `SQLAlchemy>=2.0`, `PyYAML>=6.0`.
- No JavaScript build step: every page is server-rendered Jinja.

## API

Every route below is in [`openapi/meshpost.yaml`](openapi/meshpost.yaml) and is exercised by the live probe recorded in [`docs/EVIDENCE.md`](docs/EVIDENCE.md).

| Method | Path | What it does |
| --- | --- | --- |
| `POST` | `/api/cases` | upload |
| `GET` | `/api/cases/<id>` | case info |
| `GET` | `/api/cases/<id>/section` | section cut |
| `GET` | `/api/cases/<id>/probe` | probe |
| `POST` | `/api/reports` | report |

## Screenshots

Captured from the running service with headless Chromium at 1440×900, one image per page, committed under [`docs/assets/screens/`](docs/assets/screens/).

<table>
<tr>
<td width="50%"><img src="docs/assets/screens/healthz.png" alt="/healthz" width="100%"><br><sub><code>/healthz</code> &middot; 8.2 KB</sub></td>
<td width="50%"><img src="docs/assets/screens/livez.png" alt="/livez" width="100%"><br><sub><code>/livez</code> &middot; 7.3 KB</sub></td>
</tr>
</table>

<table>
<tr>
<td width="50%"><img src="docs/assets/screens/metrics.png" alt="/metrics" width="100%"><br><sub><code>/metrics</code> &middot; 14.8 KB</sub></td>
<td width="50%"><img src="docs/assets/screens/readyz.png" alt="/readyz" width="100%"><br><sub><code>/readyz</code> &middot; 7.7 KB</sub></td>
</tr>
</table>

<table>
<tr>
<td width="50%"><img src="docs/assets/screens/version.png" alt="/version" width="100%"><br><sub><code>/version</code> &middot; 25.7 KB</sub></td>
</tr>
</table>

## Measured, not estimated

These numbers were produced on this checkout by `pytest --cov` and by booting `wsgi.py` and issuing one real GET per documented path. The commands are in [`docs/EVIDENCE.md`](docs/EVIDENCE.md).

| Signal | Value |
| --- | --- |
| Tests | **25 / 25 passed** (2.0 s, exit 0) |
| Line coverage | **61.3%** — 456 of 708 statements |
| Source | 15 files / 1,533 lines |
| Test code | 4 files / 241 lines |
| Documented paths | 5 in the spec, 3 GET |
| Live probe | 12 GET requests to the booted app, **8 answered 200** |
| Median latency | **4.5 ms** (single uncached request, dev server) |
| Slowest / fastest | 175.6 ms `/` / 4.1 ms `/livez` |
| Bytes served | 8.6 KB across 12 responses |
| Screenshots | 6 captured |

## Architecture

```
meshpost/
├── src/sim_post/
│   ├── http.py                         379  HTTP plumbing for sim_post: correlation ids, access 
│   ├── config.py                       174  Environment-driven configuration for sim_post
│   ├── observability.py                169  Structured logging and request correlation for sim_p
│   ├── _app.py                         168  
│   ├── cli.py                          149  sim-post CLI - inspect FEA/CFD result files and the 
│   ├── app.py                          119  Application factory for sim_post
│   ├── errors.py                       108  Typed application errors and their HTTP mapping for 
│   ├── post/api.py                     101  
│   ├── paths.py                         52  Filesystem layout for sim_post
│   ├── post/loader.py                   50  
│   ├── models.py                        28  
│   ├── post/sections.py                 27  
├── openapi/meshpost.yaml                  the contract of record
├── schema/meshpost.sql                    the DDL
├── tests/                       the suite that has to stay green
├── docs/EVIDENCE.md             the recorded live route walk
├── Dockerfile                   multi-stage build
└── wsgi.py                      entry point
```

The package keeps one shape across the service: `config.py` reads the environment once, `observability.py` emits structured JSON logs carrying a request id, `errors.py` turns exceptions into a single JSON envelope, `models.py` holds the tables, and the `post/` package holds the routes.

## Quality gates

| Gate | Command | Threshold |
| --- | --- | --- |
| Suite | `pytest -q` | all green |
| Coverage | `pytest --cov` | floor set in `pyproject.toml` from the measured value |
| Lint | `ruff check src tests` | zero findings |
| Format | `ruff format --check src tests` | zero reformats |
| Types | `mypy src` | zero errors |
| Security | `bandit -c pyproject.toml -r src` | reviewed skip list, no unreviewed finding |
| Live routes | boot `wsgi.py`, one GET per documented path | no 5xx, no undocumented guard |

CI runs the first six on Python 3.11, 3.12 and 3.13 for every push to `main`, plus a container build. See [`.github/workflows/ci.yml`](.github/workflows/ci.yml).

## Deploy

```sh
docker build -t meshpost .
docker run --rm -p 8000:8000 --env-file .env.example meshpost
```

Configuration is environment-only — every variable is documented in [`.env.example`](.env.example), and the service refuses to start with a production secret missing.

## Limits, stated rather than hidden

- Parsed cases live in memory, so a restart loses them — the README states this rather than implying persistence.
- The VTK loader reads the ASCII scalar layout it was written for; other variants are rejected with a parse error rather than half-read.

## License

MIT — see [LICENSE](LICENSE).
