<?php
$servername = "localhost";
$username   = "root";
$password   = "";
$database   = "db_provapython";

$conn = new mysqli($servername, $username, $password, $database);

if ($conn->connect_error) {
    die("Erro na conexão: " . $conn->connect_error);
}

$conn->set_charset("utf8");
?>
