# Caso de estudio demostrativo: Control de vencimientos
**Sector:** droguerías. **Servicio:** automatización operativa e IA generativa. **Estado:** prototipo con datos sintéticos.

## Problema → solución
Prioriza lotes usando vencimientos, demanda compartida y exposición económica estimada.
El flujo conserva evidencia de hallazgos, genera un resumen opcional y registra la revisión del responsable.

## Resultado verificable
La evaluación `python scripts/evaluate.py` compara los códigos detectados con cuatro escenarios esperados. Las pruebas incluyen entradas inválidas, persistencia, API y degradación de IA. Ver `validation.md` para la ejecución realizada.
El éxito en este conjunto pequeño no representa precisión sobre documentos reales ni reducción de tiempo de un cliente.

## Medición de piloto
1. Seleccionar una muestra representativa y registrar volumen, dificultad y excepciones.
2. Medir tiempo manual y asistido sobre casos equivalentes; incluir correcciones y revisión humana.
3. Comparar con etiquetas verificadas por un responsable: precisión y cobertura por tipo de hallazgo.
4. Reportar mediana, percentil 90, falsos positivos y falsos negativos. Separar casos sin evidencia suficiente.
5. Medir costo de IA y porcentaje de borradores corregidos. Evaluar fidelidad de cada afirmación a sus fuentes.

Ahorro de tiempo (%) = (tiempo manual − tiempo asistido) / tiempo manual × 100.
Las cifras de pérdidas evitadas requieren seguimiento del inventario y evidencia de resultados posteriores.

## Texto de tarjeta web
Droguerías · Control de vencimientos · Revisión manual → análisis con evidencias y seguimiento → resultado del piloto pendiente de medición.
