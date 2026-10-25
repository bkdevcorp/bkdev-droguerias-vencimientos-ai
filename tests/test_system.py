import copy
import json
import os
import tempfile
import threading
import unittest
import urllib.request
import urllib.error
from pathlib import Path
from unittest.mock import patch
from http.server import ThreadingHTTPServer
from app.services.analysis import analyze
from app.adapters.storage import Storage
from app.adapters.narrator import narrate
from app.controllers.http import make_handler
ROOT=Path(__file__).resolve().parents[1]
SAMPLE=json.loads((ROOT/'data/sample.json').read_text())

class SystemTests(unittest.TestCase):
    def test_golden(self):
        for case in json.loads((ROOT/'evals/golden.json').read_text()):
            with self.subTest(case=case['name']):
                self.assertEqual(sorted(f['code'] for f in analyze(case['input'])['findings']),sorted(case['expected_codes']))
    def test_invalid_date(self):
        data=copy.deepcopy(SAMPLE);data['as_of']='no-es-fecha'
        with self.assertRaises(ValueError):analyze(data)
    def test_negative_and_nonfinite(self):
        for bad in [-1,'NaN','Infinity',True,1.2]:
            data=copy.deepcopy(SAMPLE)
            data.get('receipt',data.get('inventory'))[0]['quantity']=bad
            with self.subTest(bad=bad), self.assertRaises(ValueError):analyze(data)
    def test_duplicates(self):
        data=copy.deepcopy(SAMPLE); key='receipt' if 'receipt' in data else 'inventory'
        data[key].append(data[key][0])
        with self.assertRaises(ValueError):analyze(data)
    def test_review_once_and_persistence(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/'db.sqlite';store=Storage(path);rid=store.save(SAMPLE,analyze(SAMPLE))
            store.review(rid,'Responsable','Verificado')
            self.assertEqual(Storage(path).get(rid)['status'],'revisado')
            with self.assertRaises(ValueError):store.review(rid,'Otro','Segunda revisión')
    def test_template(self):
        with patch.dict(os.environ,{'AI_MODE':'template'}):self.assertEqual(narrate(analyze(SAMPLE))['mode'],'plantilla')
    def test_ai_failure_falls_back(self):
        with patch.dict(os.environ,{'AI_MODE':'ollama'}),patch('urllib.request.urlopen',side_effect=OSError('offline')):
            self.assertIn('warning',narrate(analyze(SAMPLE)))
    def test_ai_rejects_fake_source(self):
        raw=json.dumps({'message':{'content':json.dumps({'text':'Borrador','sources':['INVENTADA']})}}).encode()
        with patch.dict(os.environ,{'AI_MODE':'ollama'}),patch('urllib.request.urlopen') as call:
            call.return_value.__enter__.return_value.read.return_value=raw
            self.assertEqual(narrate(analyze(SAMPLE))['mode'],'plantilla')
    def test_http(self):
        with tempfile.TemporaryDirectory() as tmp:
            server=ThreadingHTTPServer(('127.0.0.1',0),make_handler(Path(tmp)/'db.sqlite'))
            thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
            base=f'http://127.0.0.1:{server.server_port}'
            def request(path,data=None):
                req=urllib.request.Request(base+path,data=None if data is None else json.dumps(data).encode(),headers={'Content-Type':'application/json'})
                return urllib.request.urlopen(req)
            try:
                self.assertEqual(request('/api/health').status,200)
                self.assertIn(b'<!doctype html>',request('/').read())
                with patch.dict(os.environ,{'AI_MODE':'template'}):r=json.load(request('/api/analyze',SAMPLE))
                self.assertIn(b'code',request('/api/export/'+str(r['id'])).read())
                self.assertEqual(len(json.load(request('/api/history'))),1)
                self.assertEqual(json.load(request('/api/review',{'id':r['id'],'reviewer':'Ana','note':'Validado'}))['status'],'revisado')
                with self.assertRaises(urllib.error.HTTPError):request('/api/analyze',{'as_of':'bad'})
            finally:server.shutdown();server.server_close();thread.join()
