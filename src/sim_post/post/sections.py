def section_cut(case, axis, value):
    """Slice nodes where axis == value (nearest), return (x, y, field_val)."""
    idx = {"x": 0, "y": 1, "z": 2}[axis]
    points = []
    for node, field in zip(
        case["nodes"],
        case["fields"].get("vonMises", case["fields"].get(list(case["fields"].keys())[0], [])),
    ):
        if abs(node[idx] - value) < 0.05:
            points.append([node[0], node[1], field])
    return points


def probe(case, x, y, z):
    """Nearest node."""
    best, best_d = None, float("inf")
    for node in case["nodes"]:
        d = (node[0] - x) ** 2 + (node[1] - y) ** 2 + (node[2] - z) ** 2
        if d < best_d:
            best_d = d
            best = node
    out = {"node": best}
    for name, vals in case["fields"].items():
        i = case["nodes"].index(best)
        out[name] = vals[i]
    return out
