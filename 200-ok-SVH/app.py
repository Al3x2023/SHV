from flask import Flask, request, jsonify
from flask_cors import CORS
import face_recognition
import os
import io
import mysql.connector
from datetime import datetime
from werkzeug.utils import secure_filename
import base64
from flask_bcrypt import Bcrypt

def convert_blob_to_base64(blob_data):
    if blob_data:
        return base64.b64encode(blob_data).decode('utf-8')  # Codifica como Base64 y decodifica a string
    return None

app = Flask(__name__)
bcrypt = Bcrypt(app)
CORS(app)

# Configuración de la base de datos
db_config = {
    'user': 'root',
    'password': '',
    'host': 'localhost',
    'database': 'acceso',
}
@app.route('/api')
def hello():
    return "Hello!"
def get_db_connection():
    print("Obteniendo conexión a la base de datos...")
    conn = mysql.connector.connect(**db_config)
    if conn.is_connected():
        print("Conectado a la base de datos.")
    return conn

UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads')
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
    print(f"Creado directorio de subida de archivos: {UPLOAD_FOLDER}")
else:
    print(f"Usando directorio de subida de archivos existente: {UPLOAD_FOLDER}")

@app.route('/api/imagenes', methods=['POST'])
def upload_image():
    print("Tipo de contenido recibido:", request.content_type)
    print("Solicitud recibida para subir imagen.")
    if 'image/jpeg' not in request.content_type:
        print("Error: Formato de imagen no soportado.")
        return jsonify({'error': 'Formato de imagen no soportado'}), 400

    image_data = io.BytesIO(request.data)
    image_data.seek(0)

    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    filename = f'uploaded_image_{timestamp}.jpg'
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    print(f"Guardando imagen recibida en: {filepath}")

    with open(filepath, 'wb') as f:
        f.write(image_data.read())
    print("Imagen guardada exitosamente.")

    image_valid, id_usuario = process_image(filepath)
    print(f"Procesamiento de imagen completado. Resultado: {'Válida' if image_valid else 'Inválida'}")

    if image_valid:
        print("Imagen válida, activando servo y registrando acceso.")
        registrar_acceso(id_usuario)
        
        # Obtiene los detalles adicionales del usuario para la respuesta.
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT nombre FROM usuarios WHERE id_usuario = %s", (id_usuario,))
        user = cursor.fetchone()
        cursor.close()
        conn.close()
        
        # Asegúrate de que se encontró el usuario antes de intentar acceder a su nombre.
        if user:
            return jsonify({'message': 'Acceso concedido.', 'activate_servo': True, 'user_id': id_usuario, 'user_name': user[0]}), 200
        else:
            print("Error: Usuario no encontrado en la base de datos.")
            return jsonify({'error': 'User not found'}), 404
    else:
        print("Acceso denegado.")
        return jsonify({'message': 'Acceso denegado.', 'activate_servo': False}), 200
    
def process_image(filepath):
    try:
        print(f"Cargando y procesando imagen: {filepath}")
        unknown_image = face_recognition.load_image_file(filepath)
        unknown_encodings = face_recognition.face_encodings(unknown_image)
        if not unknown_encodings:
            print("No se encontraron caras en la imagen.")
            return False, None

        unknown_encoding = unknown_encodings[0]
        conn = get_db_connection()
        cursor = conn.cursor(buffered=True)  # Opción buffered=True para MySQL Connector/Python
        print("Obteniendo rostros conocidos de la base de datos...")
        cursor.execute("SELECT id_usuario, rostro FROM usuarios WHERE activo = TRUE")
        rows = cursor.fetchall()  # Consumir todos los resultados de una vez

        for id_usuario, rostro in rows:
            if rostro is not None:
                print(f"Procesando rostro del usuario {id_usuario}")
                known_image = face_recognition.load_image_file(io.BytesIO(rostro))
                known_encoding = face_recognition.face_encodings(known_image)[0]
                results = face_recognition.compare_faces([known_encoding], unknown_encoding)
                if results[0]:
                    print(f"Usuario {id_usuario} reconocido.")
                    return True, id_usuario

        print("Ningún usuario reconocido en la imagen.")
        return False, None
    except Exception as e:
        print(f"Error al procesar la imagen: {e}")
        return False, None
    finally:
        if 'cursor' in locals():  # Verificar si el cursor fue creado
            cursor.close()
        if 'conn' in locals():  # Verificar si la conexión fue creada
            conn.close()


def registrar_acceso(id_usuario):
    print(f"Registrando acceso para el usuario {id_usuario}")
    conn = get_db_connection()
    cursor = conn.cursor()
    query = """INSERT INTO historial (fecha_hora, id_puerta, id_usuario)
               VALUES (%s, %s, %s)"""
    cursor.execute(query, (datetime.now(), 1, id_usuario))  # Asume id_puerta = 1 por defecto
    conn.commit()
    print("Acceso registrado en la base de datos.")
    cursor.close()
    conn.close()

@app.route('/api/usuarios', methods=['GET'])
def get_usuarios():
    conn = get_db_connection()
    cursor = conn.cursor()
    # Incluye los campos BLOB en la consulta
    cursor.execute('SELECT id_usuario, nombre, correo, activo, foto, rostro FROM usuarios')
    usuarios = cursor.fetchall()

    # Asegúrate de convertir los datos BLOB a Base64 antes de intentar serializarlos a JSON
    usuarios_lista = [{
        'id_usuario': usr[0],
        'nombre': usr[1],
        'correo': usr[2],
        'activo': usr[3],
        'foto': convert_blob_to_base64(usr[4]),  # Convierte el BLOB de foto a Base64
        'rostro': convert_blob_to_base64(usr[5])  # Convierte el BLOB de rostro a Base64
    } for usr in usuarios]

    cursor.close()
    conn.close()

    return jsonify(usuarios_lista)


@app.route('/api/usuarios', methods=['POST'])
def create_usuario():
    new_user_data = request.get_json()

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO usuarios (nombre, correo, pass, activo) VALUES (%s, %s, %s, %s)',
                   (new_user_data['nombre'], new_user_data['correo'], new_user_data['pass'], new_user_data['activo']))
    conn.commit()
    cursor.close()
    conn.close()

    return jsonify({'status': 'success'}), 201
@app.route('/api/usuarios/<int:id_usuario>', methods=['PUT'])
def update_usuario(id_usuario):
    update_data = request.get_json()

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('UPDATE usuarios SET nombre=%s, correo=%s, pass=%s, activo=%s WHERE id_usuario=%s',
                   (update_data['nombre'], update_data['correo'], update_data['pass'], update_data['activo'], id_usuario))
    conn.commit()
    cursor.close()
    conn.close()

    return jsonify({'status': 'success'}), 200

@app.route('/api/usuarios/<int:id_usuario>', methods=['DELETE'])
def delete_usuario(id_usuario):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM usuarios WHERE id_usuario=%s', (id_usuario,))
    conn.commit()
    cursor.close()
    conn.close()

    return jsonify({'status': 'success'}), 200

bcrypt = Bcrypt(app)  # app es tu instancia de Flask

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    plain_text_password = data.get('password')
    print("Received login request with email:", email)  # Depuración: registrar el email recibido

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        print("Database connection established.")  # Depuración: conexión exitosa

        # Cambia la consulta para obtener solo el hash de la contraseña, no la contraseña en texto plano
        cursor.execute("SELECT id_usuario, nombre, pass FROM usuarios WHERE correo = %s", (email,))
        user = cursor.fetchone()

        # Verifica si user es None y procede con la verificación de la contraseña
        if user and bcrypt.check_password_hash(user[2], plain_text_password):
            print("User authenticated successfully.")  # Depuración: éxito en la autenticación
            return jsonify({'isAuthenticated': True, 'user': {'id_usuario': user[0], 'nombre': user[1]}}), 200
        else:
            print("Authentication failed. User not found or password does not match.")  # Depuración: fallo en la autenticación
            return jsonify({'isAuthenticated': False}), 401
    except Exception as e:
        print(f"Error during authentication: {e}")  # Depuración: registrar errores inesperados
        return jsonify({'error': 'Internal server error'}), 500
    finally:
        if 'cursor' in locals():
            cursor.close()
            print("Database cursor closed.")  # Depuración: cursor cerrado
        if 'conn' in locals():
            conn.close()
            print("Database connection closed.")  # Depuración: conexión cerrada
   


if __name__ == '__main__':
    print("Iniciando servidor Flask...")
    app.run(debug=True, host='0.0.0.0')
