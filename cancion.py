"""Producción de canciones: carpeta por pedido, vista previa de 1 minuto, registro de cambios y entrega con la descarga oficial.

Flujo (ver LEEME.md):
  python cancion.py nuevo TC-0101                 crea C:\\Pedidos\\TC\\Pendientes\\TC-0101\\{1-datos,2-letra,3-vistas-previas,4-entrega}
  python cancion.py previa TC-0101                graba 1 minuto de lo que suena en la PC (le das play en Suno)
  python cancion.py cambio TC-0101 "más lenta"    anota el cambio que pidió el cliente (hasta 5)
  python cancion.py final TC-0101 "C:\\...\\descarga.mp3" --para "Marta"
                                                   copia la DESCARGA OFICIAL de Suno a 4-entrega, con nombre y datos
  python cancion.py listo TC-0101                 mueve el pedido a C:\\Pedidos\\TC\\Listos
Los pedidos de la tienda ya vienen con carpeta (pedidos.py traer / el bot) y su historial.txt.
"""
import argparse, pathlib, re, subprocess, sys, tempfile, wave

import carpetas

PEDIDOS = carpetas.PEDIDOS
CAMBIOS_MAX = 5
SEGUNDOS = 60
ESPERA_MAX = 120          # segundos esperando a que empiece a sonar
UMBRAL = 0.01             # nivel a partir del cual se considera que la canción empezó
RATE = 48_000

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


def carpeta(pedido, estado="Pendientes"):
    return carpetas.carpeta(pedido, estado, defecto="TC")


def registro(pedido):
    return carpeta(pedido) / carpetas.HISTORIAL


def anotar(pedido, linea):
    carpetas.anotar(carpeta(pedido), linea)


def previas(pedido):
    return sorted((carpeta(pedido) / "3-vistas-previas").glob("v*-previa.mp3"))


def cambios_usados(pedido):
    if not registro(pedido).exists():
        return 0
    return max((int(n) for n in re.findall(r"\] Cambio (\d+)", registro(pedido).read_text(encoding="utf-8"))), default=0)


def nuevo(a):
    base = carpeta(a.pedido)
    for sub in ("1-datos", "2-letra", "3-vistas-previas", "4-entrega"):
        (base / sub).mkdir(parents=True, exist_ok=True)
    if not registro(a.pedido).exists():
        anotar(a.pedido, f"Pedido {a.pedido} creado a mano")
    print(f"Listo: {base}\n  1-datos   respuestas del formulario\n  2-letra   la letra (prompts/letra-cancion.md)")


def grabar_loopback(segundos):
    import numpy as np
    import soundcard as sc
    mic = sc.get_microphone(id=str(sc.default_speaker().name), include_loopback=True)
    bloque = RATE // 10
    with mic.recorder(samplerate=RATE, channels=2) as r:
        print(f"Dale play en Suno desde el principio. Espero hasta {ESPERA_MAX} s a que empiece a sonar…")
        for _ in range(ESPERA_MAX * 10):
            primero = r.record(numframes=bloque)
            if np.abs(primero).max() > UMBRAL:
                break
        else:
            sys.exit("No escuché nada. ¿Está sonando por los altavoces predeterminados de Windows?")
        print(f"Grabando {segundos} s…")
        resto = r.record(numframes=RATE * segundos - bloque)
    datos = np.concatenate([primero, resto])
    return (np.clip(datos, -1, 1) * 32767).astype("<i2")


def previa(a):
    base = carpeta(a.pedido)
    if not base.exists():
        sys.exit(f"No existe {base}. Primero: cancion.py nuevo {a.pedido}")
    n = len(previas(a.pedido)) + 1
    if n > CAMBIOS_MAX + 1:
        sys.exit(f"Ya hay {n - 1} versiones: se usaron los {CAMBIOS_MAX} cambios incluidos.")
    datos = grabar_loopback(a.segundos)
    wav = pathlib.Path(tempfile.gettempdir()) / f"tc-previa-{a.pedido}.wav"
    with wave.open(str(wav), "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(RATE); w.writeframes(datos.tobytes())
    salida = base / "3-vistas-previas" / f"v{n}-previa.mp3"
    fin = a.segundos - 4
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(wav),
                    "-af", f"afade=t=in:d=0.3,afade=t=out:st={fin}:d=4", "-ac", "2", "-b:a", "128k",
                    "-metadata", "title=Vista previa · Tu Canción", "-metadata", "artist=tucancion.com.ar", str(salida)],
                   check=True)
    wav.unlink()
    anotar(a.pedido, f"Vista previa v{n} grabada ({a.segundos} s): 3-vistas-previas\{salida.name}")
    restantes = CAMBIOS_MAX - cambios_usados(a.pedido)
    print(f"Listo: {salida}\nMandásela al cliente. Cambios disponibles: {restantes} de {CAMBIOS_MAX}.")


def cambio(a):
    usados = cambios_usados(a.pedido)
    if usados >= CAMBIOS_MAX:
        sys.exit(f"Ya se usaron los {CAMBIOS_MAX} cambios incluidos. Un cambio más se cotiza aparte.")
    anotar(a.pedido, f"Cambio {usados + 1}/{CAMBIOS_MAX} (anotado a mano): {a.texto}")
    print(f"Anotado. Quedan {CAMBIOS_MAX - usados - 1} cambios. Generá la nueva versión en Suno y grabá otra previa.")


def final(a):
    origen = pathlib.Path(a.archivo)
    if not origen.exists():
        sys.exit(f"No encuentro {origen}")
    nombre = f"Tu canción para {a.para}.mp3" if a.para else f"Tu canción {a.pedido}.mp3"
    salida = carpeta(a.pedido) / "4-entrega" / nombre
    codec = ["-c:a", "copy"] if origen.suffix.lower() == ".mp3" else ["-c:a", "libmp3lame", "-b:a", "320k"]
    titulo = f"Para {a.para}" if a.para else "Tu canción"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(origen), "-map", "0:a", *codec,
                    "-metadata", f"title={titulo}", "-metadata", "artist=Tu Canción",
                    "-metadata", "comment=tucancion.com.ar", str(salida)], check=True)
    anotar(a.pedido, f"Versión final lista con la descarga oficial de Suno ({origen.name}): 4-entrega\{nombre}")
    print(f"Listo para entregar: {salida}")


def listo(a):
    destino = carpetas.mover_a_listos(a.pedido, defecto="TC")
    print(f"Movido a {destino}.")


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    for nombre, fn in (("nuevo", nuevo), ("listo", listo)):
        s = sub.add_parser(nombre); s.add_argument("pedido"); s.set_defaults(fn=fn)
    s = sub.add_parser("previa"); s.add_argument("pedido"); s.add_argument("--segundos", type=int, default=SEGUNDOS); s.set_defaults(fn=previa)
    s = sub.add_parser("cambio"); s.add_argument("pedido"); s.add_argument("texto"); s.set_defaults(fn=cambio)
    s = sub.add_parser("final"); s.add_argument("pedido"); s.add_argument("archivo"); s.add_argument("--para", default=""); s.set_defaults(fn=final)
    a = p.parse_args()
    a.fn(a)
