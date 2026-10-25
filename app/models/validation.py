from datetime import date
from decimal import Decimal, InvalidOperation

def text(value, field):
    if not isinstance(value, str) or not value.strip() or len(value) > 200:
        raise ValueError(f'{field}: texto obligatorio, máximo 200 caracteres')
    return value.strip()

def number(value, field, integer=False):
    if isinstance(value, bool):
        raise ValueError(f'{field}: número inválido')
    try:
        n = Decimal(str(value))
    except (InvalidOperation, TypeError):
        raise ValueError(f'{field}: número inválido')
    if not n.is_finite() or n < 0 or (integer and n != int(n)):
        raise ValueError(f'{field}: debe ser no negativo' + (' y entero' if integer else ''))
    return int(n) if integer else n

def day(value):
    try:
        return date.fromisoformat(value)
    except (ValueError, TypeError):
        raise ValueError('Fecha inválida; usar AAAA-MM-DD')

def rows(value):
    if not isinstance(value, list) or not 1 <= len(value) <= 2000 or any(not isinstance(x, dict) for x in value):
        raise ValueError('Se requieren entre 1 y 2000 registros')
    return value
