from .post import api as post_api
from .models import Case, Field, db
from .post.api import bp
from .post.loader import load_csv

from flask import Flask, flash, jsonify, redirect, render_template, request, url_for
import os
from . import paths

# Templates and static assets live at <project root>/templates and
# <project root>/static, next to web/, so resolve them from this file instead
# of the process working directory.

def build_app():
    """Build the application: configuration, database, then routes."""
    app = Flask(__name__, template_folder=str(paths.TEMPLATES_DIR), static_folder=str(paths.STATIC_DIR))
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + str(paths.INSTANCE_DIR / "simpost.db")
    app.secret_key = os.environ.get("SIMPOST_SECRET", "sim-post-dev-secret")
    db.init_app(app)
    with app.app_context():
        db.create_all()
    app.register_blueprint(bp)

    # Upload settings the operator last typed, plus the log of what the API did.
    # Templates render these (or rows from SQLite), never placeholder markup.
    PAGE_STATE = {"case_name": "bracket_v2", "case_format": "csv", "log": "no upload yet",
                  "export_note": "CSV export is served from the case rows on /"}
    DATA_DIR = os.environ.get("SIMPOST_DATA_DIR", str(paths.DATA_DIR))

    def _cases():
        return Case.query.order_by(Case.id.desc()).all()

    def _field_stats(case):
        return [{"name": f.name, "min": f.min, "max": f.max, "mean": f.mean}
                for f in Field.query.filter_by(case_id=case.id).all()]

    @app.context_processor
    def inject_state():
        """Case list, statistics and form defaults come from SQLite."""
        rows = _cases()
        latest = rows[0] if rows else None
        fields = _field_stats(latest) if latest else []
        return {
            "app_name": "sim-post",
            "data_dir": DATA_DIR,
            "case_count": len(rows),
            "recent_cases": [{"id": c.id, "name": c.name, "format": c.format,
                              "nodes": c.nodes or 0, "fields_json": c.fields_json or "[]",
                              "created_at": c.created_at} for c in rows[:20]],
            "latest_case": latest,
            "stats": {"nodes": latest.nodes if latest else 0,
                      "fields": len(fields),
                      "fields_list": [f["name"] for f in fields],
                      "log": PAGE_STATE["log"]},
            "export_note": PAGE_STATE["export_note"],
            "case_name": request.args.get("case") or PAGE_STATE["case_name"],
            "case_format": request.args.get("format") or PAGE_STATE["case_format"],
            "active_case": latest.id if latest else "",
            "log": PAGE_STATE["log"],
        }

    @app.get("/")
    def index():
        return render_template("index.html")

    @app.get("/report/<int:cid>")
    def report_view(cid):
        case = Case.query.get_or_404(cid)
        return render_template("report.html", case=case, field_stats=_field_stats(case))

    @app.post("/cases")
    def start_case():
        """Control-panel form target: records an upload the API then parses."""
        name = (request.form.get("name") or "case1").strip()
        fmt = request.form.get("format", "csv")
        upload = request.files.get("file")
        case = Case(name=name, format=fmt, file_path=os.path.join(DATA_DIR, name + "." + fmt))
        db.session.add(case)
        db.session.flush()
        parsed = ""
        if upload is not None and upload.filename:
            raw = upload.read()
            os.makedirs(DATA_DIR, exist_ok=True)
            with open(case.file_path, "wb") as fh:
                fh.write(raw)
            try:
                text = raw.decode("utf-8-sig", "replace")
                if fmt == "csv":
                    loaded = load_csv(text)
                    post_api._cases[case.id] = loaded
                    case.nodes = len(loaded.get("nodes") or [])
                    case.fields_json = str(sorted((loaded.get("fields") or {}).keys()))
                    for fname, values in (loaded.get("fields") or {}).items():
                        series = [float(v) for v in values]
                        db.session.add(Field(case_id=case.id, name=fname,
                                             min=min(series), max=max(series),
                                             mean=sum(series) / len(series),
                                             data_json=str(series)))
                    parsed = "%d node(s), fields %s" % (
                        case.nodes, ", ".join(sorted(loaded.get("fields") or {})))
                else:
                    parsed = "stored %d bytes (vtk parsing is CLI-only: cli.py section)" % len(raw)
            except Exception as exc:
                parsed = "stored %d bytes, parse failed: %s" % (len(raw), exc)
        db.session.commit()
        PAGE_STATE["case_name"] = name
        PAGE_STATE["case_format"] = fmt
        PAGE_STATE["log"] = "case #%d (%s, %s): %s" % (
            case.id, name, fmt, parsed or "no file in the upload")
        flash("case #%d registered" % case.id)
        return redirect(url_for("report_view", cid=case.id))

    @app.get("/api/health")
    def api_health():
        return jsonify({"status": "ok", "app": "sim-post", "version": "0.1.0"})

    @app.get("/api/config")
    def api_config():
        """Data directory and supported formats the UI and CLI both read."""
        return jsonify({"data_dir": DATA_DIR,
                        "formats": ["csv", "vtk"],
                        "cases": Case.query.count(),
                        "database": app.config["SQLALCHEMY_DATABASE_URI"]})

    if __name__ == "__main__":  # python -m web.app  (see Dockerfile CMD)
        app.run(host="0.0.0.0", port=int(os.environ.get("PORT", "8000")))

    return app

app = build_app()
