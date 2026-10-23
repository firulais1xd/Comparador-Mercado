"""Búsqueda de productos en tiendas VTEX (Olímpica, Éxito, Carulla, Jumbo, Metro)."""
import time
from urllib.parse import quote

try:
    from curl_cffi import requests as http  # imita un navegador Chrome: algunas tiendas bloquean bots
    _KW = {"impersonate": "chrome"}
except ImportError:  # pragma: no cover
    import requests as http
    _KW = {"headers": {"User-Agent": "Mozilla/5.0 (Linux; Android 14) Chrome/130 Mobile"}}


def buscar(url_tienda: str, texto: str, cantidad: int = 40) -> list[dict]:
    """Devuelve los productos disponibles de la tienda para la búsqueda, en un formato simple."""
    url = (f"{url_tienda.rstrip('/')}/api/catalog_system/pub/products/search"
           f"?ft={quote(texto)}&_from=0&_to={cantidad - 1}")
    ultimo_error = None
    for intento in range(3):
        try:
            r = http.get(url, timeout=30, **_KW)
            if r.status_code in (200, 206):
                return list(_extraer(r.json(), url_tienda))
            ultimo_error = f"HTTP {r.status_code}"
        except Exception as e:  # red, JSON inválido, etc.
            ultimo_error = str(e)[:200]
        time.sleep(2 * (intento + 1))
    raise RuntimeError(ultimo_error)


def _extraer(datos, url_tienda: str):
    for p in datos or []:
        nombre = p.get("productName") or ""
        link = p.get("link") or ""
        if link.startswith("/"):
            link = url_tienda.rstrip("/") + link
        for item in p.get("items", []):
            oferta = _mejor_oferta(item)
            if not oferta:
                continue
            precio, lista = oferta
            yield {
                "nombre": item.get("nameComplete") or nombre,
                "marca": p.get("brand") or "",
                "precio": precio,
                "precio_lista": lista,
                "url": link,
            }


def _mejor_oferta(item):
    mejores = []
    for s in item.get("sellers", []):
        o = s.get("commertialOffer") or {}
        precio = o.get("Price") or 0
        disponible = o.get("AvailableQuantity", 0) > 0 or o.get("IsAvailable") is True
        if precio > 0 and disponible:
            mejores.append((float(precio), float(o.get("ListPrice") or precio)))
    return min(mejores) if mejores else None
