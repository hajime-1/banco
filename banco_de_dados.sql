-- Script de criação da tabela de clientes (SQLite)
CREATE TABLE IF NOT EXISTS clientes (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  nome TEXT NOT NULL,
  cpf TEXT,
  email TEXT,
  telefone TEXT,
  agencia TEXT,
  conta TEXT,
  senha_hash TEXT,
  created_at TEXT
);
