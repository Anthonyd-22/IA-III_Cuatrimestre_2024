import json
from random import randrange

with open("base_conocimiento.json", "r") as base_conocimiento:
    base_conocimientos = json.load(base_conocimiento)

def buscar_tramite(user_in):
    for tramite in base_conocimientos["tramites"]:
        for palabras in tramite["palabras_clave"]:
            if palabras.lower() in user_in.lower():
                return tramite
    return None


while True:
    user_input = input(f"{base_conocimientos['saludo'][randrange(len(base_conocimientos['saludo']))]}: ")
    user_input = user_input.lower()
    tramite_encontrado = buscar_tramite(user_input)

    if tramite_encontrado:
        print(f"Trámite identificado: {tramite_encontrado['nombre']}")
        print("Requisitos:")
        for requisito in tramite_encontrado["requisitos"]:
            print(f"- {requisito}")
    else:
        print("No se encontró un trámite relacionado a su consulta.")
    user_input = input("¿Desea realizar otro trámite? (s/n): ")
    if user_input.lower() == "n":
        print(f"{base_conocimientos['despedida'][randrange(len(base_conocimientos['despedida']))]}")
        break
