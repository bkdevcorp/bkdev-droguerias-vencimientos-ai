# Validación realizada

Python 3.12.14.
- `python -m unittest discover -s tests -v`: 11 pruebas aprobadas.
- `python scripts/evaluate.py`: 4/4 escenarios sintéticos aprobados.
- `node --check`: sintaxis del JavaScript válida.
- HTTP real en puerto temporal: carga HTML, análisis, historial, exportación, revisión y entrada inválida.

El adaptador Ollama se verificó con respuestas simuladas, fallos de conexión y referencias inexistentes. No se ejecutó un modelo real ni se midió calidad generativa. Docker, extracción PDF opcional y revisión visual en navegador no se ejecutaron en este entorno.

Documentación del contrato Ollama: https://docs.ollama.com/api/chat

Las cifras anteriores son pruebas del software; no son precisión comercial ni ahorro de un cliente.
