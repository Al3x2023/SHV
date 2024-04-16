const video = document.getElementById('video');
const canvas = document.getElementById('canvas');
const context = canvas.getContext('2d');
const snap = document.getElementById('snap');
const send = document.getElementById('send');

// Solicitar acceso a la cámara
navigator.mediaDevices.getUserMedia({ video: true })
    .then(stream => video.srcObject = stream)
    .catch(err => console.error("Error: ", err));

// Capturar la imagen en el canvas
snap.addEventListener("click", function() {
    context.drawImage(video, 0, 0, 640, 480);
});

// Enviar la imagen al servidor
send.addEventListener("click", function() {
    canvas.toBlob(function(blob) {
        const reader = new FileReader();
        reader.readAsArrayBuffer(blob);
        reader.onloadend = function() {
            const arrayBuffer = reader.result;
            const bytes = new Uint8Array(arrayBuffer);
            fetch('http://192.168.1.70:5000/api/imagenes', {
                method: 'POST',
                headers: {
                    'Content-Type': 'image/jpeg'
                },
                body: bytes
            })
            .then(response => response.json())
            .then(data => console.log(data))
            .catch(error => console.error('Error:', error));
        };
    }, 'image/jpeg');
});
