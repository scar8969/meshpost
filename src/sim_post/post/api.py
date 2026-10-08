from ..models import Case, Field, db
from .fields import normalize, stats
from .loader import load_csv, load_vtk
from .sections import probe, section_cut

from flask import Blueprint, jsonify, request, abort
import os
from .. import paths

bp = Blueprint("post", __name__)
DATA_DIR = str(paths.DATA_DIR)
_cases = {}  # id -> parsed case dict (in-memory for simplicity)

@bp.post("/api/cases")
def upload():
    f = request.files.get("file")
    if not f:
        return jsonify({"error": "no file"}), 400
    fmt = request.form.get("format", "csv")
    os.makedirs(DATA_DIR, exist_ok=True)
    path = os.path.join(DATA_DIR, f.filename)
    f.save(path)
    try:
        case = load_csv(path) if fmt == "csv" else load_vtk(path)
    except Exception:
        return jsonify({"error": "parse failed"}), 400
    c = Case(name=request.form.get("name", f.filename), format=fmt, file_path=path,
             nodes=len(case["nodes"]), fields_json=str(list(case["fields"].keys())))
    db.session.add(c)
    db.session.flush()
    for name, values in case["fields"].items():
        st = stats(values)
        db.session.add(Field(case_id=c.id, name=name, min=st["min"], max=st["max"],
                             mean=st["mean"], data_json=str(normalize(values))))
    db.session.commit()
    _cases[c.id] = case
    return jsonify({"id": c.id, "nodes": c.nodes, "fields": list(case["fields"].keys())})

@bp.get("/api/cases/<int:cid>")
def get_case(cid):
    c = Case.query.get_or_404(cid)
    fields = [{"name": f.name, "min": f.min, "max": f.max, "mean": f.mean}
              for f in Field.query.filter_by(case_id=cid).all()]
    return jsonify({"id": c.id, "name": c.name, "nodes": c.nodes, "fields": fields})

@bp.get("/api/cases/<int:cid>/section")
def section(cid):
    case = _cases.get(cid)
    if not case:
        abort(404)
    return jsonify({"points": section_cut(case, request.args.get("axis", "z"),
                                          request.args.get("value", 0.5, type=float))})

@bp.get("/api/cases/<int:cid>/probe")
def probe_point(cid):
    case = _cases.get(cid)
    if not case:
        abort(404)
    return jsonify({"values": probe(case, request.args.get("x", 0, type=float),
                                    request.args.get("y", 0, type=float),
                                    request.args.get("z", 0, type=float))})

@bp.post("/api/reports")
def report():
    d = request.get_json(force=True, silent=True) or {}
    return jsonify({"report_id": 1, "url": f"/report/{d.get('case_id', 1)}"})
