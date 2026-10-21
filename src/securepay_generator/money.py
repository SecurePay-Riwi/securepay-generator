"""Montos y monedas: tasas de cambio y precisión de cada moneda."""

import json
from bisect import bisect_right
from decimal import ROUND_HALF_UP, Decimal

from securepay_generator.config import TASAS_FILE
from securepay_shared.config import MONEDA_DECIMALES


class Tasas:
    """Tasas de cambio por día: unidades de cada moneda por 1 USD.

    Si un día no tiene tasa (Frankfurter no la publicó o aún no llega),
    vale la última publicada antes, igual que hará el motor con la tabla
    de DynamoDB.
    """

    def __init__(self, por_fecha):
        if not por_fecha:
            raise ValueError("No hay tasas")
        self.por_fecha = por_fecha
        self.fechas = sorted(por_fecha)

    def del_dia(self, fecha):
        """Las tasas que valen en esa fecha (datetime o "AAAA-MM-DD")."""
        dia = fecha if isinstance(fecha, str) else fecha.date().isoformat()
        k = bisect_right(self.fechas, dia)
        if k == 0:
            raise ValueError(f"No hay tasas para {dia}: la primera es {self.fechas[0]}")
        return self.por_fecha[self.fechas[k - 1]]


def cargar_tasas(ruta=TASAS_FILE):
    """Lee las tasas guardadas, una entrada por día publicado."""
    # parse_float=Decimal lee 0.88286 como Decimal exacto, sin pasar por
    # float, que lo guardaría como 0.88285999999999997...
    datos = json.loads(ruta.read_text(encoding="utf-8"), parse_float=Decimal)
    return Tasas(
        {
            dia: {moneda: Decimal(tasa) for moneda, tasa in tasas.items()}
            for dia, tasas in datos["tasas"].items()
        }
    )


def paso(moneda):
    """La unidad más pequeña de la moneda: 0.01, o 1 para el yen."""
    return Decimal(1).scaleb(-MONEDA_DECIMALES[moneda])


def redondear(monto, moneda):
    """Deja el monto con los decimales que admite su moneda."""
    return Decimal(monto).quantize(paso(moneda), rounding=ROUND_HALF_UP)


def desde_usd(usd, moneda, tasas):
    """Convierte un monto en USD a la moneda de la cuenta.

    tasas son las de un día: Tasas.del_dia(fecha de la transacción).
    """
    return redondear(Decimal(str(usd)) * tasas[moneda], moneda)


def a_usd(monto, moneda, tasas):
    """Convierte un monto de su moneda a USD (sin redondear)."""
    return Decimal(monto) / tasas[moneda]
