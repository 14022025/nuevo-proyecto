// Construye la invitación (versión verde y crema, 5 páginas verticales 9:16) como PowerPoint.
// Uso:  npm install pptxgenjs   y luego   node construir_invitacion.js
// Resultado: Invitacion_sin_fuentes.pptx  -> después correr incrustar_fuentes.py
// Tipografías: Pinyon Script (títulos cursivos), Cormorant Garamond (texto), Montserrat (etiquetas en mayúscula).
const pptxgen = require("pptxgenjs");
const pres = new pptxgen();
pres.defineLayout({ name: "STORY", width: 5.625, height: 10 });
pres.layout = "STORY";
pres.title = "Cumpleaños Karina Llanos";

const path = require("path");
const A = path.join(__dirname, "assets") + "/";
const SCRIPT = "Pinyon Script", SERIF = "Cormorant Garamond", SANS = "Montserrat";
const WINE = "7A1626", GREEN = "6E7A48", GREEN_D = "4E5A32", CREAM = "F4ECDC", INK = "3E3A2C";
const W = 5.625;
const center = (w) => (W - w) / 2;

function t(s, text, o) {
  s.addText(text, Object.assign({ isTextBox: true, margin: 0, align: "center", valign: "middle", x: 0.45, w: W - 0.9 }, o));
}
function img(s, name, x, y, w, h, objectName) { s.addImage({ path: A + name, x, y, w, h, objectName, altText: objectName }); }
const bg = (s, n) => img(s, n, 0, 0, W, 10, "Fondo");

// 1 ─ Sobre / carta
{
  const s = pres.addSlide(); bg(s, "emboss_corners_cream.jpg");
  t(s, "UNA CARTA ESPECIAL PARA TI", { y: 1.3, h: 0.3, fontFace: SANS, fontSize: 9.5, color: GREEN_D, charSpacing: 4 });
  const sw = 2.15, sh = sw * 655 / 538;
  img(s, "seal_real_wine.png", center(sw), 4.2 - sh / 2, sw, sh, "Sello de cera");
  t(s, "por el cumpleaños de", { y: 5.85, h: 0.4, fontFace: SERIF, italic: true, fontSize: 17, color: INK });
  t(s, "Karina Llanos", { y: 6.25, h: 1.0, fontFace: SCRIPT, fontSize: 48, color: WINE });
  t(s, "JUEVES  ·  3 DE DICIEMBRE", { y: 7.45, h: 0.3, fontFace: SANS, fontSize: 9.5, color: GREEN_D, charSpacing: 3 });
  img(s, "flourish_burg.png", center(2.6), 8.2, 2.6, 0.26, "Adorno");
  t(s, "ABRE LA INVITACIÓN", { y: 8.55, h: 0.3, fontFace: SANS, fontSize: 9, color: GREEN_D, charSpacing: 4 });
}

// 2 ─ Saludo + calendario
{
  const s = pres.addSlide(); bg(s, "cream_plain.jpg");
  t(s, "¡Queridos compañeros!", { y: 1.45, h: 0.85, fontFace: SCRIPT, fontSize: 36, color: WINE });
  t(s, [
    { text: "Se acerca una fecha muy especial e importante para todos nosotros: ", options: {} },
    { text: "¡el cumpleaños de nuestra querida jefa Karina!", options: { italic: true, color: WINE } },
  ], { y: 2.35, h: 1.0, x: 0.6, w: W - 1.2, fontFace: SERIF, fontSize: 16, color: INK, lineSpacingMultiple: 1.1 });
  t(s, "Como ya es tradición, cada año organizamos un compartir para celebrar esta ocasión tan bonita, y este año no será la excepción.", {
    y: 3.45, h: 1.0, x: 0.6, w: W - 1.2, fontFace: SERIF, fontSize: 16, color: INK, lineSpacingMultiple: 1.1 });

  // calendario diciembre 2026 (empieza martes)
  t(s, "Diciembre", { y: 4.75, h: 0.7, fontFace: SCRIPT, fontSize: 32, color: GREEN_D });
  const days = ["Lu", "Ma", "Mi", "Ju", "Vi", "Sá", "Do"];
  const cw = 0.62, x0 = center(cw * 7), y0 = 5.55, rh = 0.48;
  days.forEach((d, i) => t(s, d.toUpperCase(), { x: x0 + i * cw, w: cw, y: y0, h: 0.3, fontFace: SANS, fontSize: 8, color: GREEN_D, charSpacing: 1 }));
  for (let day = 1; day <= 31; day++) {
    const idx = day + 0; // Tuesday offset 1
    const col = idx % 7, row = Math.floor(idx / 7);
    const x = x0 + col * cw, y = y0 + 0.4 + row * rh;
    if (day === 3) {
      s.addShape(pres.shapes.HEART, { x: x + cw / 2 - 0.25, y: y - 0.04, w: 0.5, h: 0.46, fill: { color: WINE }, line: { color: WINE, width: 0 }, objectName: "Corazón día 3" });
      t(s, "3", { x, w: cw, y, h: 0.36, fontFace: SERIF, bold: true, fontSize: 15, color: CREAM });
    } else {
      t(s, String(day), { x, w: cw, y, h: 0.36, fontFace: SERIF, fontSize: 15, color: INK });
    }
  }
}

// 3 ─ Detalles (verde)
{
  const s = pres.addSlide(); bg(s, "emboss_frame_green.jpg");
  t(s, "Los detalles", { y: 1.0, h: 0.9, fontFace: SCRIPT, fontSize: 44, color: CREAM });
  img(s, "flourish_cream.png", center(2.4), 1.95, 2.4, 0.24, "Adorno");
  const rows = [
    ["ic_cal_cream.png", "FECHA", "Jueves 3 de diciembre"],
    ["ic_clock_cream.png", "HORA", "1:00 p. m."],
    ["ic_lunch_cream.png", "PLAN", "Almuerzo de cumpleaños"],
    ["ic_pin_cream.png", "LUGAR", "Pendiente por definir"],
  ];
  rows.forEach(([ic, lab, val], i) => {
    const y = 2.5 + i * 1.3;
    img(s, ic, center(0.5), y, 0.5, 0.5, "Icono " + lab);
    t(s, lab, { y: y + 0.55, h: 0.28, fontFace: SANS, fontSize: 8.5, color: CREAM, charSpacing: 4 });
    t(s, val, { y: y + 0.82, h: 0.4, fontFace: SERIF, bold: true, fontSize: 19, color: CREAM });
  });
  t(s, "Te avisaremos el lugar muy pronto", { y: 7.75, h: 0.35, fontFace: SERIF, italic: true, fontSize: 14, color: CREAM });
}

// 4 ─ Aporte + confirmación
{
  const s = pres.addSlide(); bg(s, "emboss_corners_cream_b.jpg");
  img(s, "ic_gift_wine.png", center(0.55), 0.6, 0.55, 0.55, "Icono regalo");
  t(s, "Tu aporte", { y: 1.15, h: 0.85, fontFace: SCRIPT, fontSize: 42, color: WINE });
  t(s, "$250.000", { y: 2.05, h: 0.8, fontFace: SERIF, bold: true, fontSize: 48, color: GREEN_D });
  t(s, "CUOTA POR PERSONA", { y: 2.85, h: 0.28, fontFace: SANS, fontSize: 8.5, color: INK, charSpacing: 4 });
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 0.65, y: 3.4, w: W - 1.3, h: 1.25, rectRadius: 0.12, fill: { color: "E8E1CC" }, line: { color: GREEN, width: 0.75 }, objectName: "Tarjeta aporte" });
  t(s, [
    { text: "Plazo máximo: ", options: {} }, { text: "30 de noviembre", options: { bold: true, color: WINE, breakLine: true } },
    { text: "El dinero lo recibe ", options: {} }, { text: "Cecilia", options: { bold: true, color: WINE } },
  ], { x: 0.75, w: W - 1.5, y: 3.5, h: 1.05, fontFace: SERIF, fontSize: 17, color: INK, lineSpacingMultiple: 1.3 });

  img(s, "flourish_burg.png", center(2.4), 5.0, 2.4, 0.24, "Adorno");
  t(s, "¿Contamos contigo?", { y: 5.45, h: 0.85, fontFace: SCRIPT, fontSize: 38, color: WINE });
  t(s, "Confírmanos tu asistencia lo más pronto posible, ya que necesitamos definir un lugar donde podamos estar cómodamente todos.", {
    y: 6.35, h: 1.2, x: 0.6, w: W - 1.2, fontFace: SERIF, fontSize: 16, color: INK, lineSpacingMultiple: 1.1 });
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: center(3.2), y: 7.8, w: 3.2, h: 0.5, rectRadius: 0.25, fill: { color: WINE }, line: { color: WINE, width: 0 }, objectName: "Botón" });
  t(s, "CONFIRMAR ASISTENCIA", { x: center(3.2), w: 3.2, y: 7.8, h: 0.5, fontFace: SANS, fontSize: 9, bold: true, color: CREAM, charSpacing: 3 });
}

// 5 ─ Cierre (verde)
{
  const s = pres.addSlide(); bg(s, "emboss_corners_green.jpg");
  t(s, "¡Esperamos contar con tu compañía para compartir un momento lleno de alegría, cariño y buenos deseos para nuestra querida Karina!", {
    y: 2.2, h: 1.9, x: 0.6, w: W - 1.2, fontFace: SERIF, italic: true, fontSize: 19, color: CREAM, lineSpacingMultiple: 1.15 });
  img(s, "flourish_cream.png", center(2.4), 4.35, 2.4, 0.24, "Adorno");
  t(s, "Con cariño,", { y: 4.85, h: 0.7, fontFace: SCRIPT, fontSize: 32, color: CREAM });
  t(s, "tu equipo", { y: 5.45, h: 0.8, fontFace: SCRIPT, fontSize: 40, color: CREAM });
  const sw = 1.6, sh = sw * 655 / 538;
  img(s, "seal_real_wine.png", center(sw), 6.45, sw, sh, "Sello de cera");
  t(s, "¡UN ABRAZO PARA TODOS!", { y: 8.65, h: 0.3, fontFace: SANS, fontSize: 9, color: CREAM, charSpacing: 4 });
}

pres.writeFile({ fileName: path.join(__dirname, "Invitacion_sin_fuentes.pptx") }).then(() => console.log("ok"));
