import tkinter as tk
from tkinter import filedialog
import pymysql
import pickle
import uuid
from numpy import array
import numpy as np

def conectar_bd():
    return pymysql.connect(host='localhost', user='root', password='', database='200-ok-web-security')

def insertar_datos_faciales(correo, ruta_imagen):
    conn = conectar_bd()
    cursor = conn.cursor()
    
    # Leer los bytes de la imagen
    with open(ruta_imagen, 'rb') as file:
        image_bytes = file.read()
    
    # Generar el vector de características faciales (simulado)
    face_vector = np.random.rand(3)
    face_vector_serialized = pickle.dumps(face_vector)
    
    # Buscar UsuarioID por correo
    query_usuario_id = "SELECT UsuarioID FROM Usuarios WHERE Correo = %s"
    cursor.execute(query_usuario_id, (correo,))
    result = cursor.fetchone()
    
    if result:
        usuario_id = result[0]
        datos_faciales_id = str(uuid.uuid4())
        
        query_insertar_datos = """
        INSERT INTO DatosFacialesUsuarios (
            DatosFacialesID,
            UsuarioID,
            DatosVectorCaracteristicas,
            Imagen
        ) VALUES (%s, %s, %s, %s)
        """
        cursor.execute(query_insertar_datos, (datos_faciales_id, usuario_id, face_vector_serialized, image_bytes))
        
        # Confirmar inserción
        conn.commit()
        mensaje = "Datos faciales insertados correctamente."
    else:
        mensaje = "No se encontró un usuario con ese correo."
    
    # Cerrar conexión
    cursor.close()
    conn.close()
    return mensaje

def seleccionar_imagen():
    ruta_imagen = filedialog.askopenfilename()
    entrada_imagen.delete(0, tk.END)
    entrada_imagen.insert(0, ruta_imagen)

def registrar_datos():
    correo = entrada_correo.get()
    ruta_imagen = entrada_imagen.get()
    mensaje = insertar_datos_faciales(correo, ruta_imagen)
    resultado_operacion.config(text=mensaje)

# Crear la ventana de la interfaz
ventana = tk.Tk()
ventana.title("Registro de Datos Faciales")

# Correo electrónico
etiqueta_correo = tk.Label(ventana, text="Correo electrónico:")
etiqueta_correo.pack()
entrada_correo = tk.Entry(ventana)
entrada_correo.pack()

# Selección de imagen
etiqueta_imagen = tk.Label(ventana, text="Ruta de la imagen:")
etiqueta_imagen.pack()
entrada_imagen = tk.Entry(ventana)
entrada_imagen.pack()
boton_seleccionar_imagen = tk.Button(ventana, text="Seleccionar imagen", command=seleccionar_imagen)
boton_seleccionar_imagen.pack()

# Botón para registrar los datos
boton_registrar = tk.Button(ventana, text="Registrar Datos", command=registrar_datos)
boton_registrar.pack()

# Etiqueta para mostrar el resultado de la operación
resultado_operacion = tk.Label(ventana, text="")
resultado_operacion.pack()

# Mostrar la ventana
ventana.mainloop()
