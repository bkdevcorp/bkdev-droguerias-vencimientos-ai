import sqlite3
import json
from pathlib import Path
from datetime import datetime, timezone

class Storage:
    def __init__(self, path):
        self.path = str(path)
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        with self.connect() as db:
            db.executescript("""CREATE TABLE IF NOT EXISTS runs (
                id INTEGER PRIMARY KEY, created TEXT NOT NULL, payload TEXT NOT NULL,
                result TEXT NOT NULL, status TEXT NOT NULL DEFAULT 'pendiente',
                reviewer TEXT, note TEXT);
                CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY, run_id INTEGER, created TEXT, event TEXT, detail TEXT);""")
    def connect(self):
        db = sqlite3.connect(self.path)
        db.row_factory = sqlite3.Row
        return db
    def save(self, payload, result):
        now = datetime.now(timezone.utc).isoformat()
        with self.connect() as db:
            c = db.execute('INSERT INTO runs(created,payload,result) VALUES(?,?,?)',
                           (now, json.dumps(payload), json.dumps(result)))
            rid = c.lastrowid
            db.execute('INSERT INTO events(run_id,created,event,detail) VALUES(?,?,?,?)',
                       (rid, now, 'analizado', 'rules-v1'))
        return rid
    def history(self):
        with self.connect() as db:
            return [dict(r) for r in db.execute('SELECT id,created,status,reviewer,note FROM runs ORDER BY id DESC LIMIT 100')]
    def get(self, rid):
        with self.connect() as db:
            r = db.execute('SELECT * FROM runs WHERE id=?', (rid,)).fetchone()
        if not r: raise LookupError('Análisis no encontrado')
        r = dict(r)
        r['payload'] = json.loads(r['payload'])
        r['result'] = json.loads(r['result'])
        return r
    def review(self, rid, reviewer, note):
        now = datetime.now(timezone.utc).isoformat()
        with self.connect() as db:
            c = db.execute("UPDATE runs SET status='revisado',reviewer=?,note=? WHERE id=? AND status='pendiente'", (reviewer,note,rid))
            if c.rowcount != 1: raise ValueError('Análisis inexistente o ya revisado')
            db.execute('INSERT INTO events(run_id,created,event,detail) VALUES(?,?,?,?)',
                       (rid,now,'revisado',json.dumps({'reviewer':reviewer,'note':note})))
