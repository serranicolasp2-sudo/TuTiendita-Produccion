"""Dónde vive cada pedido en la PC y su historial (13/10).

  C:\\Pedidos\\RF\\Pendientes\\RF-0010 - Agapito Gonzalez\\     fotos, mientras se trabaja
  C:\\Pedidos\\RF\\Listos\\RF-0010 - Agapito Gonzalez\\         fotos entregadas (se borran a los 30 días)
  C:\\Pedidos\\TC\\Pendientes\\TC-0002 - Casimiro tuculo\\      canciones (igual)

El nombre lleva el del comprador tal como lo escribió en el formulario, para ubicarlo rápido. Los scripts buscan
la carpeta por el número de pedido, así que se puede renombrar a mano si conviene (mientras empiece con el número).
Cada carpeta tiene historial.txt: lo pedido, cada cambio y lo que se hizo, para contrastar con los resultados.
"""
import datetime
import pathlib
import re
import shutil

PEDIDOS = pathlib.Path(r"C:\Pedidos")
TIPOS = ("RF", "TC")
ESTADOS = ("Pendientes", "Listos")
HISTORIAL = "historial.txt"


def tipo(pid: str, defecto: str = "RF") -> str:
    t = pid.split("-")[0].upper()
    return t if t in TIPOS else defecto


def nombre_carpeta(pid: str, comprador: str = "") -> str:
    limpio = re.sub(r'[<>:"/\\|?*\x00-\x1f]', "", comprador or "")
    limpio = re.sub(r"\s+", " ", limpio).strip()[:40].rstrip(". ")
    return f"{pid} - {limpio}" if limpio else pid


def buscar(pid: str, estado: str | None = None) -> pathlib.Path | None:
    """La carpeta del pedido ("RF-0010" o "RF-0010 - …"), en el estado pedido o en cualquiera."""
    for e in ([estado] if estado else ESTADOS):
        for t in TIPOS:
            raiz = PEDIDOS / t / e
            if not raiz.exists():
                continue
            for c in raiz.iterdir():
                if c.is_dir() and (c.name == pid or c.name.startswith(pid + " ")):
                    return c
    return None


def carpeta(pid: str, estado: str = "Pendientes", comprador: str = "", defecto: str = "RF") -> pathlib.Path:
    """La que existe en ese estado o, si no hay, dónde va (no la crea)."""
    return buscar(pid, estado) or PEDIDOS / tipo(pid, defecto) / estado / nombre_carpeta(pid, comprador)


def mover_a_listos(pid: str, defecto: str = "RF") -> pathlib.Path:
    origen = buscar(pid, "Pendientes")
    if not origen:
        raise FileNotFoundError(f"No encuentro {pid} en Pendientes")
    destino = PEDIDOS / tipo(pid, defecto) / "Listos" / origen.name
    destino.parent.mkdir(parents=True, exist_ok=True)
    if destino.exists():                    # ya se había entregado (por ejemplo, una reentrega): se juntan
        shutil.copytree(origen, destino, dirs_exist_ok=True)
        shutil.rmtree(origen)
    else:
        shutil.move(str(origen), str(destino))
    return destino


def listos() -> list[pathlib.Path]:
    return [c for t in TIPOS if (PEDIDOS / t / "Listos").exists() for c in (PEDIDOS / t / "Listos").iterdir() if c.is_dir()]


def anotar(base: pathlib.Path, texto: str):
    """Agrega una entrada con fecha a historial.txt (las líneas siguientes van con sangría)."""
    hora = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
    lineas = str(texto).strip().splitlines() or [""]
    bloque = f"[{hora}] {lineas[0]}\n" + "".join(f"    {l}\n" if l.strip() else "\n" for l in lineas[1:])
    base.mkdir(parents=True, exist_ok=True)
    with (base / HISTORIAL).open("a", encoding="utf-8") as f:
        f.write(bloque + "\n")


def anotar_pid(pid: str, texto: str):
    base = buscar(pid)
    if base:
        anotar(base, texto)
