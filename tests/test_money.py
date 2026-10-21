from datetime import datetime, timezone
from decimal import Decimal

import pytest

from securepay_generator.money import Tasas, a_usd, desde_usd, redondear


def test_redondear_respeta_los_decimales_de_cada_moneda():
    assert redondear(Decimal("636114.00"), "JPY") == Decimal("636114")
    assert str(redondear(Decimal("636114.00"), "JPY")) == "636114"
    assert str(redondear(Decimal("10.005"), "USD")) == "10.01"


def test_desde_usd_y_a_usd_son_inversas(tasas):
    del_dia = tasas.del_dia("2026-10-01")
    cop = desde_usd(100, "COP", del_dia)
    assert cop == redondear(Decimal(100) * del_dia["COP"], "COP")
    assert abs(a_usd(cop, "COP", del_dia) - 100) < Decimal("0.01")


def test_tasas_guardadas_empiezan_en_la_fecha_de_referencia(tasas):
    assert tasas.fechas[0] == "2026-10-01"
    for dia in tasas.fechas:
        assert set(tasas.por_fecha[dia]) == {"USD", "COP", "EUR", "JPY"}
        assert tasas.por_fecha[dia]["USD"] == 1


# Jueves 1, viernes 2 y lunes 5 de octubre de 2026.
_TASAS = Tasas(
    {
        "2026-10-01": {"USD": Decimal(1), "COP": Decimal("3300")},
        "2026-10-02": {"USD": Decimal(1), "COP": Decimal("3310")},
        "2026-10-05": {"USD": Decimal(1), "COP": Decimal("3350")},
    }
)


def test_cada_dia_usa_su_propia_tasa():
    assert _TASAS.del_dia("2026-10-02")["COP"] == Decimal("3310")
    lunes = datetime(2026, 10, 5, 23, 59, tzinfo=timezone.utc)
    assert _TASAS.del_dia(lunes)["COP"] == Decimal("3350")


def test_fin_de_semana_usa_la_del_viernes():
    assert _TASAS.del_dia("2026-10-03")["COP"] == Decimal("3310")
    assert _TASAS.del_dia("2026-10-04")["COP"] == Decimal("3310")


def test_dia_aun_no_publicado_usa_la_ultima():
    assert _TASAS.del_dia("2026-10-25")["COP"] == Decimal("3350")


def test_antes_de_la_primera_tasa_falla():
    with pytest.raises(ValueError, match="No hay tasas"):
        _TASAS.del_dia("2026-09-30")
