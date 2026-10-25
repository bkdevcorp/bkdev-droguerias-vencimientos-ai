import csv
import io
import json
import os
import time
from http.server import BaseHTTPRequestHandler
from pathlib import Path
from app.services.analysis import analyze
from app.models.validation import text
from app.adapters.storage import Storage
from app.adapters.narrator import narrate

ROOT = Path(__file__).resolve().parents[2]

def make_handler(db_path=None):
    storage = Storage(db_path or os.environ.get('DB_PATH', ROOT/'var'/'demo.sqlite'))
    class Handler(BaseHTTPRequestHandler):
        def send(self, code, value, mime='application/json; charset=utf-8'):
            raw = json.dumps(value,ensure_ascii=False).encode() if mime.startswith('application/json') else value.encode()
            self.send_response(code)
            self.send_header('Content-Type',mime)
            self.send_header('Content-Length',str(len(raw)))
            self.send_header('X-Content-Type-Options','nosniff')
            self.send_header('Cache-Control','no-store')
            self.end_headers(); self.wfile.write(raw)
        def do_GET(self):
            try:
                if self.path=='/': return self.send(200,(ROOT/'app/views/index.html').read_text(),'text/html; charset=utf-8')
                if self.path=='/api/sample': return self.send(200,json.loads((ROOT/'data/sample.json').read_text()))
                if self.path=='/api/history': return self.send(200,storage.history())
                if self.path=='/api/health': return self.send(200,{'status':'ok'})
                if self.path.startswith('/api/export/'):
                    rid = int(self.path.rsplit('/',1)[1])
                    result = storage.get(rid)['result']
                    buf = io.StringIO(); w = csv.writer(buf)
                    w.writerow(['id','severity','code','message','source'])
                    for f in result['findings']:
                        cells = [str(f[k]) for k in ['id','severity','code','message','source']]
                        w.writerow(["'"+v if v.startswith(('=','+','-','@')) else v for v in cells])
                    return self.send(200,buf.getvalue(),'text/csv; charset=utf-8')
                return self.send(404,{'error':'Ruta no encontrada'})
            except (ValueError, LookupError) as e: return self.send(400,{'error':str(e)})
        def do_POST(self):
            try:
                # Solicitudes JSON de mismo origen; sin CORS para escrituras.
                origin = self.headers.get('Origin')
                if origin and origin != 'http://' + self.headers.get('Host',''):
                    return self.send(403,{'error':'Origen no permitido'})
                if self.headers.get('Content-Type','').split(';')[0] != 'application/json':
                    return self.send(415,{'error':'Usar application/json'})
                size = int(self.headers.get('Content-Length','0'))
                if not 0 < size <= 1_000_000: return self.send(413,{'error':'Límite de 1 MB'})
                payload = json.loads(self.rfile.read(size))
                if not isinstance(payload,dict): raise ValueError('Se requiere un objeto JSON')
                if self.path=='/api/analyze':
                    start = time.perf_counter()
                    result = analyze(payload)
                    result['narrative'] = narrate(result)
                    result['elapsed_ms'] = round((time.perf_counter()-start)*1000,2)
                    result['rules_version'] = 'rules-v1'
                    rid = storage.save(payload,result)
                    return self.send(200,{'id':rid,**result})
                if self.path=='/api/review':
                    storage.review(int(payload['id']),text(payload.get('reviewer'),'Responsable'),text(payload.get('note'),'Observación'))
                    return self.send(200,{'status':'revisado'})
                return self.send(404,{'error':'Ruta no encontrada'})
            except (ValueError, KeyError, TypeError) as e: return self.send(400,{'error':str(e)})
    return Handler
