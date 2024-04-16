register_user.php<?php
use Ramsey\Uuid\Uuid;

$usuarioID = Uuid::uuid4()->toString();

$DATABASE_HOST = 'localhost';
$DATABASE_USER = 'root';
$DATABASE_PASSWORD = '';
$DATABASE_DB = '200-ok-web-security';

// Conexión a la base de datos
$conn = new mysqli($DATABASE_HOST, $DATABASE_USER, $DATABASE_PASSWORD, $DATABASE_DB);
if ($conn->connect_error) {
    die("Conexión fallida: " . $conn->connect_error);
}

// Recogemos los datos del formulario
$correo = $_POST['correo'];
// Hasheando la contraseña
$contrasenaHash = password_hash($contrasena, PASSWORD_DEFAULT);
$nombre = $_POST['nombre'];
$apellido = $_POST['apellido'];
$usuarioID = UUID::v4(); // Necesitarás una función o método para generar UUIDs.

// Preparar y vincular
$stmt = $conn->prepare("INSERT INTO Usuarios (UsuarioID, Correo, Contrasena, Nombre, Apellido, Estado, Rol) VALUES (?, ?, ?, ?, ?, 'Activa', 'usuario')");
$stmt->bind_param("sssss", $usuarioID, $correo, $contrasena, $nombre, $apellido);

// Ejecutar y verificar
if ($stmt->execute()) {
    echo "Nuevo usuario registrado exitosamente.";
} else {
    echo "Error: " . $stmt->error;
}

$stmt->close();
$conn->close();
?>
