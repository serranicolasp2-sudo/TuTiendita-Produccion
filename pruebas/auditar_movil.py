"""Auditoría móvil de las webs: emula teléfonos con Chrome (y Safari/WebKit si está instalado) y mide lo que
suele romperse en el celular. Saca capturas por pantalla.

  python auditar_movil.py <url-base> <carpeta-salida> [--webkit]
"""
import json
import pathlib
import sys

from playwright.sync_api import sync_playwright

BASE, SALIDA = sys.argv[1].rstrip("/"), pathlib.Path(sys.argv[2])
SALIDA.mkdir(parents=True, exist_ok=True)
PAGINAS = {"portal": "/tutienditaia/", "fotos": "/tutienditaia/restauraciondefotos/", "cancion": "/tutienditaia/tucancion/",
           "gracias-fotos": "/tutienditaia/restauraciondefotos/gracias.html", "gracias-cancion": "/tutienditaia/tucancion/gracias.html"}
EQUIPOS = ["iPhone SE", "iPhone 13", "Pixel 7", "Galaxy S8"]

MEDIR = r"""() => {
  const W = innerWidth, H = innerHeight;
  const desplazable = el => { for (let p = el.parentElement; p; p = p.parentElement) {
      const o = getComputedStyle(p).overflowX; if (o === 'auto' || o === 'scroll' || o === 'hidden') return true; } return false; };
  const visible = el => { const r = el.getBoundingClientRect(); const s = getComputedStyle(el);
      return r.width > 0 && r.height > 0 && s.visibility !== 'hidden' && s.display !== 'none'; };
  const texto = el => (el.innerText || el.value || el.getAttribute('aria-label') || '').trim().replace(/\s+/g, ' ').slice(0, 50);
  const desbordes = [], chicos = [], tactiles = [], zoom = [];
  for (const el of document.querySelectorAll('body *')) {
    if (!visible(el)) continue;
    const r = el.getBoundingClientRect();
    if (r.right > W + 1 && !desplazable(el)) desbordes.push(el.tagName + '.' + el.className + ' ' + Math.round(r.right) + 'px ' + texto(el));
    const fs = parseFloat(getComputedStyle(el).fontSize);
    if (fs < 13 && [...el.childNodes].some(n => n.nodeType === 3 && n.textContent.trim())) chicos.push(Math.round(fs) + 'px ' + texto(el));
  }
  for (const el of document.querySelectorAll('a, button, select, input:not([type=hidden]), textarea, summary, label.modo, label.rf-marco, label.checkbox-estilo-item')) {
    if (!visible(el)) continue;
    const r = el.getBoundingClientRect();
    const enTexto = el.tagName === 'A' && el.closest('p, li') && !el.style.minHeight;
    if ((r.height < 40 || r.width < 40) && !(el.type === 'radio' || el.type === 'checkbox') && !enTexto)
      tactiles.push(Math.round(r.width) + 'x' + Math.round(r.height) + ' ' + el.tagName + ' ' + texto(el));
    if (['INPUT', 'SELECT', 'TEXTAREA'].includes(el.tagName) && parseFloat(getComputedStyle(el).fontSize) < 16
        && !['radio', 'checkbox', 'file'].includes(el.type)) zoom.push(el.tagName + ' ' + (el.name || el.id));
  }
  const secciones = [...document.querySelectorAll('body > div > section, body > section, main > section, section')]
    .filter((s, i, a) => !a.some(o => o !== s && o.contains(s)))
    .map(s => ({titulo: texto(s.querySelector('h1, h2') || s), pantallas: +(s.getBoundingClientRect().height / H).toFixed(2)}));
  return {ancho: document.documentElement.scrollWidth, vista: W, pantallas: +(document.documentElement.scrollHeight / H).toFixed(1),
          desbordes: [...new Set(desbordes)].slice(0, 15), letraChica: [...new Set(chicos)].slice(0, 15),
          tactilesChicos: [...new Set(tactiles)].slice(0, 25), zoomIOS: zoom, secciones};
}"""


def auditar(pw, motor, equipos):
    nav = getattr(pw, motor).launch(**({"channel": "chrome"} if motor == "chromium" else {}))
    informe = {}
    for equipo in equipos:
        d = dict(pw.devices[equipo])
        d.pop("default_browser_type", None)
        ctx = nav.new_context(**d, locale="es-AR")
        for nombre, ruta in PAGINAS.items():
            pag = ctx.new_page()
            pag.goto(BASE + ruta, wait_until="networkidle")
            pag.wait_for_timeout(500)
            informe[f"{motor} · {equipo} · {nombre}"] = pag.evaluate(MEDIR)
            if equipo == "iPhone 13":
                alto = pag.evaluate("document.documentElement.scrollHeight")
                vh = d["viewport"]["height"]
                for i in range(0, min(alto, vh * 14), vh):
                    pag.evaluate(f"window.scrollTo(0, {i})")
                    pag.wait_for_timeout(250)
                    pag.screenshot(path=str(SALIDA / f"{motor}-{nombre}-{i // vh:02d}.png"))
            pag.close()
        ctx.close()
    nav.close()
    return informe


with sync_playwright() as pw:
    resultado = auditar(pw, "chromium", EQUIPOS)
    if "--webkit" in sys.argv:
        resultado |= auditar(pw, "webkit", ["iPhone SE", "iPhone 13"])
(SALIDA / "auditoria.json").write_text(json.dumps(resultado, indent=1, ensure_ascii=False), encoding="utf-8")
for k, v in resultado.items():
    print(f"{k}: ancho {v['ancho']}/{v['vista']} · {v['pantallas']} pantallas · desbordes {len(v['desbordes'])} · "
          f"letra<13 {len(v['letraChica'])} · táctiles chicos {len(v['tactilesChicos'])} · zoom iOS {len(v['zoomIOS'])}")
