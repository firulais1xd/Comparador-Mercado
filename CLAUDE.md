# Reglas del repositorio

- **Cada cambio que se suba a GitHub debe documentarse en `CHANGELOG.md`**, en una entrada nueva arriba del todo con el formato `## vX.Y.Z — AAAA-MM-DD` y las secciones Motivo, Cambios (indicando los archivos) y Cómo verificar. La documentación va **en el mismo commit** que el cambio.
  - Versión: Z para correcciones, Y para funciones nuevas o cambios en la canasta, X para cambios grandes.
  - Los commits automáticos "Precios del …" (solo `data/`) no se documentan.
- Antes de subir: `python -m pytest -q tests` debe pasar.
- Los mensajes de commit van en español y describen el cambio.
- Idioma del código, la página y la documentación: español.
- Ciudad: Barranquilla. Las tiendas se configuran en `config/tiendas.yml` y los productos en `config/productos.yml`.
