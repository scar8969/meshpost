import csv
from typing import Any


def load_csv(path):
    nodes: list[Any] = []
    fields: dict[str, list[float]] = {}
    with open(path) as f:
        reader = csv.reader(f)
        header = next(reader)
        # header: x,y,z,field1,field2,...
        for row in reader:
            if len(row) < 4:
                continue
            nodes.append([float(row[0]), float(row[1]), float(row[2])])
            for i, name in enumerate(header[3:]):
                fields.setdefault(name, []).append(float(row[3 + i]))
    return {"nodes": nodes, "fields": fields}


def load_vtk(path):
    nodes, fields = [], {}
    with open(path) as f:
        lines = f.readlines()
    i = 0
    while i < len(lines) and "POINTS" not in lines[i]:
        i += 1
    if i >= len(lines):
        raise ValueError("no POINTS in vtk")
    n = int(lines[i].split()[1])
    coords: list[Any] = []
    i += 1
    while len(coords) < n:
        coords += [float(x) for x in lines[i].split()]
        i += 1
    nodes = [coords[j : j + 3] for j in range(0, 3 * n, 3)]
    # SCALARS fields
    while i < len(lines):
        if "SCALARS" in lines[i]:
            name = lines[i].split()[1]
            i += 2  # skip LOOKUP_TABLE
            vals: list[float] = []
            while i < len(lines) and len(vals) < n:
                vals += [float(x) for x in lines[i].split()]
                i += 1
            fields[name] = vals[:n]
        else:
            i += 1
    return {"nodes": nodes, "fields": fields}
