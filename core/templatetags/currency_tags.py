from django import template
from decimal import Decimal

register = template.Library()

@register.filter
def format_cop(value):
    """
    Formatea un número como pesos colombianos (COP).
    Ejemplo: 1234567.89 -> "COP 1.234.567"
    """
    if value is None:
        return "COP 0"
    
    try:
        # Convertir a float
        num = float(value)
        # Redondear sin decimales (pesos colombianos no tienen centavos mostrados)
        num = int(round(num))
        # Formato con miles separados por puntos
        formatted = f"{num:,}".replace(",", ".")
        return f"COP {formatted}"
    except (ValueError, TypeError):
        return "COP 0"
