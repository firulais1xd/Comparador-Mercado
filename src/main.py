"""Recolecta los precios del día, guarda el historial, avisa por Telegram y genera la página.

Uso:  python -m src.main            (normal)
      RESUMEN=1 python -m src.main  (fuerza el resumen semanal)
"""
import csv
import json
import os
import statistics
import sys
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path

import yaml

from . import sitio, telegram, tiendas
from .medidas import cantidad, cumple

RAIZ = Path(__file__).resolve().parent.parent
CSV = RAIZ / "data" / "precios.csv"
ESTADO = RAIZ / "data" / "estado.json"
COLUMNAS = ["fecha", "producto", "tienda", "nombre", "marca", "precio", "precio_lista",
            "cantidad", "unidad", "precio_unidad", "precio_ref", "url"]
BOGOTA = timezone(timedelta(hours=-5))
UMBRAL_BAJA = 0.10          # avisar si baja 10 % o más frente a su precio habitual
DIAS_HABITUAL = 30
SIMBOLO = {"kg": "kg", "l": "L", "und": "und"}


def pesos(x: float) -> str:
    return "$" + f"{x:,.0f}".replace(",", ".")


def cargar_yaml(nombre):
    with open(RAIZ / "config" / nombre, encoding="utf-8") as f:
        return yaml.safe_load(f)


def recolectar(productos, lista_tiendas, hoy: str):
    filas, estado = [], {}
    for t in lista_tiendas:
        encontrados, errores, sin_match = 0, [], {}
        for p in productos:
            try:
                candidatos = tiendas.buscar(t["url"], p["buscar"], verificar_ssl=not t.get("ssl_incompleto"))
            except Exception as e:
                errores.append(f"{p['nombre']}: {e}")
                if len(errores) >= 3 and encontrados == 0:   # la tienda no responde: no insistir
                    errores.append("(se omiten los demás productos de esta tienda)")
                    break
                continue
            mejor = elegir(candidatos, p)
            if mejor:
                encontrados += 1
                filas.append({"fecha": hoy, "producto": p["nombre"], "tienda": t["nombre"], **mejor})
            else:   # diagnóstico: qué devolvió la tienda, para poder ajustar los filtros
                sin_match[p["nombre"]] = [c["nombre"] for c in candidatos[:6]]
        estado[t["nombre"]] = {"encontrados": encontrados, "total": len(productos), "errores": errores[:5],
                               "sin_coincidencia": sin_match}
        print(f"{t['nombre']}: {encontrados}/{len(productos)} productos" + (f" · {len(errores)} errores" if errores else ""))
        for e in errores[:3]:
            print("   ", e)
        for prod, nombres in sin_match.items():
            print(f"    sin coincidencia para {prod}. La tienda devolvió: {nombres}")
    return filas, estado


def elegir(candidatos, p):
    """El producto que cumple los filtros con menor precio por unidad."""
    lo, hi = p.get("rango", [0, float("inf")])
    mejor = None
    for c in candidatos:
        if not cumple(c["nombre"], p.get("requiere", []), p.get("excluye", [])):
            continue
        q = cantidad(c["nombre"], p["unidad"])
        if not q or not (lo <= q <= hi):
            continue
        pu = c["precio"] / q
        if mejor is None or pu < mejor["precio_unidad"]:
            mejor = {
                "nombre": c["nombre"], "marca": c["marca"], "precio": round(c["precio"]),
                "precio_lista": round(c["precio_lista"]), "cantidad": q, "unidad": p["unidad"],
                "precio_unidad": round(pu, 2), "precio_ref": round(pu * p["referencia"]), "url": c["url"],
            }
    return mejor


def leer_historial():
    if not CSV.exists():
        return []
    with open(CSV, encoding="utf-8", newline="") as f:
        filas = list(csv.DictReader(f))
    for r in filas:
        for k in ("precio", "precio_lista", "cantidad", "precio_unidad", "precio_ref"):
            r[k] = float(r[k])
    return filas


def guardar(historial, hoy):
    CSV.parent.mkdir(exist_ok=True)
    with open(CSV, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=COLUMNAS)
        w.writeheader()
        for r in sorted(historial, key=lambda r: (r["fecha"], r["producto"], r["tienda"])):
            w.writerow({k: r[k] for k in COLUMNAS})


def bajas_de_precio(historial, hoy_filas, hoy):
    """Productos que hoy están al menos UMBRAL_BAJA por debajo de su precio habitual (mediana de 30 días)."""
    desde = (datetime.fromisoformat(hoy) - timedelta(days=DIAS_HABITUAL)).date().isoformat()
    previos = defaultdict(list)
    for r in historial:
        if desde <= r["fecha"] < hoy:
            previos[(r["producto"], r["tienda"])].append(r["precio_unidad"])
    alertas = []
    for r in hoy_filas:
        antes = previos.get((r["producto"], r["tienda"]))
        if not antes or len(antes) < 2:
            continue
        habitual = statistics.median(antes)
        cambio = r["precio_unidad"] / habitual - 1
        if cambio <= -UMBRAL_BAJA:
            alertas.append((cambio, r, habitual))
    return sorted(alertas, key=lambda a: a[0])


def canasta(hoy_filas):
    """Valor de la canasta por tienda, solo con productos que tienen todas las tiendas con datos."""
    por_prod = defaultdict(dict)
    for r in hoy_filas:
        por_prod[r["producto"]][r["tienda"]] = r
    tiendas_hoy = sorted({r["tienda"] for r in hoy_filas})
    comunes = [p for p, d in por_prod.items() if len(d) == len(tiendas_hoy)]
    totales = {t: sum(por_prod[p][t]["precio_ref"] for p in comunes) for t in tiendas_hoy}
    return sorted(totales.items(), key=lambda x: x[1]), comunes, por_prod


def mensaje_alertas(alertas):
    lineas = ["🛒 <b>Bajaron de precio hoy</b>"]
    for cambio, r, habitual in alertas[:15]:
        u = SIMBOLO[r["unidad"]]
        lineas.append(
            f"• <b>{r['producto']}</b> en {r['tienda']}: {pesos(r['precio'])} "
            f"({pesos(r['precio_unidad'])}/{u}, <b>{cambio:+.0%}</b> vs. {pesos(habitual)}/{u}) "
            f"<a href=\"{r['url']}\">ver</a>"
        )
    return "\n".join(lineas)


def mensaje_resumen(hoy_filas, estado, url_pagina):
    totales, comunes, por_prod = canasta(hoy_filas)
    lineas = []
    if totales:
        lineas.append(f"🧺 <b>Canasta de mercado</b> ({len(comunes)} productos presentes en todas las tiendas)")
        base = totales[0][1]
        for i, (t, total) in enumerate(totales, 1):
            extra = "" if i == 1 else f"  (+{pesos(total - base)})"
            lineas.append(f"{i}. {t} — <b>{pesos(total)}</b>{extra}")
    lineas.append("\n🏷️ <b>Dónde está más barato cada producto</b>")
    for prod in sorted(por_prod):
        r = min(por_prod[prod].values(), key=lambda r: r["precio_unidad"])
        lineas.append(f"• {prod}: {r['tienda']} {pesos(r['precio'])} ({pesos(r['precio_unidad'])}/{SIMBOLO[r['unidad']]})")
    sin_datos = [t for t, e in estado.items() if e["encontrados"] == 0]
    if sin_datos:
        lineas.append(f"\n⚠️ Sin datos hoy de: {', '.join(sin_datos)}")
    if url_pagina:
        lineas.append(f"\n📊 <a href=\"{url_pagina}\">Ver gráficas e historial</a>")
    return "\n".join(lineas)


def url_pagina():
    repo = os.getenv("GITHUB_REPOSITORY", "")
    if "/" not in repo:
        return ""
    dueno, nombre = repo.split("/", 1)
    return f"https://{dueno.lower()}.github.io/{nombre}/"


def main():
    ahora = datetime.now(BOGOTA)
    hoy = ahora.date().isoformat()
    productos = cargar_yaml("productos.yml")
    lista_tiendas = [t for t in cargar_yaml("tiendas.yml") if t.get("activa", True)]

    hoy_filas, estado = recolectar(productos, lista_tiendas, hoy)
    historial = [r for r in leer_historial() if r["fecha"] != hoy]   # si se repite el día, se reemplaza
    alertas = bajas_de_precio(historial, hoy_filas, hoy)
    historial += hoy_filas
    guardar(historial, hoy)
    ESTADO.write_text(json.dumps({"actualizado": ahora.isoformat(timespec="minutes"), "tiendas": estado},
                                 ensure_ascii=False, indent=2), encoding="utf-8")

    sitio.generar(historial, hoy, estado, productos, RAIZ / "sitio")

    if not hoy_filas:
        telegram.enviar("⚠️ <b>Comparador de mercado</b>: hoy ninguna tienda respondió. Revisa el registro de GitHub Actions.")
        sys.exit(1)

    if alertas:
        telegram.enviar(mensaje_alertas(alertas))
    resumen = os.getenv("RESUMEN", "").lower() in ("1", "true", "si", "sí")
    if resumen or ahora.weekday() == 0:          # lunes, o ejecución manual
        telegram.enviar(mensaje_resumen(hoy_filas, estado, url_pagina()))
    print(f"Listo: {len(hoy_filas)} precios, {len(alertas)} alertas.")


if __name__ == "__main__":
    main()
