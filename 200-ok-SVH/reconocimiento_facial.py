import face_recognition

print("Cargando imagen conocida...")
known_image = face_recognition.load_image_file("persona_conocida.jpg")
known_encoding = face_recognition.face_encodings(known_image)[0]

print("Cargando imagen de prueba...")
unknown_image = face_recognition.load_image_file("imagen_de_prueba.jpg")
unknown_encoding = face_recognition.face_encodings(unknown_image)[0]

print("Comparando caras...")
results = face_recognition.compare_faces([known_encoding], unknown_encoding)

if results[0]:
    print("La persona conocida está en la imagen de prueba.")
else:
    print("La persona conocida NO está en la imagen de prueba.")
