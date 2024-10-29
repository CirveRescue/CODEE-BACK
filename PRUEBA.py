import sqlite3
from fastapi import FastAPI, BackgroundTasks, WebSocket
import cv2
import numpy as np
import asyncio
import paramiko

# Conectar a la base de datos

def activar_pluma_via_ssh(host, username, password, command="echo 1 > /path/to/pluma"):
    try:
        # Conectar a la Raspberry Pi mediante SSH
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(host, username=username, password=password)
        
        # Ejecutar el comando para activar la pluma
        stdin, stdout, stderr = ssh.exec_command(command)
        
        # Verificar si hubo errores
        error = stderr.read().decode()
        if error:
            print("Error activando la pluma:", error)
        else:
            print("Pluma activada exitosamente.")
        
        # Cerrar la conexión
        ssh.close()
    except Exception as e:
        print(f"Error en la conexión SSH: {e}")

def prueba_conexion_ssh():
    host = "172.16.35.152"       # IP de la Raspberry Pi
    username = "Prueba"           # Usuario de la Raspberry Pi
    password = "sistemas"         # Contraseña de la Raspberry Pi
    command = "echo 1 > /sys/class/gpio/gpio17/value"  # Comando para activar la pluma (ajusta si es necesario)
    
    activar_pluma_via_ssh(host, username, password, command)

# Llama a la función de prueba
if __name__ == "__main__":
    prueba_conexion_ssh()

