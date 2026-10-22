"""Banco de pruebas de restauración: mismas funciones que el bot, sin tocar pedidos ni el servidor.

  python probar_restauracion.py <carpeta-de-salida>

Por cada caso: análisis (una vez por foto), restauración en cada modo de color pedido y pedidos de cambio
(validación + rehacer desde el original, como el bot). Deja resultados.json, las imágenes y los prompts.
"""
import concurrent.futures as cf
import json
import pathlib
import shutil
import sys
import threading
import time

AQUI = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI.parents[1] / "tienda" / "herramientas"))
import bot  # noqa: E402
import restauracion  # noqa: E402

sys.stdout.reconfigure(encoding="utf-8")
SALIDA = pathlib.Path(sys.argv[1])
SALIDA.mkdir(parents=True, exist_ok=True)
WEB = AQUI.parents[1] / "web" / "restauraciondefotos" / "img"
LISTOS = pathlib.Path(r"C:\Pedidos\Listos")

FOTOS = {
    "cumple": WEB / "muestra-antes.jpg",
    "grupo-guitarra": LISTOS / "RF-0005" / "1-original" / "foto-01.jpg",
    "pareja-estudio": LISTOS / "RF-0008" / "1-original" / "foto-01.jpg",
    "retrato-gorro": LISTOS / "RF-0009" / "1-original" / "foto-01.jpg",
    "abuelo-nene": LISTOS / "RF-0006" / "1-original" / "foto-01.jpg",
}
MODOS = {"Color": "color", "Mantener colores de época": "mantener", "Blanco y negro": "byn"}
RESTAURAR = [  # (foto, modo)
    ("cumple", "Mantener colores de época"), ("cumple", "Blanco y negro"),
    ("grupo-guitarra", "Color"), ("grupo-guitarra", "Mantener colores de época"), ("grupo-guitarra", "Blanco y negro"),
    ("pareja-estudio", "Color"), ("pareja-estudio", "Mantener colores de época"), ("pareja-estudio", "Blanco y negro"),
    ("retrato-gorro", "Blanco y negro"),
]
CAMBIOS = [  # (foto, modo con el que compró, comentario del cliente)
    ("pareja-estudio", "Color", "el vestido de ella era azul con flores blancas y la corbata de él bordó"),
    ("grupo-guitarra", "Color", "la cara del señor de la guitarra quedó distinta, que se parezca más a la original. "
                                "Y la guitarra era más clarita"),
    ("retrato-gorro", "Blanco y negro", "mejor pasala a color, el gorro era rojo"),
    ("cumple", "Mantener colores de época", "sacale lo amarillento, que quede más neutra"),
    ("cumple", "Color", "que la nena de adelante sonría más y sacá al nene de la derecha"),
    ("abuelo-nene", "Color", "jajaja ok"),
]

lock = threading.Lock()
resultados = {"fichas": {}, "restauraciones": [], "cambios": []}


def guardar():
    with lock:
        (SALIDA / "resultados.json").write_text(json.dumps(resultados, indent=2, ensure_ascii=False), encoding="utf-8")


def log(msg):
    with lock:
        print(time.strftime("%H:%M:%S"), msg, flush=True)


def ficha(nombre):
    ruta = SALIDA / f"{nombre}-ficha.json"
    if ruta.exists():
        return json.loads(ruta.read_text(encoding="utf-8"))
    t = time.time()
    f = restauracion.analizar(FOTOS[nombre], {"color": "Color"})
    ruta.write_text(json.dumps(f, indent=2, ensure_ascii=False), encoding="utf-8")
    log(f"análisis {nombre}: {time.time() - t:.0f} s, {len(f['elementos'])} objetos, época {f['epoca']}")
    resultados["fichas"][nombre] = {"segundos": round(time.time() - t), **f}
    guardar()
    return f


def restaurar(nombre, modo, cambio=None, sufijo=""):
    f = json.loads((SALIDA / f"{nombre}-ficha.json").read_text(encoding="utf-8"))
    datos = {"color": modo, "comentarios": ""}
    prompt = restauracion.instruccion(datos, f, restauracion.referencias(f), cambio)
    base = f"{nombre}-{MODOS[modo]}{sufijo}"
    (SALIDA / f"{base}-prompt.txt").write_text(prompt, encoding="utf-8")
    t = time.time()
    bot.codex_restaurar(FOTOS[nombre], SALIDA / f"{base}.png", prompt)
    seg = round(time.time() - t)
    log(f"listo {base}: {seg} s")
    return base, seg


def tarea_restaurar(nombre, modo):
    try:
        base, seg = restaurar(nombre, modo)
        r = {"foto": nombre, "modo": modo, "archivo": f"{base}.png", "segundos": seg}
    except Exception as e:
        log(f"FALLÓ {nombre} {modo}: {e}")
        r = {"foto": nombre, "modo": modo, "error": str(e)}
    with lock:
        resultados["restauraciones"].append(r)
    guardar()


def tarea_cambio(i, nombre, modo, nota):
    t = time.time()
    try:
        v = restauracion.validar_cambio(nota, {"color": modo, "comentarios": ""}, [FOTOS[nombre]])
        r = {"n": i, "foto": nombre, "modo": modo, "nota": nota, "validacion": v,
             "segundos_validacion": round(time.time() - t)}
        log(f"cambio {i} ({nombre}): {'válido' if v['valida'] else 'NO válido'} → {v['instruccion'] or v['rechazado']}")
        if v["valida"] and v["instruccion"].strip():
            modo_final = v.get("modo_color") or modo
            base, seg = restaurar(nombre, modo_final, v["instruccion"], sufijo=f"-cambio{i}")
            r.update(archivo=f"{base}.png", modo_final=modo_final, segundos=seg)
    except Exception as e:
        log(f"FALLÓ cambio {i}: {e}")
        r = {"n": i, "foto": nombre, "modo": modo, "nota": nota, "error": str(e)}
    with lock:
        resultados["cambios"].append(r)
    guardar()


if __name__ == "__main__":
    inicio = time.time()
    shutil.copy2(AQUI.parents[1] / "produccion" / "referencias" / "prueba-cumple-con-referencias.jpg",
                 SALIDA / "cumple-color.jpg")   # el modo Color del cumpleaños ya se hizo el 09/10
    resultados["restauraciones"].append({"foto": "cumple", "modo": "Color", "archivo": "cumple-color.jpg",
                                         "segundos": 347, "nota": "hecha el 09/10"})
    for n in FOTOS:
        if n != "abuelo-nene":
            ficha(n)
    with cf.ThreadPoolExecutor(max_workers=3) as ex:
        trabajos = [ex.submit(tarea_restaurar, n, m) for n, m in RESTAURAR]
        trabajos += [ex.submit(tarea_cambio, i, n, m, nota) for i, (n, m, nota) in enumerate(CAMBIOS, 1)]
        cf.wait(trabajos)
    resultados["minutos_total"] = round((time.time() - inicio) / 60, 1)
    guardar()
    log(f"TERMINADO en {resultados['minutos_total']} min")
