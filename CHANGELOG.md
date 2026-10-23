# Historial de cambios

La entrada más reciente va arriba. Cada entrada tiene:

- **Motivo:** por qué se hizo el cambio.
- **Cambios:** qué se modificó y en qué archivos.
- **Cómo verificar:** qué debería notarse.

Los commits automáticos "Precios del AAAA-MM-DD" solo actualizan `data/` y no se documentan aquí.

---

## v0.1.4 — 2026-10-23

**Motivo:** el bot de Telegram no enviaba mensajes, y desde fuera no se podía saber por qué (los registros de Actions no estaban accesibles).

**Cambios:**
- `src/telegram.py`: registra el resultado de cada envío: si hay token, si se detectó el chat, cuántos mensajes tenía el bot en su bandeja, cuántos se enviaron y los errores que devolvió Telegram. No guarda el token ni el número de chat.
- `src/main.py`: ese registro queda en la sección `"telegram"` de `data/estado.json`.

**Cómo verificar:** después de una ejecución, `data/estado.json` muestra el estado de Telegram.

---

## v0.1.3 — 2026-10-23

**Motivo:** en la tercera ejecución, Olímpica, Jumbo y Metro tuvieron 20/20 productos y Éxito y Carulla 19/20. Les faltaban las lentejas, porque su buscador solo devolvía lentejas preparadas o en snack.

**Cambios:**
- `config/productos.yml`: Lentejas usa tres búsquedas ("lentejas", "lenteja", "lentejas 500 g") y excluye las tostadas u horneadas.

**Cómo verificar:** en la siguiente ejecución diaria, Lentejas no debería aparecer en "sin_coincidencia" de Éxito ni de Carulla en `data/estado.json`.

---

## v0.1.2 — 2026-10-23

**Motivo:** la segunda ejecución confirmó que Jumbo y Metro ya funcionan (19/20 productos), pero aún se colaban productos que solo mencionan el ingrediente ("Caladitos de mantequilla", "Cazuela de lentejas"), y las búsquedas de huevos y sal no devolvían nada en algunas tiendas.

**Cambios:**
- `src/medidas.py`: nueva opción `empieza`, para exigir que el nombre comience por cierta palabra.
- `src/main.py`: `buscar` puede ser una lista de búsquedas; los resultados se combinan.
- `config/productos.yml`:
  - `empieza` en Huevos, Lentejas, Mantequilla, Sal y Café.
  - Búsquedas más generales para Huevos ("huevos") y Sal ("sal", "sal refisal").
  - Café: se excluyen los sobres individuales (Kolado), que confundían el cálculo por kilo.
- `tests/test_medidas.py`: prueba de `empieza`.

**Cómo verificar:** en `data/estado.json` no debería aparecer Huevos ni Sal en "sin_coincidencia", y Mantequilla y Lentejas deberían ser los productos básicos en todas las tiendas.

---

## v0.1.1 — 2026-10-23

**Motivo:** en la primera ejecución real, Olímpica, Éxito y Carulla respondieron (19/20 productos cada una), pero Jumbo y Metro fallaron por un error de certificado SSL, y algunos productos se emparejaron mal.

**Cambios:**
- `src/tiendas.py`: opción para aceptar sitios que envían el certificado SSL incompleto. Se pidieron 50 resultados por búsqueda en vez de 40.
- `config/tiendas.yml`: `ssl_incompleto: true` en Jumbo y Metro. Solo se leen precios públicos; no se envían datos.
- `config/productos.yml`:
  - Mantequilla: se excluyen productos que solo "saben a" mantequilla (tostadas, arepas, pancitos, ponqués, etc.).
  - Lentejas: se excluyen las preparadas ("con zanahoria y papa").
  - Atún: se excluyen las mezclas con maíz o verduras.
- `src/main.py`: cuando una tienda no tiene coincidencia para un producto, el registro y `data/estado.json` muestran qué devolvió la tienda, para poder ajustar los filtros.

**Cómo verificar:** en la siguiente ejecución, Jumbo y Metro deberían mostrar productos, y Mantequilla y Lentejas deberían ser los productos básicos.

---

## v0.1.0 — 2026-10-23

**Motivo:** primera versión. Comparar precios de mercado en Barranquilla, recibir alertas por Telegram y ver gráficas en una página web.

**Cambios:**
- `src/tiendas.py`: lectura del catálogo público VTEX de Olímpica, Éxito, Carulla, Jumbo y Metro. Imita un navegador (curl_cffi) y reintenta 3 veces.
- `src/medidas.py`: lee el tamaño de cada paquete (g, kg, libras, ml, L, unidades, packs "x6") para comparar por precio unitario. Los filtros por palabra completa evitan confundir "sal" con "salsa".
- `config/productos.yml`: canasta inicial de 20 productos básicos (arroz, aceite, azúcar, leche, huevos, café, queso costeño, etc.).
- `src/main.py`: elige la presentación más económica por tienda, guarda `data/precios.csv` y avisa de bajas de 10 % o más frente a la mediana de 30 días. Los lunes envía el resumen de la canasta. Si una tienda falla 3 veces seguidas, se omite ese día.
- `src/sitio.py` y `src/plantilla.html`: página con el ranking de la canasta, una tabla de precios con la tienda más barata resaltada, historial por producto y estado de las tiendas. Funciona en celular y en modo oscuro.
- `src/telegram.py`: envío de mensajes, con detección automática del chat ID.
- `.github/workflows/diario.yml`: se ejecuta todos los días a las 6:37 a. m. (hora de Colombia), guarda el historial y publica en GitHub Pages.
- `tests/test_medidas.py`: 16 pruebas de lectura de tamaños y filtros.

**Cómo verificar:** ejecuta *Actions › Precios diarios › Run workflow*. El registro muestra cuántos productos encontró cada tienda, Telegram recibe el resumen y la página muestra la tabla.
