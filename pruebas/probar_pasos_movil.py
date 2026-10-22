"""Recorre los formularios en pasos como un cliente en el celular (Chrome = Android, WebKit = iPhone).

  python probar_pasos_movil.py <url-base> <carpeta-salida>
"""
import pathlib
import sys

from playwright.sync_api import sync_playwright

BASE, SALIDA = sys.argv[1].rstrip("/"), pathlib.Path(sys.argv[2])
SALIDA.mkdir(parents=True, exist_ok=True)
FOTO = pathlib.Path(r"C:\Users\Nicolás\Desktop\Proyectos\RegalosIA\web\restauraciondefotos\img\cuadro-madera.webp")
errores = []


def chequear(cond, msg):
    print(("  ok  " if cond else "  MAL ") + msg)
    if not cond:
        errores.append(msg)


def titulo(p):
    return p.locator(".m-pasos-titulo").inner_text()


def siguiente(p):
    p.locator(".m-paso:not([hidden]) .m-siguiente").click()
    p.wait_for_timeout(400)


def recorrer(pw, motor, equipo):
    nav = getattr(pw, motor).launch(**({"channel": "chrome"} if motor == "chromium" else {}))
    d = dict(pw.devices[equipo]); d.pop("default_browser_type", None)
    ctx = nav.new_context(**d, locale="es-AR")
    p = ctx.new_page()
    print(f"== {motor} · {equipo} · fotos")
    p.goto(BASE + "/tutienditaia/restauraciondefotos/", wait_until="networkidle")
    chequear(titulo(p).startswith("Paso 1 de 2"), f"1 foto empieza en 'Paso 1 de 2': {titulo(p)}")
    siguiente(p)
    chequear(titulo(p).startswith("Paso 1"), "sin foto no avanza")
    p.set_input_files("#rf-fotos", str(FOTO))
    siguiente(p)
    chequear("Tus datos" in titulo(p), f"con foto pasa a los datos: {titulo(p)}")
    p.locator("form").scroll_into_view_if_needed()
    p.screenshot(path=str(SALIDA / f"{motor}-fotos-paso-datos.png"))
    p.locator('[data-prod-id="rf-cuadro-enmarcado-20x30"]').click()
    p.wait_for_timeout(300)
    chequear(titulo(p).startswith("Paso 1 de 3"), f"cuadro enmarcado: 3 pasos y vuelve al 1: {titulo(p)}")
    chequear(p.locator("#rf-seccion-marco").is_visible(), "aparece el color del marco")
    p.set_input_files("#rf-fotos", str(FOTO))
    siguiente(p)
    chequear(titulo(p).startswith("Paso 1"), "sin marco no avanza")
    p.locator('#rf-seccion-marco label').nth(1).click()
    siguiente(p)
    chequear("Envío" in titulo(p) and p.locator("#envio_calle").is_visible(), f"paso de envío: {titulo(p)}")
    p.locator("form").scroll_into_view_if_needed()
    p.screenshot(path=str(SALIDA / f"{motor}-fotos-paso-envio.png"))
    p.locator('[data-prod-id="rf-foto-1"]').click()
    p.wait_for_timeout(300)
    p.locator("form").scroll_into_view_if_needed()
    p.screenshot(path=str(SALIDA / f"{motor}-fotos-paso-1.png"))

    print(f"== {motor} · {equipo} · canción")
    p.goto(BASE + "/tutienditaia/tucancion/", wait_until="networkidle")
    chequear(titulo(p).startswith("Paso 1 de 3"), f"canción en 3 pasos: {titulo(p)}")
    siguiente(p)
    chequear(titulo(p).startswith("Paso 1"), "sin 'para quién' no avanza")
    p.fill('[name="para_quien"]', "Mamá")
    siguiente(p)
    chequear(p.locator(".m-pasos-error").is_visible() and titulo(p).startswith("Paso 1"), "sin estilo avisa y no avanza")
    p.locator('.checkbox-estilo-item').first.click()
    siguiente(p)
    chequear("historia" in titulo(p).lower(), f"pasa a la historia: {titulo(p)}")
    p.locator("form").scroll_into_view_if_needed()
    p.screenshot(path=str(SALIDA / f"{motor}-cancion-paso-historia.png"))
    siguiente(p)
    chequear("historia" in titulo(p).lower(), "historia vacía no avanza")
    p.fill('[name="historia"]', "Mi mamá cantaba boleros mientras cocinaba los domingos en la casa de Sarandí.")
    siguiente(p)
    chequear("Tus datos" in titulo(p), f"pasa a los datos: {titulo(p)}")
    p.locator(".m-paso:not([hidden]) .m-atras").click()
    p.wait_for_timeout(300)
    chequear("historia" in titulo(p).lower(), "Atrás vuelve un paso")
    p.goto(BASE + "/tutienditaia/tucancion/", wait_until="networkidle")
    p.locator("form").scroll_into_view_if_needed()
    p.screenshot(path=str(SALIDA / f"{motor}-cancion-paso-1.png"))
    for nombre, ruta in (("fotos", "/tutienditaia/restauraciondefotos/"), ("cancion", "/tutienditaia/tucancion/")):
        p.goto(BASE + ruta, wait_until="networkidle")
        h = p.locator("section ol").first
        h.scroll_into_view_if_needed()
        p.evaluate("window.scrollBy(0, -80)")
        p.wait_for_timeout(300)
        p.screenshot(path=str(SALIDA / f"{motor}-{nombre}-slides.png"))
        p.evaluate("window.scrollTo(0, 0)")
        p.wait_for_timeout(200)
        p.screenshot(path=str(SALIDA / f"{motor}-{nombre}-arriba.png"))
        ancho = p.evaluate("[document.documentElement.scrollWidth, innerWidth]")
        chequear(ancho[0] <= ancho[1], f"{nombre}: sin scroll horizontal {ancho}")
        pantallas = p.evaluate("(document.documentElement.scrollHeight / innerHeight).toFixed(1)")
        print(f"  {nombre}: {pantallas} pantallas")
    nav.close()


with sync_playwright() as pw:
    recorrer(pw, "chromium", "Pixel 7")
    recorrer(pw, "webkit", "iPhone 13")
print("ERRORES:", errores or "ninguno")
