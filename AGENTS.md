# Instrucciones de desarrollo
Lee README.md y docs/architecture.md antes de editar.
Mantén MVC: controllers HTTP, models validaciones, services reglas, adapters infraestructura, views presentación.
No mezcles cálculos de negocio con narración LLM. Nunca hagas que un LLM acepte mercadería o libere stock.
Datos solo sintéticos. No añadir secretos ni bases SQLite al repositorio.
Todo cambio de reglas requiere casos positivos, negativos y de borde; actualiza evals/golden.json.
Ejecuta python -m unittest discover -s tests -v y python scripts/evaluate.py.
Versiona prompts y reglas; registra fuentes y conserva eventos de revisión.
Las cifras de tiempos ahorrados o pérdidas evitadas necesitan medición con usuarios; no inventarlas.
