-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Tempo de geração: 20/11/2025 às 22:18
-- Versão do servidor: 10.4.32-MariaDB
-- Versão do PHP: 8.0.30

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Banco de dados: `db_provapython`
--
CREATE DATABASE IF NOT EXISTS `db_provapython` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;
USE `db_provapython`;

-- --------------------------------------------------------

--
-- Estrutura para tabela `tb_auditoria`
--

CREATE TABLE `tb_auditoria` (
  `id_auditoria` int(11) NOT NULL,
  `id_usuario` int(11) NOT NULL,
  `acao` varchar(150) NOT NULL,
  `status_antigo` varchar(50) NOT NULL,
  `status_novo` varchar(50) NOT NULL,
  `tabela_afetada` varchar(100) NOT NULL,
  `registro_id` varchar(50) NOT NULL,
  `ip_origem` varchar(50) DEFAULT NULL,
  `data_evento` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estrutura para tabela `tb_cidades`
--

CREATE TABLE `tb_cidades` (
  `id_cidades` int(11) NOT NULL,
  `nome` varchar(100) NOT NULL,
  `estado` varchar(2) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;


-- --------------------------------------------------------

--
-- Estrutura para tabela `tb_enderecos`
--

CREATE TABLE `tb_enderecos` (
  `id_enderecos` int(11) NOT NULL,
  `rua` varchar(150) NOT NULL,
  `numero` varchar(10) NOT NULL,
  `complemento` varchar(100) DEFAULT NULL,
  `bairro` varchar(100) NOT NULL,
  `cep` varchar(15) NOT NULL,
  `id_cidade` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;


-- --------------------------------------------------------

--
-- Estrutura para tabela `tb_envios`
--

CREATE TABLE `tb_envios` (
  `id_envios` int(11) NOT NULL,
  `codigo_rastreio` varchar(50) NOT NULL,
  `descricao` varchar(200) NOT NULL,
  `id_endereco_origem` int(11) NOT NULL,
  `id_endereco_destino` int(11) NOT NULL,
  `data_postagem` datetime NOT NULL,
  `id_status_atual` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estrutura para tabela `tb_historico_status`
--

CREATE TABLE `tb_historico_status` (
  `id_historico_status` int(11) NOT NULL,
  `id_envio` int(11) NOT NULL,
  `id_status` int(11) NOT NULL,
  `localizacao` varchar(150) NOT NULL,
  `observacao` text NOT NULL,
  `data_evento` datetime DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estrutura para tabela `tb_status`
--

CREATE TABLE `tb_status` (
  `id_status` int(11) NOT NULL,
  `nome` varchar(50) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Despejando dados para a tabela `tb_status`
--

INSERT INTO `tb_status` (`id_status`, `nome`) VALUES
(7, 'Aguardando Retirada'),
(4, 'Centro da Distribuidora'),
(2, 'Coletado'),
(9, 'Devolvido'),
(3, 'Em Transito'),
(6, 'Entregue'),
(1, 'Postado'),
(8, 'Retido'),
(5, 'Saiu para entrega');

-- --------------------------------------------------------

--
-- Estrutura para tabela `tb_usuarios`
--

CREATE TABLE `tb_usuarios` (
  `id_usuarios` int(11) NOT NULL,
  `nome` varchar(100) NOT NULL,
  `username` varchar(50) NOT NULL,
  `senha_hash` varchar(255) NOT NULL,
  `tipo` enum('comum','operador','admin') NOT NULL DEFAULT 'comum',
  `criado_em` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Índices para tabelas despejadas
--

--
-- Índices de tabela `tb_auditoria`
--
ALTER TABLE `tb_auditoria`
  ADD PRIMARY KEY (`id_auditoria`),
  ADD KEY `id_usuario` (`id_usuario`);

--
-- Índices de tabela `tb_cidades`
--
ALTER TABLE `tb_cidades`
  ADD PRIMARY KEY (`id_cidades`);

--
-- Índices de tabela `tb_enderecos`
--
ALTER TABLE `tb_enderecos`
  ADD PRIMARY KEY (`id_enderecos`),
  ADD KEY `id_cidade` (`id_cidade`);

--
-- Índices de tabela `tb_envios`
--
ALTER TABLE `tb_envios`
  ADD PRIMARY KEY (`id_envios`),
  ADD UNIQUE KEY `codigo_rastreio` (`codigo_rastreio`),
  ADD KEY `id_endereco_origem` (`id_endereco_origem`),
  ADD KEY `id_endereco_destino` (`id_endereco_destino`),
  ADD KEY `tb_status` (`id_status_atual`);

--
-- Índices de tabela `tb_historico_status`
--
ALTER TABLE `tb_historico_status`
  ADD PRIMARY KEY (`id_historico_status`),
  ADD KEY `id_envio` (`id_envio`),
  ADD KEY `id_status` (`id_status`);

--
-- Índices de tabela `tb_status`
--
ALTER TABLE `tb_status`
  ADD PRIMARY KEY (`id_status`),
  ADD UNIQUE KEY `nome` (`nome`);

--
-- Índices de tabela `tb_usuarios`
--
ALTER TABLE `tb_usuarios`
  ADD PRIMARY KEY (`id_usuarios`),
  ADD UNIQUE KEY `username` (`username`);

--
-- AUTO_INCREMENT para tabelas despejadas
--

--
-- AUTO_INCREMENT de tabela `tb_auditoria`
--
ALTER TABLE `tb_auditoria`
  MODIFY `id_auditoria` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=7;

--
-- AUTO_INCREMENT de tabela `tb_cidades`
--
ALTER TABLE `tb_cidades`
  MODIFY `id_cidades` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- AUTO_INCREMENT de tabela `tb_enderecos`
--
ALTER TABLE `tb_enderecos`
  MODIFY `id_enderecos` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=21;

--
-- AUTO_INCREMENT de tabela `tb_envios`
--
ALTER TABLE `tb_envios`
  MODIFY `id_envios` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=15;

--
-- AUTO_INCREMENT de tabela `tb_historico_status`
--
ALTER TABLE `tb_historico_status`
  MODIFY `id_historico_status` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=9;

--
-- AUTO_INCREMENT de tabela `tb_status`
--
ALTER TABLE `tb_status`
  MODIFY `id_status` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=10;

--
-- AUTO_INCREMENT de tabela `tb_usuarios`
--
ALTER TABLE `tb_usuarios`
  MODIFY `id_usuarios` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;

--
-- Restrições para tabelas despejadas
--

--
-- Restrições para tabelas `tb_auditoria`
--
ALTER TABLE `tb_auditoria`
  ADD CONSTRAINT `tb_auditoria_ibfk_1` FOREIGN KEY (`id_usuario`) REFERENCES `tb_usuarios` (`id_usuarios`);

--
-- Restrições para tabelas `tb_enderecos`
--
ALTER TABLE `tb_enderecos`
  ADD CONSTRAINT `tb_enderecos_ibfk_1` FOREIGN KEY (`id_cidade`) REFERENCES `tb_cidades` (`id_cidades`);

--
-- Restrições para tabelas `tb_envios`
--
ALTER TABLE `tb_envios`
  ADD CONSTRAINT `tb_envios_ibfk_1` FOREIGN KEY (`id_endereco_origem`) REFERENCES `tb_enderecos` (`id_enderecos`) ON DELETE CASCADE ON UPDATE CASCADE,
  ADD CONSTRAINT `tb_envios_ibfk_2` FOREIGN KEY (`id_endereco_destino`) REFERENCES `tb_enderecos` (`id_enderecos`) ON DELETE CASCADE ON UPDATE CASCADE,
  ADD CONSTRAINT `tb_status` FOREIGN KEY (`id_status_atual`) REFERENCES `tb_status` (`id_status`) ON DELETE CASCADE ON UPDATE CASCADE;

--
-- Restrições para tabelas `tb_historico_status`
--
ALTER TABLE `tb_historico_status`
  ADD CONSTRAINT `tb_historico_status_ibfk_1` FOREIGN KEY (`id_envio`) REFERENCES `tb_envios` (`id_envios`),
  ADD CONSTRAINT `tb_historico_status_ibfk_2` FOREIGN KEY (`id_status`) REFERENCES `tb_status` (`id_status`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
