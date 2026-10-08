"""C2 sim-post — tests. Run: pytest test_c2_sim_post.py"""
import sys, os

import pytest

CSV = "x,y,z,vonMises,Sx\n0,0,0,10,5\n1,0,0,20,10\n0,1,0,30,15\n1,1,0,40,20\n"

def test_load_csv(tmp_path):
    from sim_post.post.loader import load_csv
    p = tmp_path / "case.csv"
    p.write_text(CSV)
    case = load_csv(str(p))
    assert len(case["nodes"]) == 4
    assert case["fields"]["vonMises"] == [10, 20, 30, 40]

def test_stats():
    from sim_post.post.fields import stats
    assert stats([1, 2, 3]) == {"min": 1, "max": 3, "mean": 2}

def test_normalize():
    from sim_post.post.fields import normalize
    assert normalize([0, 5, 10]) == [0.0, 0.5, 1.0]

def test_section_cut():
    from sim_post.post.sections import section_cut
    case = {"nodes": [[0, 0, 0], [1, 0, 0], [0, 1, 0]],
            "fields": {"vonMises": [10, 20, 30]}}
    pts = section_cut(case, "z", 0)
    assert len(pts) == 3  # all nodes at z=0

def test_probe():
    from sim_post.post.sections import probe
    case = {"nodes": [[0, 0, 0], [1, 0, 0]],
            "fields": {"vonMises": [10, 20]}}
    out = probe(case, 0.9, 0, 0)
    assert out["node"] == [1, 0, 0]
    assert out["vonMises"] == 20
