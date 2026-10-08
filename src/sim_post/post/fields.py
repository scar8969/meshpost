def stats(values):
    return {"min": min(values), "max": max(values), "mean": sum(values) / len(values)}

def normalize(values):
    lo, hi = min(values), max(values)
    span = hi - lo or 1
    return [round((v - lo) / span, 4) for v in values]
