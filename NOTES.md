== curl ==
# curl -F "file=@bracket.csv" -F "name=bracket_v2" -F "format=csv" http://127.0.0.1:5000/api/cases
# GET  /api/cases/1
# GET  /api/cases/1/section?axis=z&value=0.5
# GET  /api/cases/1/probe?x=0&y=0&z=0
# POST /api/reports  {"case_id":1}

== session plan ==
# Session 1: loader (CSV) + fields (stats/normalize) → tests
# Session 2: sections + probes → tests
# Session 3: api + web viewport (plotly) → screenshots (internship FEA data)
# Session 4: reports + compare → README → CI/Docker/Pages → tag
