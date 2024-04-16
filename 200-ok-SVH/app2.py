from flask import Flask, request, jsonify, send_file
import face_recognition
import io
import pymysql
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Configuración de la base de datos
DATABASE_HOST = 'localhost'
DATABASE_USER = 'root'
DATABASE_PASSWORD = ''
DATABASE_DB = '200-ok-web-security'

def conectar_bd():
    return pymysql.connect(host=DATABASE_HOST, user=DATABASE_USER, password=DATABASE_PASSWORD, database=DATABASE_DB)

@app.route('/api/get-imagen', methods=['GET'])
def get_image():
    conn = conectar_bd()
    cursor = conn.cursor()
    cursor.execute("SELECT DatosVectorCaracteristicas FROM datosfacialesusuarios WHERE UsuarioID = %s", ('e80371b1-ce65-4e75-bc15-89c4da8a60bf',))
    result = cursor.fetchone()
    conn.close()
    
    if result and result[0]:
        image_data = io.BytesIO(result[0])
        image_data.seek(0)
        return send_file(image_data, mimetype='image/jpeg', as_attachment=True, attachment_filename='imagen_usuario.jpg')
    else:
        return jsonify({'error': 'No se encontró la imagen en la base de datos.'}), 404

def get_known_image():
    conn = conectar_bd()
    cursor = conn.cursor()
    cursor.execute("SELECT `DatosVectorCaracteristicas` FROM `datosfacialesusuarios` WHERE `UsuarioID` = %s", ('e80371b1-ce65-4e75-bc15-89c4da8a60bf',))
    record = cursor.fetchone()
    conn.close()

    if record and record[0]:
        known_image_data = io.BytesIO(record[0])
        known_image_data.seek(0)
        try:
            known_image = face_recognition.load_image_file(known_image_data)
            known_encodings = face_recognition.face_encodings(known_image)
            if known_encodings:
                return known_encodings[0]  # Retorna el primer vector de características encontrado
            else:
                print("No se encontraron codificaciones faciales en la imagen conocida.")
                return None
        except Exception as e:
            print(f"Error al cargar la imagen conocida: {e}")
            return None
    else:
        print("No se encontraron registros de imagen conocida en la base de datos.")
        return None

@app.route('/api/imagenes', methods=['POST'])
def upload_image():
    known_encoding = get_known_image()
    if known_encoding is None:
        return jsonify({'error': 'No se pudo cargar la imagen conocida desde la base de datos o no se encontraron codificaciones faciales.'}), 500

    if 'image/jpeg' not in request.content_type:
        return jsonify({'error': 'Formato de imagen no soportado'}), 400
    
    image_data = io.BytesIO(request.data)
    image_data.seek(0)

    try:
        unknown_image = face_recognition.load_image_file(image_data)
        unknown_encodings = face_recognition.face_encodings(unknown_image)
        
        if unknown_encodings:
            unknown_encoding = unknown_encodings[0]
            results = face_recognition.compare_faces([known_encoding], unknown_encoding)
            return jsonify({'message': 'La persona conocida está en la imagen de prueba.', 'activate_servo': results[0]}), 200
        else:
            return jsonify({'message': 'La persona conocida NO está en la imagen de prueba.', 'activate_servo': False}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
