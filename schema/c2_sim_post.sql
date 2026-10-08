-- 📐 sim-post schema
CREATE TABLE cases(id INTEGER PRIMARY KEY, name TEXT, format TEXT DEFAULT 'csv', file_path TEXT, nodes INTEGER DEFAULT 0, fields_json TEXT DEFAULT '[]', created_at DATETIME);
CREATE TABLE fields(id INTEGER PRIMARY KEY, case_id INTEGER REFERENCES cases(id), name TEXT, min REAL DEFAULT 0, max REAL DEFAULT 0, mean REAL DEFAULT 0, data_json TEXT DEFAULT '[]');
