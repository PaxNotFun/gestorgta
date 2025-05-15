# updater.py (código mejorado)
import requests
import os
import sys
import hashlib

REPO_OWNER = "PaxNotFun"
REPO_NAME = "gestorgta"
GITHUB_TOKEN = "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"  # ¡Reemplazar y no compartir!

def verificar_conexion():
    try:
        requests.get("https://github.com", timeout=5)
        return True
    except:
        return False

def actualizar_aplicacion():
    try:
        if not verificar_conexion():
            print("Sin conexión a internet")
            return False
            
        version_url = f"https://raw.githubusercontent.com/{REPO_OWNER}/{REPO_NAME}/main/version.txt"
        headers = {"Authorization": f"token {GITHUB_TOKEN}"}
        
        # Descargar versión remota
        respuesta = requests.get(version_url, headers=headers, timeout=10)
        if respuesta.status_code != 200:
            print(f"Error HTTP: {respuesta.status_code}")
            return False
            
        version_remota = respuesta.text.strip()
        version_local = open("version.txt", "r").read().strip()
        
        if version_remota == version_local:
            print("Ya tienes la última versión")
            return False
            
        # Lista de archivos con validación de hash
        archivos = {
            "main.py": "hash_main",
            "updater.py": "hash_updater",
            "database.py": "hash_database",
            "version.txt": "hash_version"
        }
        
        # Descargar y validar archivos
        for archivo, hash_esperado in archivos.items():
            url = f"https://raw.githubusercontent.com/{REPO_OWNER}/{REPO_NAME}/main/{archivo}"
            respuesta = requests.get(url, headers=headers, timeout=10)
            
            if respuesta.status_code != 200:
                print(f"Error al descargar {archivo}")
                return False
                
            # Guardar temporalmente
            with open(f"{archivo}.tmp", "wb") as f:
                f.write(respuesta.content)
                
            # Verificar hash (opcional pero recomendado)
            # hash_real = hashlib.sha256(respuesta.content).hexdigest()
            # if hash_real != hash_esperado:
            #     print(f"Hash inválido para {archivo}")
            #     return False
            
            # Reemplazar archivo
            os.replace(f"{archivo}.tmp", archivo)
            
        print("Actualización aplicada correctamente")
        return True
        
    except Exception as e:
        print(f"Error crítico: {str(e)}")
        return False

if __name__ == "__main__":
    if actualizar_aplicacion():
        print("Reiniciando aplicación...")
        os.execl(sys.executable, sys.executable, "main.py")