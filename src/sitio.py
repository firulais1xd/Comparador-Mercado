"""Genera la página web estática (carpeta sitio/) que publica GitHub Pages."""
import json
from collections import defaultdict
from pathlib import Path

PLANTILLA = Path(__file__).with_name("plantilla.html")


def generar(historial, hoy, estado, productos, destino: Path):
    tiendas = sorted({r["tienda"] for r in historial})
    hoy_tabla = defaultdict(dict)
    historia = defaultdict(lambda: defaultdict(list))
    for r in sorted(historial, key=lambda r: r["fecha"]):
        historia[r["producto"]][r["tienda"]].append([r["fecha"], round(r["precio_ref"])])
        if r["fecha"] == hoy:
            hoy_tabla[r["producto"]][r["tienda"]] = {
                k: r[k] for k in ("nombre", "precio", "precio_unidad", "precio_ref", "cantidad", "unidad", "url")
            }

    tiendas_hoy = sorted({t for d in hoy_tabla.values() for t in d})
    comunes = [p for p, d in hoy_tabla.items() if len(d) == len(tiendas_hoy)]
    canasta = sorted(
        ([t, round(sum(hoy_tabla[p][t]["precio_ref"] for p in comunes))] for t in tiendas_hoy),
        key=lambda x: x[1],
    )
    datos = {
        "hoy": hoy,
        "tiendas": tiendas,
        "productos": [{"nombre": p["nombre"], "unidad": p["unidad"], "referencia": p["referencia"]} for p in productos],
        "tabla": hoy_tabla,
        "canasta": canasta,
        "comunes": len(comunes),
        "historia": historia,
        "estado": estado,
        "dias": len({r["fecha"] for r in historial}),
    }
    js = json.dumps(datos, ensure_ascii=False).replace("</", "<\\/")
    destino.mkdir(exist_ok=True)
    (destino / "index.html").write_text(PLANTILLA.read_text(encoding="utf-8").replace("__DATOS__", js), encoding="utf-8")
