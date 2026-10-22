"""Tercera vuelta (13/10): modos "A color" vs "Mantener colores de época" con la definición del usuario, y pedidos
de cambio aplicados SOBRE la versión que vio el cliente (como hace ahora el bot).

  python probar_modos_y_cambios.py <carpeta-con-fichas> <carpeta-de-salida>
"""
import concurrent.futures as cf
import json
import pathlib
import sys
import time

AQUI = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI.parents[1] / "tienda" / "herramientas"))
import bot  # noqa: E402
import restauracion  # noqa: E402

sys.stdout.reconfigure(encoding="utf-8")
FICHAS, SALIDA = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2])
SALIDA.mkdir(parents=True, exist_ok=True)
WEB = AQUI.parents[1] / "web" / "restauraciondefotos" / "img"
LISTOS = pathlib.Path(r"C:\Pedidos\Listos")
FOTOS = {"cumple": WEB / "muestra-antes.jpg",
         "grupo-guitarra": LISTOS / "RF-0005" / "1-original" / "foto-01.jpg",
         "pareja-estudio": LISTOS / "RF-0008" / "1-original" / "foto-01.jpg"}
MODOS = {"Color": "color", "Mantener colores de época": "mantener"}
CAMBIOS = {("pareja-estudio", "Color"): "el vestido de ella era azul con flores blancas y la corbata de él bordó",
           ("grupo-guitarra", "Color"): "la cara del señor de la guitarra quedó distinta, que se parezca más a la "
                                        "original. Y la guitarra era más clarita"}
resultados = {"restauraciones": [], "cambios": []}


def log(m):
    print(time.strftime("%H:%M:%S"), m, flush=True)


def ficha(n):
    return json.loads((FICHAS / f"{n}-ficha.json").read_text(encoding="utf-8"))


def restaurar(n, modo):
    f = ficha(n)
    prompt = restauracion.instruccion({"color": modo}, f, restauracion.referencias(f))
    base = f"{n}-{MODOS[modo]}"
    (SALIDA / f"{base}-prompt.txt").write_text(prompt, encoding="utf-8")
    t = time.time()
    bot.codex_restaurar(FOTOS[n], SALIDA / f"{base}.png", prompt)
    resultados["restauraciones"].append({"foto": n, "modo": modo, "archivo": f"{base}.png", "segundos": round(time.time() - t)})
    log(f"listo {base}")
    return n, modo


def cambiar(n, modo, nota):
    f = ficha(n)
    datos = {"color": modo}
    v = restauracion.validar_cambio(nota, datos, [FOTOS[n]])
    prompt = restauracion.instruccion_cambio(datos, f, restauracion.referencias(f), v["instruccion"], v.get("modo_color") or None)
    base = f"{n}-{MODOS[modo]}-cambio"
    (SALIDA / f"{base}-prompt.txt").write_text(prompt, encoding="utf-8")
    t = time.time()
    bot.codex_restaurar(SALIDA / f"{n}-{MODOS[modo]}.png", SALIDA / f"{base}.png", prompt, referencia=FOTOS[n])
    resultados["cambios"].append({"foto": n, "modo": modo, "nota": nota, "validacion": v, "antes": f"{n}-{MODOS[modo]}.png",
                                  "archivo": f"{base}.png", "segundos": round(time.time() - t)})
    log(f"listo {base}: {v['instruccion']}")


if __name__ == "__main__":
    inicio = time.time()
    orden = [("pareja-estudio", "Color"), ("grupo-guitarra", "Color"), ("cumple", "Color"),
             ("pareja-estudio", "Mantener colores de época"), ("grupo-guitarra", "Mantener colores de época"),
             ("cumple", "Mantener colores de época")]
    with cf.ThreadPoolExecutor(max_workers=3) as ex:
        pendientes = {ex.submit(restaurar, n, m) for n, m in orden}
        while pendientes:
            hechos, pendientes = cf.wait(pendientes, return_when=cf.FIRST_COMPLETED)
            for h in hechos:
                try:
                    clave = h.result()
                except Exception as e:
                    log(f"FALLÓ: {e}")
                    continue
                if clave in CAMBIOS and isinstance(clave, tuple) and clave[0] in FOTOS:
                    pendientes.add(ex.submit(cambiar, *clave, CAMBIOS[clave]))
    resultados["minutos_total"] = round((time.time() - inicio) / 60, 1)
    (SALIDA / "resultados.json").write_text(json.dumps(resultados, indent=2, ensure_ascii=False), encoding="utf-8")
    log(f"TERMINADO en {resultados['minutos_total']} min")
