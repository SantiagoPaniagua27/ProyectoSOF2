import os
import threading

DB_FILE = "fat_db.txt"
GPWD = 0
lock = threading.Lock()

def inicializar_fat():
  if not os.path.exists(DB_FILE):
    with open(DB_FILE, "w") as f:
      f.write("0|/|DIR|-1|rwx|-\n")

  print("Sistema FAT inicializando correctamente.")
  print("DIrectorio actual: /")

def leer_registros():
  registros = []

  with open(DB_FILE, "r") as f:
    lineas = f.readlines()
  
  for linea in lineas:
    datos = linea.strip().split("|")

    registro = {
      "id": int(datos[0]),
      "nombre": datos[1],
      "tipo": datos[2],
      "padre": int(datos[3]),
      "permisos": datos[4],
      "tamano": datos[5],
    }

    registros.append(registro)

    return registros

def escribir_registros(registros):
  with open(DB_FILE, "w") as f:
    for r in registros:
      linea = (
        f"{r['id']}|"
        f"{r['nombre']}|"
        f"{r['tipo']}|"
        f"{r['padre']}|"
        f"{r['permisos']}|"
        f"{r['tamano']}\n"
      )

      f.write(linea)

def obtener_nuevo_id():
  registros = leer_registros()

  if len(registros) == 0:
    return 0
  
  ultimo_id = max(r["id"] for r in registros)

  return ultimo_id + 1

def obtener_ruta_actual():
  global GPWD

  registros = leer_registros()

  if GPWD == 0:
    return "/"
  
  ruta = []

  actual = GPWD

  while actual != 0:
    for r in registros:
      if r["id"] == actual:
        ruta.append(r["nombre"])
        actual = r["padre"]
        break
  
  ruta.reverse()

  return "/" + "/".join(ruta)

def mkdir(nomnbre):
  with lock:
    registros = leer_registros()
