# Invitación cumpleaños de Karina Llanos (versión verde y crema)

Código para reconstruir o modificar la invitación de 5 páginas verticales (formato historia, 9:16).

## Qué hay en la carpeta

| Archivo | Para qué sirve |
|---|---|
| `construir_invitacion.js` | Arma el PowerPoint: textos, posiciones, colores y tipografías de las 5 páginas |
| `incrustar_fuentes.py` | Mete las tipografías dentro del PowerPoint |
| `generar_imagenes.py` | Crea las imágenes realistas: sello de cera con la K y fondos de papel con relieve |
| `assets/` | Las imágenes ya generadas que usa la invitación (no hace falta volver a crearlas) |
| `fuentes/` | Pinyon Script, Cormorant Garamond y Montserrat (.ttf y .eot) con sus licencias OFL |

## Cómo se arma

```bash
npm install pptxgenjs
node construir_invitacion.js
python3 incrustar_fuentes.py Invitacion_sin_fuentes.pptx Invitacion_Karina.pptx
```

Solo si quieres volver a crear las imágenes (por ejemplo, otra letra en el sello):

```bash
pip install numpy scipy pillow
python3 generar_imagenes.py seal
python3 generar_imagenes.py emboss
```

## Diseño

- **Tamaño:** 5,625 × 10 pulgadas por página (1080 × 1920 px).
- **Colores:** vino `7A1626`, verde `6E7A48`, verde oscuro `4E5A32`, crema `F4ECDC`, texto `3E3A2C`.
- **Tipografías:** Pinyon Script para los títulos cursivos, Cormorant Garamond para el texto y Montserrat para las etiquetas en mayúscula con espaciado.
- **Páginas:**
  1. Portada: fondo crema con flores en relieve en dos esquinas, sello de cera vino con la K, "por el cumpleaños de Karina Llanos", jueves 3 de diciembre, "Abre la invitación".
  2. "¡Queridos compañeros!": crema liso, mensaje de la tradición y calendario de diciembre con el 3 marcado con un corazón vino.
  3. "Los detalles": fondo verde con marco en relieve. Fecha, hora (1:00 p. m.), plan (almuerzo de cumpleaños) y lugar (pendiente por definir).
  4. "Tu aporte": crema con flores en relieve. $250.000 por persona, plazo hasta el 30 de noviembre, el dinero lo recibe Cecilia, "¿Contamos contigo?" y botón de confirmar asistencia.
  5. Cierre: fondo verde con flores en relieve en las 4 esquinas, mensaje final, "Con cariño, tu equipo", "¡Un abrazo para todos!" y el sello.

## Mensaje para pegar en el otro chat de Claude

> Te adjunto el código de una invitación de cumpleaños (lee LEEME.md). Es un PowerPoint vertical de 5 páginas generado con pptxgenjs (`construir_invitacion.js`), con las tipografías incrustadas con `incrustar_fuentes.py`. Las imágenes ya están en `assets/`. Quiero que [escribe aquí el cambio que necesitas]. Al terminar, vuelve a correr los dos pasos y entrégame el .pptx y un PDF.
