"""
Mete las 3 tipografías dentro del PowerPoint para que se vean igual sin instalarlas.
Uso: python3 incrustar_fuentes.py Invitacion_sin_fuentes.pptx Invitacion_Karina.pptx
Usa las fuentes en formato EOT de fuentes/eot/ (convertidas desde los .ttf con:  npx ttf2eot Archivo.ttf > Archivo.eot)
"""
import sys, zipfile, shutil, re, os
src, dst = sys.argv[1], sys.argv[2]
E = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fuentes", "eot") + "/"
FONTS = [  # typeface, [(slot, file)]
    ("Pinyon Script", [("regular", "PinyonScript-Regular.eot")]),
    ("Cormorant Garamond", [("regular", "CormorantGaramond-Regular.eot"), ("bold", "CormorantGaramond-Bold.eot"),
                            ("italic", "CormorantGaramond-Italic.eot")]),
    ("Montserrat", [("regular", "Montserrat-Regular.eot"), ("bold", "Montserrat-Bold.eot")]),
]
zin = zipfile.ZipFile(src)
files = {n: zin.read(n) for n in zin.namelist() if not n.endswith("/")}
ct = files["[Content_Types].xml"].decode()
if 'Extension="fntdata"' not in ct:
    ct = ct.replace("<Default ", '<Default Extension="fntdata" ContentType="application/x-fontdata"/><Default ', 1)
files["[Content_Types].xml"] = ct.encode()
rels = files["ppt/_rels/presentation.xml.rels"].decode()
ids = [int(x) for x in re.findall(r'Id="rId(\d+)"', rels)]
nxt = max(ids) + 1
pres = files["ppt/presentation.xml"].decode()
lst = "<p:embeddedFontLst>"
n = 1
for face, styles in FONTS:
    lst += f'<p:embeddedFont><p:font typeface="{face}" charset="0"/>'
    for slot, fn in styles:
        rid = f"rId{nxt}"; nxt += 1
        files[f"ppt/fonts/font{n}.fntdata"] = open(E + fn, "rb").read()
        rels = rels.replace("</Relationships>",
            f'<Relationship Id="{rid}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/font" Target="fonts/font{n}.fntdata"/></Relationships>')
        lst += f'<p:{slot} r:id="{rid}"/>'
        n += 1
    lst += "</p:embeddedFont>"
lst += "</p:embeddedFontLst>"
assert "<p:notesSz" in pres
pres = re.sub(r"(<p:notesSz[^>]*/>)", r"\1" + lst, pres, count=1)
pres = pres.replace("<p:presentation ", "<p:presentation embedTrueTypeFonts=\"1\" ", 1).replace(" saveSubsetFonts=\"1\"", "")
if 'xmlns:r=' not in pres.split(">")[1] and 'xmlns:r=' not in pres[:600]:
    raise SystemExit("no r namespace")
files["ppt/presentation.xml"] = pres.encode()
files["ppt/_rels/presentation.xml.rels"] = rels.encode()
with zipfile.ZipFile(dst, "w", zipfile.ZIP_DEFLATED) as z:
    z.writestr("[Content_Types].xml", files.pop("[Content_Types].xml"))
    for k, v in files.items():
        z.writestr(k, v)
print("embedded", n - 1, "font files")
