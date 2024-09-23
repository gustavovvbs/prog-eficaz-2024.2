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

# Inserir um usuario
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

# Criar um emprestimo
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

# Listar todos os emprestimos
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

# Atualizar um livro pelo id
@app.route('/livro/<int:id>', methods=['PUT'])
def atualizar_livro(id):
    data = request.get_json()

    # Valida se ao menos um campo foi fornecido para atualizar 
    campos_validos = {'titulo', 'isbn', 'autor'}
    campos_a_atualizar = {k: v for k, v in data.items() if k in campos_validos}

    if not campos_a_atualizar:
        return jsonify({"status": "error", "message": "Nenhum campo válido fornecido para atualização. Campos aceitos: 'titulo', 'isbn', 'autor'."}), 400

    conn = conect_db()

    if conn and conn.is_connected():
        try:
            cursor = conn.cursor()

            # Verifica se o livro existe
            cursor.execute("SELECT id FROM livros WHERE id = %s", (id,))
            livro = cursor.fetchone()

            if not livro:
                return jsonify({"status": "error", "message": "Livro não encontrado."}), 404

            #gerar uma query dinamica com base nos campos q chegaram 
            set_clause = ", ".join([f"{campo} = %s" for campo in campos_a_atualizar.keys()])
            valores = list(campos_a_atualizar.values()) + [id]

            query = f"UPDATE livros SET {set_clause} WHERE id = %s"

            cursor.execute(query, valores)
            conn.commit()

            if cursor.rowcount == 0:
                return jsonify({"status": "error", "message": "Nenhuma alteração foi feita."}), 400

            return jsonify({"status": "ok", "message": f"Livro de id {id} atualizado com sucesso."}), 200

        except mysql.connector.Error as err:
            return jsonify({"status": "error", "message": f"Erro ao atualizar livro: {err}"}), 500

        finally:
            cursor.close()
            conn.close()

    return jsonify({"status": "error", "message": "Erro ao conectar ao banco de dados."}), 500



# Deletar um usuario pelo id
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

# Deletar um livro pelo id
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

# Atualizar um empréstimo pelo ID
@app.route('/emprestimo/<int:id>', methods=['PUT'])
def atualizar_emprestimo(id):
    data = request.get_json()
   
    campos_validos = {'usuario_id', 'livro_id', 'data_emprestimo'}
    campos_a_atualizar = {k: v for k, v in data.items() if k in campos_validos}

    if not campos_a_atualizar:
        return jsonify({"status": "error", "message": "Nenhum campo válido fornecido para atualização. Campos aceitos: 'usuario_id', 'livro_id', 'data_emprestimo'."}), 400
    
    conn = conect_db()
    if conn and conn.is_connected():
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM emprestimos WHERE id = %s", (id,))
            emprestimo = cursor.fetchone()

            if not emprestimo:
                return jsonify({"status": "error", "message": "Empréstimo não encontrado."}), 404
                
            set_clause = ", ".join([f"{campo} = %s" for campo in campos_a_atualizar.keys()])
            valores = list(campos_a_atualizar.values()) + [id]

            query = f"UPDATE emprestimos SET {set_clause} WHERE id = %s"
            cursor.execute(query, valores)
            conn.commit()


            if cursor.rowcount == 0:
                return jsonify({"status": "error", "message": "Nenhuma alteração foi feita."}), 400

            return jsonify({"status": "ok", "message": f"Empréstimo de id {id} atualizado com sucesso."}), 200

        except mysql.connector.Error as err:
            return jsonify({"status": "error", "message": f"Erro ao atualizar empréstimo: {err}"}), 500

        finally:
            cursor.close()
            conn.close()

    return jsonify({"status": "error", "message": "Erro ao conectar ao banco de dados."}), 500


# Deletar um emprestimo pelo id
@app.route('/emprestimo/<int:id>', methods=['DELETE'])
def deletar_emprestimo(id):
    conn = conect_db()
    if conn and conn.is_connected():
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM emprestimos WHERE id = %s", (id,))
            conn.commit()
            return jsonify({"status": "ok", "message": "Empréstimo deletado com sucesso"}, 200)
        except mysql.connector.Error as err:
            return jsonify({"status": "error", "message": f"Erro ao deletar empréstimo, {err}"}, 500)
        finally:
            cursor.close()
            conn.close()
    return jsonify({"status": "error", "message": "Erro ao conectar ao banco de dados"}, 500)

# Atualizar um usuario pelo id
@app.route('/usuario/<int:id>', methods=['PUT'])
def atualizar_usuario(id):
    data = request.get_json()

    campos_validos = {'nome', 'email', 'cpf'}
    campos_a_atualizar = {k: v for k, v in data.items() if k in campos_validos}

    if not campos_a_atualizar:
        return jsonify({"status": "error", "message": "Nenhum campo válido fornecido para atualização. Campos aceitos: 'nome', 'email', 'cpf'."}), 400

    conn = conect_db()

    if conn and conn.is_connected():
        try:
            cursor = conn.cursor()

            # Verifica se o usuário existe
            cursor.execute("SELECT id FROM usuarios WHERE id = %s", (id,))
            usuario = cursor.fetchone()

            if not usuario:
                return jsonify({"status": "error", "message": "Usuário não encontrado."}), 404

            set_clause = ", ".join([f"{campo} = %s" for campo in campos_a_atualizar.keys()])
            valores = list(campos_a_atualizar.values()) + [id]

            query = f"UPDATE usuarios SET {set_clause} WHERE id = %s"
            cursor.execute(query, valores)
            conn.commit()

            if cursor.rowcount == 0:
                return jsonify({"status": "error", "message": "Nenhuma alteração foi feita."}), 400

            return jsonify({"status": "ok", "message": "Usuário atualizado com sucesso."}), 200

        except mysql.connector.Error as err:
            return jsonify({"status": "error", "message": f"Erro ao atualizar usuário: {err}"}), 500

        finally:
            cursor.close()
            conn.close()

    return jsonify({"status": "error", "message": "Erro ao conectar ao banco de dados."}), 500


#obter livro pelo id
@app.route('/livro/<int:id>', methods=['GET'])
def obter_livro(id):
    conn = conect_db()
    if conn and conn.is_connected():
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM livros WHERE id = %s", (id,))
            livro = cursor.fetchone()
            if not livro:
                return jsonify({"status": "error", "message": "Livro não encontrado"}, 404)
            return jsonify(livro)
        except mysql.connector.Error as err:
            return jsonify({"status": "error", "message": f"Erro ao obter livro, {err}"}, 500)
        finally:
            cursor.close()
            conn.close()
    return jsonify({"status": "error", "message": "Erro ao conectar ao banco de dados"}, 500)


#obter usuario pelo id
@app.route('/usuario/<int:id>', methods=['GET'])
def obter_usuario(id):
    conn = conect_db()
    if conn and conn.is_connected():
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM usuarios WHERE id = %s", (id,))
            usuario = cursor.fetchone()
            if not usuario:
                return jsonify({"status": "error", "message": "Usuário não encontrado"}, 404)
            return jsonify(usuario)
        except mysql.connector.Error as err:
            return jsonify({"status": "error", "message": f"Erro ao obter usuário, {err}"}, 500)
        finally:
            cursor.close()
            conn.close()
    return jsonify({"status": "error", "message": "Erro ao conectar ao banco de dados"}, 500)

#obter emprestimo pelo id
@app.route('/emprestimo/<int:id>', methods=['GET'])
def obter_emprestimo(id):
    conn = conect_db()
    if conn and conn.is_connected():
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM emprestimos WHERE id = %s", (id,))
            emprestimo = cursor.fetchone()
            if not emprestimo:
                return jsonify({"status": "error", "message": "Empréstimo não encontrado"}, 404)
            return jsonify(emprestimo)
        except mysql.connector.Error as err:
            return jsonify({"status": "error", "message": f"Erro ao obter empréstimo, {err}"}, 500)
        finally:
            cursor.close()
            conn.close()
    return jsonify({"status": "error", "message": "Erro ao conectar ao banco de dados"}, 500)

    
if __name__ == '__main__':
    app.run(debug=True)