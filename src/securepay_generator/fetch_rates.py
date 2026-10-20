"""Descarga de Frankfurter las tasas de cada día desde la fecha de referencia.

    uv run python -m securepay_generator.fetch_rates

El archivo resultante se sube al repo: así el generador no depende de
internet en cada corrida y todas las corridas usan exactamente las mismas
tasas. Trae del 1 de octubre hasta el último día publicado; cuando haya
días nuevos, se vuelve a correr y se sube el archivo actualizado.
Frankfurter mezcla varios proveedores y suele traer todos los días,
incluso fines de semana; un día sin tasa (o que aún no llega) usa la
última anterior (money.Tasas).
"""

import json
import urllib.request

from securepay_generator.config import FECHA_REFERENCIA, TASAS_FILE

# La versión 2 trae COP; la versión 1 no.
URL = "https://api.frankfurter.dev/v2/rates"

BASE = "USD"
MONEDAS = ("COP", "EUR", "JPY")


def descargar():
    desde = FECHA_REFERENCIA.date().isoformat()
    # Sin "to", Frankfurter trae hasta hoy.
    url = f"{URL}?from={desde}&base={BASE}&quotes={','.join(MONEDAS)}"

    # Sin un User-Agent propio, Frankfurter rechaza la petición (403):
    # bloquea el que urllib manda por defecto ("Python-urllib/3.12").
    peticion = urllib.request.Request(
        url,
        headers={"User-Agent": "securepay-generator", "Accept": "application/json"},
    )

    with urllib.request.urlopen(peticion, timeout=30) as respuesta:
        registros = json.load(respuesta)

    # Cada registro llega como {"date", "base", "quote", "rate"}, uno por
    # moneda y por día.
    por_dia = {}
    for r in registros:
        por_dia.setdefault(r["date"], {})[r["quote"]] = r["rate"]

    tasas = {}
    for fecha in sorted(por_dia):
        faltantes = set(MONEDAS) - set(por_dia[fecha])
        if faltantes:
            # COP lo publica el Banco de la República y EUR y JPY el BCE,
            # con festivos distintos: ese día se usa la tasa anterior.
            print(f"  {fecha}: sin {sorted(faltantes)}, se omite")
            continue
        if any(t <= 0 for t in por_dia[fecha].values()):
            raise ValueError(f"Tasa inválida el {fecha}: {por_dia[fecha]}")
        tasas[fecha] = {BASE: 1, **{m: por_dia[fecha][m] for m in MONEDAS}}

    if desde not in tasas:
        raise ValueError(f"Frankfurter no trajo tasas completas del {desde}")

    contenido = {
        "fuente": url,
        "base": BASE,
        "desde": desde,
        "hasta": max(tasas),
        # Por día publicado: unidades de cada moneda por 1 USD.
        "tasas": tasas,
    }

    TASAS_FILE.parent.mkdir(parents=True, exist_ok=True)
    TASAS_FILE.write_text(
        json.dumps(contenido, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    print(f"Tasas del {desde} al {contenido['hasta']} ({len(tasas)} días) guardadas en {TASAS_FILE}")


if __name__ == "__main__":
    descargar()
