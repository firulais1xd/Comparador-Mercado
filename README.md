# 🛒 Comparador de Mercado — Barranquilla

Compara cada día los precios de una canasta de mercado en **Olímpica, Éxito, Carulla, Jumbo y Metro**. Te avisa por **Telegram** cuando algo baja de precio y publica una **página con gráficas** del historial.

Todo corre gratis en GitHub Actions. No necesitas computador ni servidor.

## Qué hace

- **Todos los días a las 6:37 a. m.** busca los productos de [`config/productos.yml`](config/productos.yml) en cada tienda.
- Compara por **precio por unidad** (por kg, por litro o por unidad). Así, un arroz de 5 kg y uno de 1 kg se comparan de forma justa.
- Guarda el historial en [`data/precios.csv`](data/precios.csv), que puedes abrir en Excel o Google Sheets.
- **Telegram:**
  - Alerta cuando un producto baja **10 % o más** frente a su precio habitual (mediana de los últimos 30 días).
  - Los **lunes** (o cuando lo ejecutas a mano) envía el resumen: qué tienda tiene la canasta más barata y dónde comprar cada producto.
- **Página web:** `https://firulais1xd.github.io/Comparador-Mercado/`

## Configuración (una sola vez, desde el teléfono)

1. **Secretos de Telegram:** en el repo, ve a *Settings › Secrets and variables › Actions › New repository secret*.
   - `TELEGRAM_TOKEN`: el token que te dio @BotFather.
   - `TELEGRAM_CHAT_ID`: opcional al principio. En la primera ejecución el bot te envía tu número de chat para que lo guardes aquí.
2. **Página web:** en *Settings › Pages › Build and deployment › Source*, elige **GitHub Actions**.
3. **Primera ejecución:** en *Actions › Precios diarios › Run workflow*.

## Personalizar

- **Agregar o quitar productos:** edita `config/productos.yml`. Cada producto explica sus campos.
- **Desactivar una tienda:** en `config/tiendas.yml`, pon `activa: false`.
- **Cambiar la hora:** edita `cron` en `.github/workflows/diario.yml` (la hora va en UTC, que son 5 horas más que en Colombia).

## Limitaciones

- Los precios son los de la **tienda en línea**. En el punto físico pueden variar un poco.
- Si una tienda cambia su página o bloquea las consultas, aparece como "⚠️ Sin datos" y las demás siguen funcionando.
- Algunos productos pueden emparejarse mal, por ejemplo una marca o variedad distinta a la que compras. Se corrige ajustando `requiere` y `excluye` en `productos.yml`.

## Estructura

```
config/productos.yml   Canasta y filtros de cada producto
config/tiendas.yml     Tiendas consultadas
src/tiendas.py         Lectura del catálogo VTEX de cada tienda
src/medidas.py         Lee el tamaño del paquete ("x6 und 1100 ml" → 6,6 L)
src/main.py            Recolecta, guarda, detecta bajas y avisa
src/sitio.py           Genera la página web
src/telegram.py        Envía los mensajes
data/precios.csv       Historial (se actualiza solo)
```

Historial de cambios: [CHANGELOG.md](CHANGELOG.md)
