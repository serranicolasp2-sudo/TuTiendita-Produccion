"""Arma el informe de las pruebas de restauración (HTML local + láminas JPG) a partir de resultados.json.

  python informe.py <carpeta-de-la-prueba>
"""
import html
import json
import pathlib
import sys

from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from probar_restauracion import FOTOS, MODOS  # noqa: E402

C = pathlib.Path(sys.argv[1])
R = json.loads((C / "resultados.json").read_text(encoding="utf-8"))
VER = C / "ver"
VER.mkdir(exist_ok=True)
NOMBRES = {"cumple": "Cumpleaños infantil (sepia, con carteles)", "grupo-guitarra": "Grupo con guitarra (color desteñido)",
           "pareja-estudio": "Pareja de estudio (sepia, años 40)", "retrato-gorro": "Retrato con gorro (blanco y negro)",
           "abuelo-nene": "Abuelo y nene (color desteñido)"}
TITULO_MODO = {"Color": "A color", "Mantener colores de época": "Mantener colores de época", "Blanco y negro": "En blanco y negro"}
FUENTE = ImageFont.truetype("arialbd.ttf", 26)


def chica(origen: pathlib.Path, nombre: str, lado=1400) -> str:
    destino = VER / f"{nombre}.jpg"
    if not destino.exists():
        im = Image.open(origen).convert("RGB")
        im.thumbnail((lado, lado), Image.LANCZOS)
        im.save(destino, quality=86)
    return f"ver/{destino.name}"


def lamina(nombre: str, celdas: list, archivo: str):
    """Fila de imágenes del mismo alto con su título arriba."""
    alto = 520
    ims = []
    for titulo, ruta in celdas:
        im = Image.open(C / ruta).convert("RGB")
        ims.append((titulo, im.resize((round(im.width * alto / im.height), alto), Image.LANCZOS)))
    ancho = sum(i.width for _, i in ims) + 12 * (len(ims) + 1)
    hoja = Image.new("RGB", (ancho, alto + 70), (255, 250, 235))
    d = ImageDraw.Draw(hoja)
    x = 12
    for titulo, im in ims:
        d.text((x, 18), titulo, fill=(26, 23, 18), font=FUENTE)
        hoja.paste(im, (x, 58))
        x += im.width + 12
    hoja.save(C / archivo, quality=85)


filas = []
restauradas = {(r["foto"], r["modo"]): r for r in R["restauraciones"] if r.get("archivo")}
fallas = [r for r in R["restauraciones"] if r.get("error")] + [c for c in R["cambios"] if c.get("error")]
for foto in FOTOS:
    modos = [m for m in MODOS if (foto, m) in restauradas]
    if not modos:
        continue
    orig = chica(FOTOS[foto], f"{foto}-original")
    celdas = [("Original", orig)] + [(TITULO_MODO[m], chica(C / restauradas[(foto, m)]["archivo"], f"{foto}-{MODOS[m]}"))
                                     for m in modos]
    lamina(foto, celdas, f"lamina-{foto}.jpg")
    ficha = json.loads((C / f"{foto}-ficha.json").read_text(encoding="utf-8"))
    objetos = "".join(f"<li><b>{html.escape(e['objeto'])}</b>: {html.escape(e['colores'])} "
                      f"<small>({e['confianza']})</small></li>" for e in ficha["elementos"])
    figuras = "".join(f'<figure><a href="{src}"><img src="{src}" loading="lazy"></a><figcaption>{t}'
                      + (f" · {restauradas[(foto, m)]['segundos']} s" if m else "") + "</figcaption></figure>"
                      for (t, src), m in zip(celdas, [None] + modos))
    filas.append(f"""<section><h2>{NOMBRES.get(foto, foto)}</h2>
<p class="meta">{html.escape(ficha['estado_color'])} · {html.escape(ficha['plano'])} · época: {html.escape(ficha['epoca'])}</p>
<div class="fila">{figuras}</div>
<details><summary>Lo que encontró el análisis ({len(ficha['elementos'])} objetos)</summary><ul>{objetos}</ul></details></section>""")

cambios = []
for c in sorted(R["cambios"], key=lambda x: x["n"]):
    v = c.get("validacion") or {}
    estado = ("rehecha" if c.get("archivo") else "no se rehízo") if not c.get("error") else "error"
    celdas = [("Original", chica(FOTOS[c["foto"]], f"{c['foto']}-original"))]
    antes = restauradas.get((c["foto"], c["modo"]))
    if antes:
        celdas.append((f"Antes ({TITULO_MODO[c['modo']]})", chica(C / antes["archivo"], f"{c['foto']}-{MODOS[c['modo']]}")))
    if c.get("archivo"):
        celdas.append(("Después del cambio", chica(C / c["archivo"], pathlib.Path(c["archivo"]).stem)))
        lamina(c["foto"], celdas, f"lamina-cambio{c['n']}.jpg")
    figuras = "".join(f'<figure><a href="{s}"><img src="{s}" loading="lazy"></a><figcaption>{t}</figcaption></figure>' for t, s in celdas)
    cambios.append(f"""<section><h3>Cambio {c['n']}: <q>{html.escape(c['nota'])}</q></h3>
<p class="meta">Validación: <b>{'válido' if v.get('valida') else 'NO válido'}</b> ({html.escape(v.get('categoria', ''))})
{' · modo nuevo: ' + html.escape(v['modo_color']) if v.get('modo_color') else ''} · {estado}</p>
<p>Instrucción para Codex: {html.escape(v.get('instruccion') or '—')}</p>
{f"<p>No se hace: {html.escape(v['rechazado'])}</p>" if v.get('rechazado') else ''}
{f"<p>Mensaje para el cliente: <i>{html.escape(v['mensaje_cliente'])}</i></p>" if v.get('mensaje_cliente') else ''}
{f"<p class='error'>{html.escape(c['error'])}</p>" if c.get('error') else ''}
<div class="fila">{figuras}</div></section>""")

ajustes = []
if len(sys.argv) > 2:      # segunda vuelta con los prompts corregidos: original | primera vuelta | con ajustes
    A = pathlib.Path(sys.argv[2])
    RA = json.loads((A / "resultados.json").read_text(encoding="utf-8"))
    casos = [(r["foto"], r["modo"], r["archivo"], restauradas.get((r["foto"], r["modo"])), "")
             for r in RA["restauraciones"] if r.get("archivo")]
    casos += [(c["foto"], c.get("modo_final", c["modo"]), c["archivo"],
               next((x for x in R["cambios"] if x["n"] == c["n"] and x.get("archivo")), None),
               f"cambio {c['n']}: «{c['nota']}»") for c in RA["cambios"] if c.get("archivo")]
    for foto, modo, archivo, antes, extra in casos:
        celdas = [("Original", chica(FOTOS[foto], f"{foto}-original"))]
        if antes:
            celdas.append(("Primera vuelta", chica(C / antes["archivo"], "v1-" + pathlib.Path(antes["archivo"]).stem)))
        celdas.append(("Con los ajustes", chica(A / archivo, "v2-" + pathlib.Path(archivo).stem)))
        lamina(foto, celdas, f"lamina-ajuste-{pathlib.Path(archivo).stem}.jpg")
        figuras = "".join(f'<figure><a href="{s}"><img src="{s}" loading="lazy"></a><figcaption>{t}</figcaption></figure>'
                          for t, s in celdas)
        ajustes.append(f"<section><h3>{NOMBRES.get(foto, foto)} · {TITULO_MODO.get(modo, modo)} {html.escape(extra)}</h3>"
                       f"<div class='fila'>{figuras}</div></section>")

tiempos = [r["segundos"] for r in R["restauraciones"] + R["cambios"] if r.get("segundos") and not r.get("nota")]
pagina = f"""<!doctype html><html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Pruebas de restauración</title><style>
:root{{--fondo:#FFFAEB;--tinta:#1A1712;--gris:#5A5345;--acento:#D7301F}}
body{{margin:0;background:var(--fondo);color:var(--tinta);font:16px/1.5 system-ui,sans-serif;padding:24px 16px}}
main{{max-width:1200px;margin:0 auto}} h1{{margin:0 0 4px}} h2{{margin:32px 0 4px}} .meta{{color:var(--gris);margin:0 0 12px}}
.fila{{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:12px}}
figure{{margin:0}} img{{width:100%;height:auto;border:2px solid var(--tinta);border-radius:6px;display:block}}
figcaption{{font-weight:700;margin-top:4px}} section{{border-top:2px solid var(--tinta);padding-top:8px;margin-top:24px}}
.error{{color:var(--acento);font-weight:700}} details{{margin-top:8px}} q{{font-style:italic}}
</style></head><body><main>
<h1>Pruebas de restauración · {C.name}</h1>
<p class="meta">{len([r for r in R['restauraciones'] if r.get('archivo')])} restauraciones en los 3 modos y {len(R['cambios'])} pedidos de cambio.
Tiempo por foto: {min(tiempos) if tiempos else '?'}–{max(tiempos) if tiempos else '?'} s, con 3 a la vez. Total: {R.get('minutos_total', '?')} min.
{f"<b class='error'>Fallas: {len(fallas)}</b>" if fallas else 'Sin fallas.'} Hacé clic en una imagen para verla grande.</p>
<h2>1. Los tres modos de color</h2>{''.join(filas)}
<h2>2. Pedidos de cambio</h2>{''.join(cambios)}
{('<h2>3. Después de corregir los prompts</h2><p class="meta">Problemas de la primera vuelta: los modos sin color '
  'coloreaban carteles y envases; en fotos a color desteñidas, «A color» y «Mantener» salían iguales; y en un cambio '
  'una persona borrosa del fondo cambió de identidad.</p>' + ''.join(ajustes)) if ajustes else ''}
</main></body></html>"""
(C / "informe.html").write_text(pagina, encoding="utf-8")
print("informe:", C / "informe.html")
