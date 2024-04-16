import cv2

# URL del flujo de video (reemplaza con la dirección IP de tu ESP32-CAM)
video_url = 'http://tu_esp32_cam_ip:80/stream'

# Capturar el video
cap = cv2.VideoCapture(video_url)

while True:
    ret, frame = cap.read()
    if ret:
        # Mostrar el frame
        cv2.imshow('ESP32-CAM Video Stream', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Liberar el capturador y cerrar las ventanas abiertas
cap.release()
cv2.destroyAllWindows()
