"""Segunda vuelta (13/10): repite los casos que fallaron con los ajustes del prompt, con las mismas fichas.

  python repetir_ajustes.py <carpeta-primera-vuelta> <carpeta-segunda-vuelta>
"""
import concurrent.futures as cf
import pathlib
import shutil
import sys
import time

V1, V2 = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2])
sys.argv = [sys.argv[0], str(V2)]
import probar_restauracion as b  # noqa: E402

for f in V1.glob("*-ficha.json"):
    shutil.copy2(f, V2 / f.name)
b.RESTAURAR = [("cumple", "Mantener colores de época"), ("cumple", "Blanco y negro"),
               ("pareja-estudio", "Mantener colores de época"),
               ("grupo-guitarra", "Color"), ("grupo-guitarra", "Mantener colores de época")]
b.CAMBIOS = [c for c in b.CAMBIOS if c[0] == "grupo-guitarra"]
inicio = time.time()
with cf.ThreadPoolExecutor(max_workers=3) as ex:
    trabajos = [ex.submit(b.tarea_restaurar, n, m) for n, m in b.RESTAURAR]
    trabajos += [ex.submit(b.tarea_cambio, 2, n, m, nota) for n, m, nota in b.CAMBIOS]
    cf.wait(trabajos)
b.resultados["minutos_total"] = round((time.time() - inicio) / 60, 1)
b.guardar()
b.log(f"TERMINADO en {b.resultados['minutos_total']} min")
