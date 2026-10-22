"""Producción de fotos restauradas: carpeta por pedido, Real-ESRGAN, vista previa con marca de agua y comparativa.

Flujo (ver LEEME.md):
  python fotos.py nuevo RF-0001          crea C:\\Pedidos\\RF\\Pendientes\\RF-0001\\{1-original,2-codex,3-entrega}
  (vos) guardás la foto del cliente en 1-original y la versión de Codex/ChatGPT en 2-codex, con el mismo nombre
  python fotos.py procesar RF-0001       mejora la resolución, arma la vista previa y la comparativa
  python fotos.py listo RF-0001          mueve el pedido a C:\\Pedidos\\RF\\Listos
"""
import pathlib, subprocess, sys, tempfile
from PIL import Image, ImageDraw, ImageFont, ImageOps

import carpetas

AQUI = pathlib.Path(__file__).parent
PEDIDOS = carpetas.PEDIDOS
ESRGAN = AQUI / "herramientas" / "realesrgan" / "realesrgan-ncnn-vulkan.exe"
SIMBOLO_SVG = AQUI.parent / "marca" / "restauracion-de-fotos" / "assets" / "logos" / "rf-simbolo.svg"
MARCA_AGUA = AQUI / "herramientas" / "marca-agua.png"
CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
LADO_MAX_FINAL = 4800      # alcanza para imprimir 30x40 cm a 300 dpi
LADO_MAX_PREVIA = 1200
EXT = {".jpg", ".jpeg", ".png", ".webp"}
CINTA, YEMA = (26, 23, 18), (255, 210, 63)

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


def carpeta(pedido, estado="Pendientes"):
    return carpetas.carpeta(pedido, estado, defecto="RF")


def nuevo(pedido):
    base = carpeta(pedido)
    for sub in ("1-original", "2-codex", "3-entrega"):
        (base / sub).mkdir(parents=True, exist_ok=True)
    print(f"Listo: {base}\n  1-original  la foto que mandó el cliente\n  2-codex     la versión de Codex/ChatGPT (mismo nombre de archivo)")


def marca_agua():
    """Convierte rf-simbolo.svg a PNG transparente una sola vez (con Chrome headless)."""
    if MARCA_AGUA.exists():
        return Image.open(MARCA_AGUA).convert("RGBA")
    MARCA_AGUA.parent.mkdir(parents=True, exist_ok=True)
    html = pathlib.Path(tempfile.gettempdir()) / "rf-marca-agua.html"
    html.write_text(f'<html><body style="margin:0;background:transparent">'
                    f'<img src="{SIMBOLO_SVG.as_uri()}" style="width:600px;height:600px;object-fit:contain"></body></html>',
                    encoding="utf-8")
    subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars", "--window-size=600,600",
                    "--default-background-color=00000000", f"--screenshot={MARCA_AGUA}", html.as_uri()],
                   check=True, capture_output=True)
    return Image.open(MARCA_AGUA).convert("RGBA")


def esrgan(entrada, salida):
    if not ESRGAN.exists():
        sys.exit(f"Falta Real-ESRGAN en {ESRGAN.parent}. Ver LEEME.md, paso de instalación.")
    subprocess.run([str(ESRGAN), "-i", str(entrada), "-o", str(salida), "-n", "realesrgan-x4plus", "-s", "4"],
                   check=True, capture_output=True, cwd=ESRGAN.parent)


def achicar(im, lado):
    im = im.copy()
    im.thumbnail((lado, lado), Image.LANCZOS)
    return im


def fuente(tam):
    for f in ("arialbd.ttf", "segoeuib.ttf", "DejaVuSans-Bold.ttf"):
        try:
            return ImageFont.truetype(f, tam)
        except OSError:
            continue
    return ImageFont.load_default()


def vista_previa(im):
    """Versión chica con el símbolo repetido en diagonal y una franja con el dominio. No sirve para imprimir."""
    im = achicar(im, LADO_MAX_PREVIA).convert("RGBA")
    w, h = im.size
    simbolo = marca_agua()
    lado = max(w, h) // 5
    simbolo = achicar(simbolo, lado)
    alfa = simbolo.getchannel("A").point(lambda a: int(a * 0.28))
    simbolo.putalpha(alfa)
    capa = Image.new("RGBA", im.size, (0, 0, 0, 0))
    paso = int(lado * 1.25)
    for fila, y in enumerate(range(-lado, h + lado, paso)):
        for x in range(-lado + (fila % 2) * paso // 2, w + lado, paso):
            capa.alpha_composite(simbolo, (x, y))
    im = Image.alpha_composite(im, capa)
    d = ImageDraw.Draw(im)
    alto = max(36, h // 18)
    d.rectangle([0, h - alto, w, h], fill=CINTA + (230,))
    d.text((w // 2, h - alto // 2), "VISTA PREVIA · restauraciondefotos.com.ar", fill=YEMA, font=fuente(alto // 2), anchor="mm")
    return im.convert("RGB")


def comparativa(original, restaurada):
    """Antes y después lado a lado, misma altura, para revisar las caras antes de mandar nada."""
    alto = 1400
    a = ImageOps.contain(original.convert("RGB"), (10_000, alto))
    b = ImageOps.contain(restaurada.convert("RGB"), (10_000, alto))
    margen, rotulo = 30, 70
    hoja = Image.new("RGB", (a.width + b.width + margen * 3, alto + margen * 2 + rotulo), YEMA)
    hoja.paste(a, (margen, margen + rotulo))
    hoja.paste(b, (a.width + margen * 2, margen + rotulo))
    d = ImageDraw.Draw(hoja)
    f = fuente(40)
    d.text((margen, margen + rotulo // 2), "ANTES", fill=CINTA, font=f, anchor="lm")
    d.text((a.width + margen * 2, margen + rotulo // 2), "DESPUÉS: ¿son las mismas caras?", fill=CINTA, font=f, anchor="lm")
    return hoja


def procesar(pedido, estado="Pendientes", solo=None):
    base = carpetas.carpeta(pedido, estado=estado, defecto="RF")
    if not (base / "2-codex").exists():
        raise FileNotFoundError(f"No existe {base / '2-codex'}")
    codex = [p for p in sorted((base / "2-codex").iterdir()) if p.suffix.lower() in EXT]
    if solo:
        stems = set(solo) if isinstance(solo, (list, tuple, set)) else {str(solo)}
        codex = [p for p in codex if p.stem in stems]
    if not codex:
        if solo:
            raise FileNotFoundError(f"No se encontraron las fotos especificadas en {base / '2-codex'}: {solo}")
        sys.exit(f"No hay fotos en {base / '2-codex'}")
    originales = {p.stem: p for p in (base / "1-original").iterdir() if p.suffix.lower() in EXT}
    salida = base / "3-entrega"
    for foto in codex:
        tmp = salida / f"_x4_{foto.stem}.png"
        print(f"{foto.name}: Real-ESRGAN x4…")
        esrgan(foto, tmp)
        final = achicar(Image.open(tmp).convert("RGB"), LADO_MAX_FINAL)
        tmp.unlink()
        final.save(salida / f"{foto.stem}-final.jpg", quality=95, subsampling=0, dpi=(300, 300))
        vista_previa(final).save(salida / f"{foto.stem}-vista-previa.jpg", quality=85)
        if foto.stem in originales:
            comparativa(Image.open(originales[foto.stem]), final).save(salida / f"{foto.stem}-comparativa.jpg", quality=88)
        else:
            print(f"  (no encontré {foto.stem} en 1-original: sin comparativa)")
        print(f"  final {final.size[0]}x{final.size[1]} · vista previa · comparativa")
    print(f"\nRevisá las comparativas en {salida} antes de mandar la vista previa.")


def listo(pedido):
    destino = carpetas.mover_a_listos(pedido, defecto="RF")
    print(f"Movido a {destino}. Recordá: las fotos del cliente se borran a los 30 días.")


if __name__ == "__main__":
    if len(sys.argv) != 3 or sys.argv[1] not in {"nuevo", "procesar", "listo"}:
        sys.exit(__doc__)
    {"nuevo": nuevo, "procesar": procesar, "listo": listo}[sys.argv[1]](sys.argv[2])
