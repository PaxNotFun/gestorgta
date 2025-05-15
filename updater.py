import requests
import os
import sys

REPO_OWNER = "PaxNotFun"
REPO_NAME = "gestorgta"
GITHUB_TOKEN = "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"  # Reemplaza esto

def actualizar_aplicacion():
    try:
        # Obtener versión remota
        version_url = f"https://raw.githubusercontent.com/{REPO_OWNER}/{REPO_NAME}/main/version.txt"
        headers = {"Authorization": f"token {GITHUB_TOKEN}"}
        version_local = open("version.txt", "r").read().strip()
        version_remota = requests.get(version_url, headers=headers).text.strip()

        if version_remota == version_local:
            return False

        # Lista de archivos a actualizar
        archivos = ["main.py", "updater.py", "database.py", "version.txt"]

        # Descargar archivos
        for archivo in archivos:
            url = f"https://raw.githubusercontent.com/{REPO_OWNER}/{REPO_NAME}/main/{archivo}"
            respuesta = requests.get(url, headers=headers)
            with open(archivo, "wb") as f:
                f.write(respuesta.content)

        return True

    except Exception as e:
        print(f"Error: {str(e)}")
        return False

if __name__ == "__main__":
    if actualizar_aplicacion():
        print("Reiniciando...")
        os.execl(sys.executable, sys.executable, "main.py") 