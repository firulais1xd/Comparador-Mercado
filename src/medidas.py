"""Lectura de tamaños en los nombres de productos y filtros por palabras."""
import re
import unicodedata


def normalizar(texto: str) -> str:
    """Minúsculas y sin tildes: 'Café Molido 500 g' -> 'cafe molido 500 g'."""
    t = unicodedata.normalize("NFKD", texto.lower())
    return "".join(c for c in t if not unicodedata.combining(c))


def palabras(texto: str) -> list[str]:
    return re.findall(r"[a-z0-9]+", normalizar(texto))


def _coincide(palabra: str, clave: str) -> bool:
    if clave.endswith("*"):
        return palabra.startswith(clave[:-1])
    return palabra in (clave, clave + "s", clave + "es")


def cumple(nombre: str, requiere: list[str], excluye: list[str]) -> bool:
    """True si el nombre tiene todas las palabras requeridas y ninguna excluida.
    En `requiere`, "a|b" acepta cualquiera de las opciones."""
    ws = palabras(nombre)
    for req in requiere:
        opciones = [normalizar(o) for o in str(req).split("|")]
        if not any(_coincide(w, o) for w in ws for o in opciones):
            return False
    for exc in excluye:
        e = normalizar(str(exc))
        if any(_coincide(w, e) for w in ws):
            return False
    return True


# unidad escrita -> (unidad base, factor)
_UNIDADES = {
    "kg": ("kg", 1), "kgs": ("kg", 1), "kilo": ("kg", 1), "kilos": ("kg", 1), "kilogramo": ("kg", 1), "kilogramos": ("kg", 1),
    "g": ("kg", 0.001), "gr": ("kg", 0.001), "grs": ("kg", 0.001), "gramo": ("kg", 0.001), "gramos": ("kg", 0.001),
    "lb": ("kg", 0.5), "lbs": ("kg", 0.5), "libra": ("kg", 0.5), "libras": ("kg", 0.5),   # libra colombiana = 500 g
    "l": ("l", 1), "lt": ("l", 1), "lts": ("l", 1), "litro": ("l", 1), "litros": ("l", 1),
    "ml": ("l", 0.001), "cc": ("l", 0.001), "mililitros": ("l", 0.001),
    "und": ("und", 1), "un": ("und", 1), "u": ("und", 1), "unidad": ("und", 1), "unidades": ("und", 1), "unds": ("und", 1),
    "rollo": ("und", 1), "rollos": ("und", 1), "huevos": ("und", 1),
}
_RE_CANT = re.compile(
    r"(\d+(?:[.,]\d+)?)\s*("
    + "|".join(sorted(map(re.escape, _UNIDADES), key=len, reverse=True))
    + r")\b"
)
# "x 6", "x30", "pack 3", "paca 12" sin unidad después
_RE_PACK = re.compile(r"\b(?:x|pack|paca|por)\s*(\d+)\b(?!\s*(?:[.,]\d)|\s*(?:kg|kgs|g|gr|grs|gramos|ml|l|lt|lts|litro|litros|cc|lb|libras?)\b)")


def _numero(s: str) -> float:
    if re.fullmatch(r"\d{1,3}\.\d{3}", s):       # 1.000 = mil
        return float(s.replace(".", ""))
    return float(s.replace(",", "."))


def cantidad(texto: str, unidad: str) -> float | None:
    """Cantidad total del paquete en la unidad pedida (kg, l o und), o None si no se puede leer.
    Ej.: 'Leche entera x6 und 1100 ml' con unidad 'l' -> 6.6"""
    t = normalizar(texto)
    medidas = [(_numero(n), _UNIDADES[u]) for n, u in _RE_CANT.findall(t)]
    conteos = [n for n, (base, _) in medidas if base == "und"] + [float(p) for p in _RE_PACK.findall(t)]
    conteos = [c for c in conteos if 1 <= c <= 200]

    if unidad in ("kg", "l"):
        valores = [n * f for n, (base, f) in medidas if base == unidad]
        if not valores:
            return None
        q = valores[0]
        mult = max(conteos) if conteos and max(conteos) <= 48 else 1
        return round(q * mult, 4)

    # unidad == "und"
    return max(conteos) if conteos else None
