const video = document.getElementById('video');
const captureButton = document.getElementById('capture');

// Obtener acceso a la cámara web
navigator.mediaDevices.getUserMedia({ video: true })
    .then(stream => {
        video.srcObject = stream;
    })
    .catch(err => console.error("Error accessing the camera: ", err));

// Función para capturar un frame y enviarlo a la API
captureButton.addEventListener('click', () => {
    const canvas = document.createElement('canvas');
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    const context = canvas.getContext('2d');
    context.drawImage(video, 0, 0, canvas.width, canvas.height);
    
    // Convertir la imagen del canvas a Blob y enviar a la API
    canvas.toBlob(blob => {
        const formData = new FormData();
        formData.append('video', blob, 'frame.mp4');

        
        fetch(' http://192.168.45.59:5000/api/stream', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            alert(JSON.stringify(data));
        })
        .catch(err => console.error("Error sending the image: ", err));
    }, 'image/jpeg');
});
