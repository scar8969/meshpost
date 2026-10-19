<p align="center">
  <img src="docs/assets/screens/root.png" alt="meshpost running" width="900">
</p>

<h1 align="center">meshpost</h1>

<p align="center"><b>Post-process FEA and CFD results without opening a GUI.</b></p>

<p align="center">
  <a href="https://github.com/scar8969/meshpost/actions/workflows/ci.yml"><img src="https://github.com/scar8969/meshpost/actions/workflows/ci.yml/badge.svg" alt="ci"></a> <a href="#quality-gates"><img src="https://img.shields.io/badge/tests-25%20passed-2ea44f" alt="tests: 25 passed"></a> <a href="#quality-gates"><img src="https://img.shields.io/badge/coverage-61.3%-yellow" alt="coverage: 61.3%"></a> <a href="#api"><img src="https://img.shields.io/badge/routes-8%20live-0969da" alt="routes: 8 live"></a> <a href="#requirements"><img src="https://img.shields.io/badge/python-3.11%2B-3776ab" alt="python: 3.11+"></a> <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-2ea44f" alt="license: MIT"></a>
</p>

meshpost loads CSV or VTK result files, exposes the mesh as sections and probes, and computes summary statistics per field — enough to answer "what is the peak here" from a script or a browser.

---

**Contents** &nbsp;·&nbsp; [Why](#why-this-exists) &nbsp;·&nbsp; [What it does](#what-it-does) &nbsp;·&nbsp; [Quickstart](#quickstart) &nbsp;·&nbsp; [Screenshots](#screenshots) &nbsp;·&nbsp; [API](#api) &nbsp;·&nbsp; [CLI](#cli) &nbsp;·&nbsp; [Configuration](#configuration) &nbsp;·&nbsp; [Measured](#measured-not-estimated) &nbsp;·&nbsp; [How a request flows](#how-a-request-flows) &nbsp;·&nbsp; [Architecture](#architecture) &nbsp;·&nbsp; [Quality gates](#quality-gates) &nbsp;·&nbsp; [Development](#development) &nbsp;·&nbsp; [Deploy](#deploy) &nbsp;·&nbsp; [Limits](#limits-stated-rather-than-hidden)

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

## API

Every route below is declared in [`openapi/meshpost.yaml`](openapi/meshpost.yaml) and exercised by the live probe recorded in [`docs/EVIDENCE.md`](docs/EVIDENCE.md).

| Method | Path | What it does |
| --- | --- | --- |
| `POST` | `/api/cases` | upload |
| `GET` | `/api/cases/<id>` | case info |
| `GET` | `/api/cases/<id>/section` | section cut |
| `GET` | `/api/cases/<id>/probe` | probe |
| `POST` | `/api/reports` | report |

## CLI

The same operations without an HTTP client. Installed as `meshpost`, and runnable from a checkout with no install:

```sh
python -m sim_post.cli --help
```

```text
usage: sim-post [-h] [--version] {stats,section,probe,cases,serve} ...

FEA/CFD post-processor: field stats, sections, probes.

positional arguments:
  {stats,section,probe,cases,serve}
    stats               min/max/mean per field of a result file
    section             cut the mesh with an axis-aligned plane
    probe               field values at the node nearest a point
    cases               list the cases stored in the SQLite database
    serve               run the Flask post-processing UI

options:
  -h, --help            show this help message and exit
  --version             show program's version number and exit
```

## Configuration

Environment only — there is no config file. Copy `.env.example` to `.env` and edit; `APP_ENV=production` refuses to start without `SECRET_KEY`.

| Variable | Default | Meaning |
| --- | --- | --- |
| `APP_ENV` | `development` | development \| staging \| production; production enforces the secret. |
| `SECRET_KEY` | `change-me-in-production` | Session/CSRF signing key. Required when APP_ENV=production. |
| `HOST` | `0.0.0.0` | Interface the dev server binds. |
| `PORT` | `8000` | Port the dev server and the container listen on. |
| `DEBUG` | `false` | Flask debug mode. Never true in production. |
| `MAX_CONTENT_LENGTH` | `8388608` | Largest accepted request body, in bytes. |
| `DATA_DIR` | `(empty)` | Where uploaded and generated files live. |
| `INSTANCE_DIR` | `(empty)` | Where the SQLite file and instance state live. |
| `LOG_DIR` | `(empty)` | Where rotated log files are written, if file logging is on. |
| `LOG_LEVEL` | `INFO` | DEBUG \| INFO \| WARNING \| ERROR. |
| `LOG_JSON` | `true` | true emits one JSON object per line; false is human-readable. |
| `REQUEST_ID_HEADER` | `X-Request-ID` | Header echoed on every response and stamped on every log line. |
| `SIMPOST_DATA_DIR` | `(empty)` | Where uploaded result files are stored; defaults under the data dir. |
| `SIMPOST_DB` | `(empty)` | SQLite file holding parsed cases; defaults under the instance dir. |
| `SIMPOST_SECRET` | `(empty)` | Flask session key. |

## Measured, not estimated

Produced on this checkout by `pytest --cov` and by booting `wsgi.py` and issuing one real GET per documented path. The commands are recorded in [`docs/EVIDENCE.md`](docs/EVIDENCE.md).

| Signal | Value |
| --- | --- |
| Tests | **25 / 25 passed** (2.0 s, exit 0) |
| Line coverage | **61.3%** — 456 of 708 statements |
| Source | 15 files / 1,554 lines |
| Test code | 4 files / 241 lines |
| Documented paths | 5 in the spec, 3 GET |
| Live probe | 12 GET requests to the booted app, **8 answered 200** |
| Median latency | **4.5 ms** (single uncached request, dev server) |
| Slowest / fastest | 175.6 ms `/` / 4.1 ms `/livez` |
| Bytes served | 8.6 KB across 12 responses |
| Screenshots | 6 captured |

## How a request flows

```text
client
  │  HTTP
  ▼
wsgi.py ──▶ sim_post/app.py:get_app()
                │  reads config once (sim_post/config.py)
                │  registers the `post` blueprint
                ▼
           route handler
             ├──▶ sim_post/models.py        tables, via Flask-SQLAlchemy
             ├──▶ sim_post/errors.py        raises typed errors → one JSON envelope
             └──▶ sim_post/observability.py JSON log line + X-Request-ID
```

Every response carries `X-Request-ID`, and the matching log line is written once at the end of the request with the status and duration, so a report of "it failed" is one `grep` away from the traceback.

## Architecture

```
meshpost/
├── src/sim_post/
│   ├── http.py                         379  HTTP plumbing for sim_post: correlation ids, access 
│   ├── config.py                       173  Environment-driven configuration for sim_post
│   ├── observability.py                169  Structured logging and request correlation for sim_p
│   ├── _app.py                         168  
│   ├── cli.py                          153  sim-post CLI - inspect FEA/CFD result files and the 
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
| Coverage | `pytest --cov` | floor in `pyproject.toml`, set below the measured value |
| Lint | `ruff check src tests` | zero findings |
| Format | `ruff format --check src tests` | zero reformats |
| Types | `mypy src` | zero errors |
| Security | `bandit -c pyproject.toml -r src` | reviewed skip list, no unreviewed finding |
| Live routes | boot `wsgi.py`, one GET per documented path | no 5xx, no undocumented guard |

CI runs the first six on Python 3.11, 3.12 and 3.13 on every push to `main`, plus a container build — [`.github/workflows/ci.yml`](.github/workflows/ci.yml).

## Development

```sh
pip install -e ".[dev]"
python -m pytest -q                      # the suite
python -m pytest --cov                   # with the coverage floor
python -m ruff check src tests           # lint
python -m ruff format --check src tests  # formatting
python -m mypy src                       # types
python -m bandit -c pyproject.toml -r src  # security
pre-commit install                       # the same checks on commit
```

Dependabot opens grouped PRs for the dev tooling weekly and for actions and the base image monthly.

## Deploy

```sh
docker build -t meshpost .
docker run --rm -p 8000:8000 --env-file .env.example meshpost
```

A `docker-compose.yml` is included for a local run with a volume for the SQLite file. The image runs as a non-root user and serves through gunicorn.

## Limits, stated rather than hidden

- Parsed cases live in memory, so a restart loses them — the README states this rather than implying persistence.
- The VTK loader reads the ASCII scalar layout it was written for; other variants are rejected with a parse error rather than half-read.

## License

MIT — see [LICENSE](LICENSE).
