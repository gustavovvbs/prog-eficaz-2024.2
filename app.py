from flask import Flask, request, jsonify
import os
import mysql.connector
from dotenv import load_dotenv 

load_dotenv()

app = Flask(__name__)

config = {
    'host': os.getenv('DB_HOST'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'database': os.getenv('DB_NAME'),
    'port': 24111,
    'ssl_ca': 'ca.pem',
    'ssl_verify_cert': True
}

def conect_db():
    try:
        conn = mysql.connector.connect(**config)
        if conn.is_connected():
            return conn
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None

# Inserir um usuário no banco de dados
@app.route('/usuario', methods=['POST'])
def adicionar_usuario():
    data = request.get_json()
    conn = conect_db()
    if conn and conn.is_connected():
        try:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO usuarios (nome, email, cpf) VALUES (%s, %s, %s)", (data['nome'], data['email'], data['cpf']))
            conn.commit()
            usuario_id = cursor.lastrowid
            return jsonify({"status": "ok", "usuario_id": usuario_id})
        except mysql.connector.Error as err:
            return jsonify({"status": "error", "message": f"Erro ao inserir usuário, {err}"})
        finally:
            cursor.close()
            conn.close()
    return jsonify({"status": "error", "message": "Erro ao conectar ao banco de dados"}, 500)

# Inserir um livro no banco de dados
@app.route('/livro', methods=['POST'])
def adicionar_livro():
    data = request.get_json()
    conn = conect_db()
    print(conn)
    if conn and conn.is_connected():
        try:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO livros (titulo, isbn, autor) VALUES (%s, %s, %s)", (data['titulo'], data['isbn'], data['autor']))
            conn.commit()
            livro_id = cursor.lastrowid
            return jsonify({"status": "ok", "livro_id": livro_id})
        except mysql.connector.Error as err:
            return jsonify({"status": "error", "message": f"Erro ao inserir livro, {err}"})
        finally:
            cursor.close()
            conn.close()
    return jsonify({"status": "error", "message": "Erro ao conectar ao banco de dados"}, 500)

# Criar um empréstimo
@app.route('/emprestimo', methods=['POST'])
def adicionar_emprestimo():
    data = request.get_json()
    conn = conect_db()
    if conn and conn.is_connected():
        try:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO emprestimos (usuario_id, livro_id, data_emprestimo) VALUES (%s, %s, NOW())", (data['usuario_id'], data['livro_id']))
            conn.commit()
            emprestimo_id = cursor.lastrowid
            return jsonify({"status": "ok", "emprestimo_id": emprestimo_id}, 201)
        except mysql.connector.Error as err:
            return jsonify({"status": "error", "message": f"Erro ao criar empréstimo, {err}"}, 500)
        finally:
            cursor.close()
            conn.close()
    return jsonify({"status": "error", "message": "Erro ao conectar ao banco de dados"}, 500)

# Listar todos os usuários
@app.route('/usuario', methods=['GET'])
def listar_usuarios():
    conn = conect_db()
    if conn and conn.is_connected():
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM usuarios")
            usuarios = cursor.fetchall()
            if not usuarios:
                return jsonify({"status": "ok", "message": "Nenhum usuário encontrado"}, 404)
            return jsonify(usuarios)
        except mysql.connector.Error as err:
            return jsonify({"status": "error", "message": f"Erro ao listar usuários, {err}"}, 500)
        finally:
            cursor.close()
            conn.close()
    return jsonify({"status": "error", "message": "Erro ao conectar ao banco de dados"}, 500)

# Listar todos os livros
@app.route('/livro', methods=['GET'])
def listar_livros():
    conn = conect_db()
    if conn and conn.is_connected():
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM livros")
            livros = cursor.fetchall()
            if not livros:
                return jsonify({"status": "ok", "message": "Nenhum livro encontrado"}, 404)
            return jsonify(livros)
        except mysql.connector.Error as err:
            return jsonify({"status": "error", "message": f"Erro ao listar livros, {err}"}, 500)
        finally:
            cursor.close()
            conn.close()
    return jsonify({"status": "error", "message": "Erro ao conectar ao banco de dados"}, 500)

# Listar todos os empréstimos
@app.route('/emprestimo', methods=['GET'])
def listar_emprestimos():
    conn = conect_db()
    if conn and conn.is_connected():
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT e.id, u.nome AS usuario, l.titulo AS livro, e.data_emprestimo 
                FROM emprestimos e 
                JOIN usuarios u ON e.usuario_id = u.id 
                JOIN livros l ON e.livro_id = l.id
            """)
            emprestimos = cursor.fetchall()
            if not emprestimos:
                return jsonify({"status": "ok", "message": "Nenhum empréstimo encontrado"}, 404)
            return jsonify(emprestimos)
        except mysql.connector.Error as err:
            return jsonify({"status": "error", "message": f"Erro ao listar empréstimos, {err}"}, 500)
        finally:
            cursor.close()
            conn.close()
    return jsonify({"status": "error", "message": "Erro ao conectar ao banco de dados"}, 500)

# Atualizar um livro pelo ID
@app.route('/livro/<int:id>', methods=['PUT'])
def atualizar_livro(id):
    data = request.get_json()
    conn = conect_db()
    if conn and conn.is_connected():
        try:
            cursor = conn.cursor()
            cursor.execute("UPDATE livros SET titulo = %s, isbn = %s, autor = %s WHERE id = %s", (data['titulo'], data['isbn'], data['autor'], id))
            conn.commit()
            return jsonify({"status": "ok", "message": "Livro atualizado com sucesso"}, 200)
        except mysql.connector.Error as err:
            return jsonify({"status": "error", "message": f"Erro ao atualizar livro, {err}"}, 500)
        finally:
            cursor.close()
            conn.close()
    return jsonify({"status": "error", "message": "Erro ao conectar ao banco de dados"}, 500)

# Deletar um usuário pelo ID
@app.route('/usuario/<int:id>', methods=['DELETE'])
def deletar_usuario(id):
    conn = conect_db()
    if conn and conn.is_connected():
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM usuarios WHERE id = %s", (id,))
            conn.commit()
            return jsonify({"status": "ok", "message": "Usuário deletado com sucesso"}, 200)
        except mysql.connector.Error as err:
            return jsonify({"status": "error", "message": f"Erro ao deletar usuário, {err}"}, 500)
        finally:
            cursor.close()
            conn.close()
    return jsonify({"status": "error", "message": "Erro ao conectar ao banco de dados"}, 500)

# Deletar um livro pelo ID
@app.route('/livro/<int:id>', methods=['DELETE'])
def deletar_livro(id):
    conn = conect_db()
    if conn and conn.is_connected():
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM livros WHERE id = %s", (id,))
            conn.commit()
            return jsonify({"status": "ok", "message": "Livro deletado com sucesso"}, 200)
        except mysql.connector.Error as err:
            return jsonify({"status": "error", "message": f"Erro ao deletar livro, {err}"}, 500)
        finally:
            cursor.close()
            conn.close()
    return jsonify({"status": "error", "message": "Erro ao conectar ao banco de dados"}, 500)

if __name__ == '__main__':
    app.run(debug=True)
