"""Adaptador optativo Ollama. Las salidas son borradores, nunca decisiones."""
import json
import os
import urllib.request
import urllib.error
from pathlib import Path

PROMPT = Path(__file__).resolve().parents[2] / 'prompts' / 'summary.txt'

def narrate(result):
    findings = result['findings']
    fallback = {'mode':'plantilla', 'text':f"Se detectaron {len(findings)} observaciones. Revise las evidencias y registre su decisión.",
                'sources':[f['id'] for f in findings], 'prompt_version':'summary-v1'}
    if os.environ.get('AI_MODE', 'template') != 'ollama': return fallback
    try:
        request = urllib.request.Request(
            os.environ.get('OLLAMA_URL','http://127.0.0.1:11434') + '/api/chat',
            data=json.dumps({'model':os.environ.get('OLLAMA_MODEL','qwen2.5:7b'),
                'stream':False, 'format':'json', 'options':{'temperature':0},
                'messages':[{'role':'system','content':PROMPT.read_text()},
                            {'role':'user','content':json.dumps(result,ensure_ascii=False)}]}).encode(),
            headers={'Content-Type':'application/json'})
        with urllib.request.urlopen(request, timeout=30) as response:
            raw = response.read(262145)
        if len(raw)>262144: raise ValueError('Salida demasiado grande')
        value = json.loads(json.loads(raw)['message']['content'])
        ids = {f['id'] for f in findings}
        if not isinstance(value,dict) or not isinstance(value.get('text'),str) or not 1 <= len(value['text']) <= 4000:
            raise ValueError('Esquema inválido')
        sources = value.get('sources')
        if not isinstance(sources,list) or any(not isinstance(s,str) or s not in ids for s in sources) or (ids and not sources):
            raise ValueError('Fuentes inválidas')
        return {'mode':'ollama','text':value['text'],'sources':sources,
                'prompt_version':'summary-v1','review_required':True}
    except (OSError, ValueError, KeyError, TypeError, urllib.error.URLError):
        return {**fallback, 'warning':'IA no disponible o salida inválida; se utilizó plantilla.'}
