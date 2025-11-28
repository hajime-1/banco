from flask import Flask, request, send_from_directory, redirect, url_for, render_template_string, escape, Response
import sqlite3
from werkzeug.security import generate_password_hash
from datetime import datetime
import os

APP_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(APP_DIR, 'banco_de_dados.db')

app = Flask(__name__, static_folder='.', static_url_path='')


def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute('''
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
    )
    ''')
    conn.commit()
    conn.close()


@app.route('/')
def index():
    return send_from_directory('.', 'main.html')


@app.route('/<path:filename>')
def static_files(filename):
    # serve any file from the project folder (html, css, js)
    return send_from_directory('.', filename)


@app.route('/api/abrir-conta', methods=['POST'])
def abrir_conta():
    # Recebe dados do formulário e grava em SQLite
    data = request.form
    nome = data.get('nome', '').strip()
    cpf = data.get('cpf', '').strip()
    email = data.get('email', '').strip()
    telefone = data.get('telefone', '').strip()
    agencia = data.get('agencia', '').strip()
    conta = data.get('conta', '').strip()
    senha = data.get('senha', '')

    if not nome or not senha:
        return "Nome e senha são obrigatórios", 400

    senha_hash = generate_password_hash(senha)
    created_at = datetime.utcnow().isoformat()

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute('''INSERT INTO clientes (nome, cpf, email, telefone, agencia, conta, senha_hash, created_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                (nome, cpf, email, telefone, agencia, conta, senha_hash, created_at))
    conn.commit()
    last_id = cur.lastrowid
    conn.close()

    # mostrar simples página de confirmação
    html = f"""
    <!doctype html>
    <html lang="pt-BR">
    <head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Conta criada</title>
    <link rel="stylesheet" href="./front.css"></head>
    <body>
      <header class="site-header"><div class="container header-inner"><div class="brand">Banco<span class="brand-accent">•</span></div></div></header>
      <main class="container" style="padding:24px 20px;max-width:700px">
        <h1>Conta criada (simulação)</h1>
        <p>Obrigado, <strong>{nome}</strong>. Seus dados foram gravados com sucesso no banco local.</p>
        <p>ID gerado: <em>{last_id}</em></p>
        <p><a href="./main.html">Voltar à página inicial</a></p>
      </main>
    </body>
    </html>
    """
    return html


@app.route('/admin')
def admin():
        # Proteção principal por HTTP Basic Auth usando ADMIN_USER / ADMIN_PASS
        expected_user = os.getenv('ADMIN_USER')
        expected_pass = os.getenv('ADMIN_PASS')

        if expected_user and expected_pass:
            auth = request.authorization
            if not auth or auth.username != expected_user or auth.password != expected_pass:
                return Response('Autenticação necessária', 401, {'WWW-Authenticate': 'Basic realm="Admin"'})
        else:
            # Fallback: proteção por token via variável de ambiente ADMIN_TOKEN
            token = request.args.get('token', '')
            expected = os.getenv('ADMIN_TOKEN')
            if not expected:
                return ("Admin não configurado. Defina as variáveis de ambiente ADMIN_USER/ADMIN_PASS ou ADMIN_TOKEN antes de usar /admin."), 403
            if token != expected:
                return ("Token inválido. Acesse /admin?token=SEU_TOKEN"), 403

        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute('SELECT id, nome, cpf, email, telefone, agencia, conta, created_at FROM clientes ORDER BY id DESC LIMIT 200')
        rows = cur.fetchall()
        conn.close()

        # montar tabela HTML segura
        rows_html = ''.join([
                '<tr>' + ''.join(f'<td>{escape(str(col))}</td>' for col in row) + '</tr>' for row in rows
        ])
        html = f"""
        <!doctype html>
        <html lang="pt-BR">
        <head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Admin - Registros</title>
        <link rel="stylesheet" href="./front.css"></head>
        <body>
            <header class="site-header"><div class="container header-inner"><div class="brand">Banco<span class="brand-accent">•</span></div></div></header>
            <main class="container" style="padding:24px 20px;max-width:1100px">
                <h1>Registros de Abertura de Conta</h1>
                <p>Mostrando até 200 registros mais recentes.</p>
                <table style="width:100%;border-collapse:collapse">
                    <thead><tr><th>ID</th><th>Nome</th><th>CPF</th><th>Email</th><th>Telefone</th><th>Agência</th><th>Conta</th><th>Criado em (UTC)</th></tr></thead>
                    <tbody>
                        {rows_html}
                    </tbody>
                </table>
                <p style="margin-top:18px"><a href="./main.html">Voltar à página inicial</a></p>
            </main>
        </body>
        </html>
        """
        return html


if __name__ == '__main__':
    init_db()
    # Use PORT do ambiente (plataformas como Render definem $PORT). Default 8000 para dev.
    port = int(os.getenv('PORT', '8000'))
    # FLASK_DEBUG=1 para debug local quando necessário
    debug = os.getenv('FLASK_DEBUG', '0') == '1'
    app.run(host='0.0.0.0', port=port, debug=debug)
