"""Láminas de la tercera vuelta: original | A color | Mantener | (B/N de la segunda vuelta) y cambios antes/después."""
import json
import pathlib
import sys

from PIL import Image, ImageDraw, ImageFont

M = pathlib.Path(sys.argv[1])          # carpeta de la tercera vuelta
A = pathlib.Path(sys.argv[2])          # carpeta de la segunda vuelta (B/N corregido)
P = pathlib.Path(sys.argv[3])          # carpeta de la primera vuelta (B/N de la pareja y el grupo)
FUENTE = ImageFont.truetype("arialbd.ttf", 24)
ORIG = {"cumple": pathlib.Path(r"C:\Users\Nicolás\Desktop\Proyectos\RegalosIA\web\restauraciondefotos\img\muestra-antes.jpg"),
        "grupo-guitarra": pathlib.Path(r"C:\Pedidos\Listos\RF-0005\1-original\foto-01.jpg"),
        "pareja-estudio": pathlib.Path(r"C:\Pedidos\Listos\RF-0008\1-original\foto-01.jpg")}


def lamina(celdas, salida, alto=430):
    ims = [(t, Image.open(r).convert("RGB")) for t, r in celdas if r.exists()]
    ims = [(t, i.resize((round(i.width * alto / i.height), alto), Image.LANCZOS)) for t, i in ims]
    hoja = Image.new("RGB", (sum(i.width for _, i in ims) + 12 * (len(ims) + 1), alto + 60), (255, 250, 235))
    d, x = ImageDraw.Draw(hoja), 12
    for t, i in ims:
        d.text((x, 16), t, fill=(26, 23, 18), font=FUENTE)
        hoja.paste(i, (x, 50))
        x += i.width + 12
    hoja.save(M / salida, quality=85)


byn = {"cumple": A / "cumple-byn.png", "grupo-guitarra": P / "grupo-guitarra-byn.png", "pareja-estudio": P / "pareja-estudio-byn.png"}
for foto, orig in ORIG.items():
    lamina([("Original", orig), ("A color", M / f"{foto}-color.png"),
            ("Mantener colores de época", M / f"{foto}-mantener.png"), ("En blanco y negro", byn[foto])],
           f"lamina-modos-{foto}.jpg")
for c in json.loads((M / "resultados.json").read_text(encoding="utf-8"))["cambios"]:
    lamina([("Original", ORIG[c["foto"]]), ("Lo que vio el cliente", M / c["antes"]), ("Después del cambio", M / c["archivo"])],
           f"lamina-cambio-{c['foto']}.jpg")
print("ok")
