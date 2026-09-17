from database.db import crear_base_datos
from core.comandos import procesar_comando

print("Sistema financiero iniciado")
crear_base_datos()

while True:
    comando = input(">> ").strip()

    if comando.lower() == "salir":
        break

    respuesta = procesar_comando(comando)
    print(respuesta)
