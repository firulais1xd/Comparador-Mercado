import pytest

from src.medidas import cantidad, cumple


@pytest.mark.parametrize("texto,unidad,esperado", [
    ("Arroz Diana 1000 g", "kg", 1.0),
    ("Arroz Roa x 5 kg", "kg", 5.0),
    ("Arroz Diana 1.000 g", "kg", 1.0),
    ("Aceite Premier 3000 ml", "l", 3.0),
    ("Leche entera Alquería x6 und 1100 ml", "l", 6.6),
    ("Leche Entera Colanta Bolsa 1100ml", "l", 1.1),
    ("Café Sello Rojo Molido 500 g", "kg", 0.5),
    ("Huevos rojos AA x30", "und", 30),
    ("Huevo Kikes rojo tipo A 30 unidades", "und", 30),
    ("Papel higiénico Familia x 12 rollos", "und", 12),
    ("Panela 2 libras", "kg", 1.0),
    ("Atún Van Camps en agua 160 g pack x3", "kg", 0.48),
    ("Crema dental Colgate 75 ml", "l", 0.075),
    ("Mantequilla Alpina 2,5 kg", "kg", 2.5),
    ("Producto sin tamaño", "kg", None),
])
def test_cantidad(texto, unidad, esperado):
    assert cantidad(texto, unidad) == (pytest.approx(esperado) if esperado else None)


def test_cumple_palabra_completa():
    assert cumple("Sal Refisal 1 kg", ["sal"], ["salsa"])
    assert not cumple("Salsa de tomate", ["sal"], [])          # 'sal' no es 'salsa'
    assert cumple("Huevos rojos x30", ["huev*"], [])
    assert not cumple("Huevo de chocolate", ["huev*"], ["chocolate"])
    assert cumple("Pasta Doria Espagueti 500 g", ["spaghetti|espagueti"], [])
    assert cumple("Queso Costeño 500 g", ["queso", "costeno"], [])
    assert not cumple("Leche Deslactosada Entera", ["leche", "entera"], ["deslactosada"])
