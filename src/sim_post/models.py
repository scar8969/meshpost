from datetime import datetime

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Case(db.Model):
    __tablename__ = "cases"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), default="")
    format = db.Column(db.String(8), default="csv")
    file_path = db.Column(db.String(256), default="")
    nodes = db.Column(db.Integer, default=0)
    fields_json = db.Column(db.Text, default="[]")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Field(db.Model):
    __tablename__ = "fields"
    id = db.Column(db.Integer, primary_key=True)
    case_id = db.Column(db.Integer, db.ForeignKey("cases.id"))
    name = db.Column(db.String(64), default="")
    min = db.Column(db.Float, default=0.0)
    max = db.Column(db.Float, default=0.0)
    mean = db.Column(db.Float, default=0.0)
    data_json = db.Column(db.Text, default="[]")  # normalized 0..1 per node
