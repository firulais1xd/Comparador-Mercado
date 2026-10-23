# Historial de cambios

La entrada más reciente va arriba. Cada entrada tiene:

- **Motivo:** por qué se hizo el cambio.
- **Cambios:** qué se modificó y en qué archivos.
- **Cómo verificar:** qué debería notarse.

Los commits automáticos "Precios del AAAA-MM-DD" solo actualizan `data/` y no se documentan aquí.

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
