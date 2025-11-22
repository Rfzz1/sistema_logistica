<?php
session_start();
include "conexao.php"; include "consultas.php";

if ($_SERVER["REQUEST_METHOD"] === "POST") {
    $_SESSION["codigo_rastreio"] = $_POST["codigo_rastreio"];

    // Evita reenvio do formulário ao atualizar a página
    header("Location: index.php");
    exit;
}

$dadosEnvio = null;
$historico = null;
$endOrigem = null;
$endDestino = null;

if (!empty($_SESSION["codigo_rastreio"])) {
    $codigoRastreio = $_SESSION["codigo_rastreio"];
    $dadosEnvio = consultarEnvio($conn, $codigoRastreio);
    
    if ($dadosEnvio) {
        $historico   = consultarHistorico($conn, $dadosEnvio["id_envios"]);
		$endOrigem  = consultarEndereco($conn, $dadosEnvio["id_endereco_origem"]);
		$endDestino = consultarEndereco($conn, $dadosEnvio["id_endereco_destino"]);

    }
}

?>
<!doctype html>
<html lang="pt-br">
<head>

	<link rel="preconnect" href="https://fonts.googleapis.com">
	<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
	<link href="https://fonts.googleapis.com/css2?family=Outfit:wght@100..900&display=swap" rel="stylesheet">
	
    <meta charset="utf-8">
    <link rel="stylesheet" href="css/index.css">
    <link rel="stylesheet" href="css/reset.css">
    <link rel="stylesheet" href="css/rodape.css">	
    <link rel="icon" href="img/entrega.jpg" type="image/png">
    <title>Sistema de Rastreio</title>
</head>
<?php include "cabecalho.php";?>
<body>
	<div class="main-container">
		<h1 id="titulo">RASTREIE SEU PRODUTO</h1>

		<form method="POST" action="">
			<label class="label">Código de Rastreio do Produto</label>
			<input type="text" id="input" name="codigo_rastreio" placeholder="Código de rastreio" 
			value="<?php echo isset($_SESSION['codigo_rastreio']) ? $_SESSION['codigo_rastreio'] : ''; ?>"
            required>
			<button id="enviar" type="submit">Enviar</button>
		</form>
	
	<?php
		if ($dadosEnvio) {

			echo '<div class="resultado">';
				echo '<h3 class="subtit">Informações do Envio</h3>';
				echo '<p class="subsub"><strong>Código:</strong> ' . $dadosEnvio["codigo_rastreio"] . '</p>';
				echo '<p class="subsub"><strong>Descrição:</strong> ' . $dadosEnvio["descricao"] . '</p>';
				echo '<p class="subsub"><strong>Postado em:</strong> ' . $dadosEnvio["data_postagem"] . '</p>';
			
			echo '<div class="origem">';
				echo "<h3 class='subtit'>Origem</h3>";
				echo $endOrigem["rua"] . ", " . $endOrigem["numero"] . "<br>";
				echo $endOrigem["bairro"] . "<br>";
				echo $endOrigem["cidade"] . " — " . $endOrigem["estado"];
			echo '</div>';

			echo '<div class="origem">';
				echo "<h3 class='subtit'>Destino</h3>";
				echo ($endDestino['rua'] ?? "") . ", " . ($endDestino['numero'] ?? "") . "<br>";
				echo ($endDestino['bairro'] ?? "") . "<br>";
				echo ($endDestino['cidade'] ?? "") . " — " . ($endDestino['estado'] ?? "") . "<br><br>";
			echo '</div>';
			
			echo '<div class="origem">';
				echo '<h3 class="subtit">Histórico de Movimentações</h3>';
			echo '<div class="timeline">';

			foreach ($historico as $linha) {
				echo '<div class="evento">';
					echo '<div class="datahora">';
						echo '<span class="data">' . date("d/m/Y", strtotime($linha["data_evento"])) . '</span>';
						echo ' — ';
						echo '<span class="hora">' . date("H:i", strtotime($linha["data_evento"])) . '</span>';
					echo '</div>';

					echo '<span id="status">' . $linha["status_nome"] . '</span><br>';
					echo $linha["localizacao"] . "<br>";
					echo "<em>" . $linha["observacao"] . "</em>";
				echo '</div>';
			}

			echo '</div>';
			echo '</div>';


		} elseif (!empty($_SESSION["codigo_rastreio"])) {

			echo '<p class="info">Nenhuma informação encontrada.</p>';

		}
	?>


	</div>

    <footer>
        &copy; 2025 SENAI — Sistema de Rastreio
    </footer>
</body>
</html>
