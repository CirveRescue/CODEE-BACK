import sqlite3
import pandas as pd
from datetime import datetime

# Ruta del archivo CSV y base de datos
csv_file_path = 'C:/Formulario.csv'
db_file_path = 'C:/xampp/htdocs/codee/database/CODE.db'

# Cargar el archivo CSV
data = pd.read_csv(csv_file_path)

# Conectar a la base de datos SQLite
conn = sqlite3.connect(db_file_path)
cursor = conn.cursor()

# Obtener la fecha y hora actual para 'created_at' y 'updated_at'
current_timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

# Preparar la inserción de datos en la tabla 'informacion_adicional'
for index, row in data.iterrows():
    # Buscar el ID del usuario relacionado por su correo
    correo_usuario = row['Dirección de correo electrónico']  # Correo del usuario en el CSV
    cursor.execute("SELECT ID_Usuario FROM usuario WHERE Correo = ?", (correo_usuario,))
    usuario = cursor.fetchone()

    if usuario:
        usuario_id = usuario[0]  # Extraer el ID del usuario
        
        # Buscar el ID del vehículo relacionado, si existe una placa
        vehiculo_id = None
        if pd.notna(row['Placa']):
            placa = row['Placa'].replace("-", "").replace(" ", "")
            cursor.execute("SELECT ID_Vehiculo FROM vehiculo WHERE Placa = ?", (placa,))
            vehiculo = cursor.fetchone()
            vehiculo_id = vehiculo[0] if vehiculo else None

        # Extraer la información adicional
        numero_nomina = row.get('Número de nomina', None)
        numero_control = row.get('Número de control', None)
        correo_alternativo = row.get('Correo Electronico', None)
        declara_informacion_veridica = row.get('Declaro que la información proporcionada es verdadera y completa', False)
        
        # Manejar "cuentas con candado" y asignar "No aplica" (booleano 0) si está vacío
        cuentas_con_candado = row.get('cuentas con candado:', 'No aplica')
        if pd.isna(cuentas_con_candado) or cuentas_con_candado.strip() == '':
            cuentas_con_candado = 'NO APLICA'  # Si está vacío, se inserta como 0 (No aplica)

        nombre_local = row.get('Nombre del local', None)
        foto_ine_frente = row.get('Fotografiá de INE (Frente)', None)
        foto_ine_trasera = row.get('Fotografiá de INE (Trasera)', None)
        foto_tarjeta_circulacion = row.get('Fotografiá de Tarjeta de Circulación', None)

        # Insertar la información adicional
        try:
            cursor.execute("""
                INSERT INTO informacion_adicional (
                    usuario_id, vehiculo_id, numero_nomina, numero_control,
                    correo_electronico_alternativo, declara_informacion_veridica, cuentas_con_candado,
                    nombre_local, foto_ine_frente, foto_ine_trasera, foto_tarjeta_circulacion,
                    created_at, updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                usuario_id, vehiculo_id, numero_nomina, numero_control,
                correo_alternativo, declara_informacion_veridica, cuentas_con_candado,
                nombre_local, foto_ine_frente, foto_ine_trasera, foto_tarjeta_circulacion,
                current_timestamp, current_timestamp
            ))
            conn.commit()
            print(f"Información adicional insertada para el usuario {usuario_id}.")
        except sqlite3.IntegrityError as e:
            print(f"Error al insertar la información adicional: {e}")
    else:
        print(f"Usuario con correo {correo_usuario} no encontrado. No se puede insertar información adicional.")

conn.close()
