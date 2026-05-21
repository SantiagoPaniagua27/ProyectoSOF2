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

def mkdir(nombre):
  with lock:
    registros = leer_registros()

    for r in registros:
      if r["nombre"] == nombre and r["padre"] == GPWD:
        print("Ese directorio ya existe.")
        return

    nuevo_id = obtener_nuevo_id()

    with open(DB_FILE, "a") as f:
      f.write(
        f"{nuevo_id}|"
        f"{nombre}|"
        f"DIR|"
        f"{GPWD}|"
        f"rwx|-"
        f"\n"
      )

    print(f"Directorio '{nombre}' creado correctamente.")

def touch(nombre):
  with lock:
    registros = leer_registros()

    for r in registros:
      if r["nombre"] == nombre and r["padre"] == GPWD:
        print("Ese archivo ya existe.")
        return
    
    nuevo_id = obtener_nuevo_id()

    with open(DB_FILE, "a") as f:
      f.write(
        f"{nuevo_id}|"
        f"{nombre}|"
        f"FILE|"
        f"{GPWD}|"
        f"rw-|0"
        f"\n"
      )
    
    print(f"Archivo '{nombre}' creado correctamente")

def ls():
  registros = leer_registros()
  encontrados = []

  for r in registros:
    if r["padre"] == GPWD:
      encontrados.append(r["nombre"])

  if len(encontrados) == 0:
    print("Directorio vacío.")
  else:
    for nombre in encontrados:
      print(nombre)

def ls_l():
  registros = leer_registros()
  
  print("ID | TIPO | PERMISOS | TAMAÑO | NOMBRE")
  
  encontrado = False

  for r in registros:
    if r["padre"] == GPWD:
      print(
        f"{r['id']} | "
        f"{r['tipo']} | "
        f"{r['permisos']} | "
        f"{r['tamano']} | "
        f"{r['nombre']}"
      )

      encontrado = True
  
  if not encontrado:
    print("No hay archivos o directorios")

def cd(nombre):
  global GPWD

  registros = leer_registros()

  if nombre == "..":
    if GPWD == 0:
      print("Ya estas en el directorio raíz")
      return
    
    for r in registros:
      if r["id"] == GPWD:
        GPWD = r["padre"]
        print(f"Directorio actual cambiado a: {obtener_ruta_actual()}")
        return
    
  for r in registros:
    if(
      r["nombre"] == nombre
      and r["tipo"] == "DIR"
      and r["padre"] == GPWD
    ):
      GPWD = r["id"]
      print(f"Directorio actual cambiado a: {obtener_ruta_actual()}")
      return
  print("Directorio no encontrado")

def chmod(permisos, nombre):
  registros = leer_registros()
  encontrado = False

  for r in registros:
    if r["nombre"] == nombre and r["padre"] == GPWD:
      r["permisos"] = permisos
      encontrado = True
      break
  
  if encontrado:
    escribir_registros(registros)
    print (f"Permisos de '{nombre}' cambiados a {permisos}")
  else:
    print("Archivo o directorio no encontrado")

def rm(nombre):
  registros = leer_registros()
  nuevos_registros = []
  eliminado = False

  for r in registros:
    if r["nombre"] == nombre and r["padre"] == GPWD:
      if r["tipo"] == "DIR":
        print("No se puede eliminar un directorio con rm")
        return
      
      eliminado = True
      continue

    nuevos_registros.append(r)

  if eliminado:
    escribir_registros(nuevos_registros)
    print(f"Archivo '{nombre}' eliminado correctamente")
  else:
    print("Archivo no encontrado")

def crear_archivo_hilo(nombre):
  print(f"{threading.current_thread().name} creando archivo {nombre}")
  touch(nombre)

def test_hilos():
  print("Iniciando prueba concurrente con hilos...")
  hilos = []

  for i in range(5):
    nombre = f"hilo_{i + 1}.txt"

    hilo = threading.Thread(
      target=crear_archivo_hilo,
      args = (nombre,),
      name = f"Hilo {i + 1}"
    )

    hilos.append(hilo)
    hilo.start()

  for h in hilos:
    h.join()
  
  print("Todos los hilos finalizaron correctamente")

def mostrar_menu():
  print("\n_________________________________")
  print("SIMULADOR FAT")
  print("________________________________")

  print("Comandos disponibles:")
  print("mkdir <nombre_directorio>")
  print("cd <nombre_directorio>")
  print("cd ..")
  print("touch <nombre_archivo>")
  print("ls")
  print("ls -l")
  print("chmod <permisos> <nombre>")
  print("rm <nombre_archivo>")
  print("test_hilos")
  print("exit")

def main():
  inicializar_fat()
  mostrar_menu()

  while True:
    ruta = obtener_ruta_actual()
    comando = input(f"\n{ruta}>")

    if comando.strip() == "":
      continue

    partes = comando.split()

    try:
      if partes[0] == "mkdir":
        if len(partes) < 2:
          print("Uso: mkdir <nombre>")
        else:
          mkdir(partes[1])
      elif partes[0] == "touch":
        if len(partes) < 2:
          print("Uso: touch <nombre>")
        else:
          touch(partes[1])
      elif partes[0] =="ls":
        if len(partes) > 1 and partes[1] == "-l":
          ls_l()
        else:
          ls()
      elif partes[0] == "cd":
        if len(partes) < 2:
          print("Uso: cd <directorio>")
        else:
          cd(partes[1])
      elif partes[0] == "rm":
        if len(partes) < 2:
          print("Uso: rm <archivo>")
        else:
          rm(partes[1])
      elif partes[0] == "chmod":
        if len(partes) < 3:
          print("Uso: chmod <permisos> <nombre>")
        else:
          chmod(partes[1], partes[2])
      elif partes[0] == "test_hilos":
        test_hilos()
      elif partes[0] == "exit":
        print("Saliendo del simulador FAT...")
        break
      else:
        print("Comando no encontrado.")
    except Exception as e:
      print("Error: ", e)

if __name__ == "__main__":
  main()