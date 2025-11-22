<?php

function consultarEnvio($conn, $codigo) {
    $sql = "SELECT * FROM tb_envios WHERE codigo_rastreio = ?";
    $stmt = $conn->prepare($sql);
    $stmt->bind_param("s", $codigo);
    $stmt->execute();
    return $stmt->get_result()->fetch_assoc();
}


function consultarHistorico($conn, $idEnvio) {
    $sql = "SELECT h.*, s.nome AS status_nome
            FROM tb_historico_status h
            INNER JOIN tb_status s ON h.id_status = s.id_status
            WHERE h.id_envio = ?
            ORDER BY h.data_evento DESC";

    $stmt = $conn->prepare($sql);
    $stmt->bind_param("i", $idEnvio);
    $stmt->execute();
    return $stmt->get_result()->fetch_all(MYSQLI_ASSOC);
}


function consultarTodos($conn) {
    $sql = "SELECT * FROM tb_envios ORDER BY codigo_rastreio ASC";
    $res = mysqli_query($conn, $sql);
    return mysqli_fetch_all($res, MYSQLI_ASSOC);
}

function consultarStatus($conn, $codigo) {
    $sql = "SELECT id_status_atual FROM tb_envios WHERE codigo_rastreio = '$codigo'";
    $res = mysqli_query($conn, $sql);
    return mysqli_fetch_assoc($res);
}

function consultarPorData($conn, $data) {
    $sql = "SELECT * FROM tb_envios WHERE DATE(data_postagem) = '$data'";
    $res = mysqli_query($conn, $sql);
    return mysqli_fetch_all($res, MYSQLI_ASSOC);
}

function consultarPorNome($conn, $nome) {
    $sql = "SELECT * FROM tb_envios WHERE descricao LIKE '%$nome%'";
    $res = mysqli_query($conn, $sql);
    return mysqli_fetch_all($res, MYSQLI_ASSOC);
}

function verificarDuplicidade($conn, $codigo) {
    $sql = "SELECT COUNT(*) AS total FROM tb_envios WHERE codigo_rastreio = '$codigo'";
    $res = mysqli_query($conn, $sql);
    return mysqli_fetch_assoc($res)["total"];
}

function consultarEndereco($conn, $idEndereco) {
    // Buscar endereço
    $sql = "SELECT * FROM tb_enderecos WHERE id_enderecos = ?";
    $stmt = $conn->prepare($sql);
    $stmt->bind_param("i", $idEndereco);
    $stmt->execute();
    $endereco = $stmt->get_result()->fetch_assoc();

    if (!$endereco) return null;

    // Buscar cidade
    $sqlCidade = "SELECT nome AS cidade, estado 
                  FROM tb_cidades 
                  WHERE id_cidades = ?";
    $stmtCidade = $conn->prepare($sqlCidade);
    $stmtCidade->bind_param("i", $endereco["id_cidades"]);
    $stmtCidade->execute();
    $cidade = $stmtCidade->get_result()->fetch_assoc();

    // Se não existir cidade, cria valores vazios ao invés de null
    if (!$cidade) {
        $cidade = ["cidade" => "", "estado" => ""];
    }

    return array_merge($endereco, $cidade);
}
?>
