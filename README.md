# BKDev · Control de vencimientos
Demostrador de automatización e IA generativa para droguerías, con datos sintéticos y revisión humana.

## Ejecutar
Python 3.12 o superior. Sin dependencias externas de runtime.
```bash
python run.py
```
Abre http://127.0.0.1:8002. Carga el ejemplo o importa un archivo JSON, analiza, revisa las evidencias, exporta CSV y registra la revisión. El historial se guarda en `var/demo.sqlite`.

```bash
python -m unittest discover -s tests -v
python scripts/evaluate.py
```

## IA generativa opcional
Por defecto funciona con una plantilla explícitamente identificada. Para narración con un modelo local, instala Ollama por separado y descarga el modelo elegido. Configura en la terminal antes de iniciar:
```bash
export AI_MODE=ollama
export OLLAMA_URL=http://127.0.0.1:11434
export OLLAMA_MODEL=qwen2.5:7b
python run.py
```
En PowerShell usa `$env:AI_MODE="ollama"`, etc. Se usa `POST /api/chat`, JSON no streaming, timeout 30 s y prompt versionado. No se incluye una suscripción ni un modelo dentro del proyecto. Las referencias se validan por id; toda narración requiere revisión semántica humana. El proveedor de IA no decide ni escribe inventario. Si falla, se conserva el análisis y se muestra una plantilla.

## Docker
```bash
docker build -t bkdev-vencimientos .
docker run --rm -p 127.0.0.1:8002:8002 -v bkdev-vencimientos-data:/app/var bkdev-vencimientos
```
Para persistencia con volumen verifica permisos del usuario `demo`. El endpoint Ollama requiere configuración de red específica desde contenedores. El demo sin IA no requiere conexiones externas.

## Contrato de inventario
`inventory`: `{sku, lot, quantity, unit_cost, expiry, status}`. `monthly_demand`: unidades/mes por SKU. `as_of`: fecha ISO explícita.
`status`: `available` o `blocked`. Costo unitario expresado en PEN. Lotes únicos por SKU; consolidar almacenes antes de cargar.
Demanda lineal aproximada con meses de 30 días. Se distribuye una sola vez por SKU en orden FEFO. Stock bloqueado o vencido no consume demanda elegible.
Exposición = remanente estimado × costo; incluye stock bloqueado y vencido. Es una estimación de exposición, no pérdida confirmada ni ahorro.
90 días es umbral de alerta ilustrativo. No ejecuta despachos, devoluciones ni cambios de ERP.

## API
- `GET /api/sample`: ejemplo sintético.
- `POST /api/analyze`: analiza JSON y guarda ejecución.
- `GET /api/history`: últimas 100 revisiones.
- `POST /api/review`: `{id, reviewer, note}`; una sola revisión por ejecución.
- `GET /api/export/ID`: observaciones CSV.
- `GET /api/health`: estado.

## Harness y arquitectura
MVC con servicios y adaptadores: [arquitectura](docs/architecture.md), [instrucciones del agente](AGENTS.md), [caso de estudio](docs/case-study.md), golden dataset en `evals/` y CI en `.github/workflows/`.

Primera versión local: sin autenticación, OCR, integraciones de ERP ni certificación de cumplimiento normativo. Preparar identidad, roles, infraestructura y revisión sectorial antes de un uso real. No contiene datos de clientes ni resultados comerciales atribuidos.
