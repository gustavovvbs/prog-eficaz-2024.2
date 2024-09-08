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

#inserir um aluno no db 
@app.route('/aluno', methods=['POST'])
def adicionar_aluno():
    data = request.get_json()
    conn = conect_db()
    if conn and conn.is_connected():
        try:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO alunos (nome, cpf, curso) VALUES (%s, %s, %s)", (data['nome'], data['cpf'], data['curso']))
            conn.commit()
            aluno_id = cursor.lastrowid
            return(jsonify({"status": "ok", "aluno_id": aluno_id}))

        except mysql.connector.Error as err:
            return jsonify({"status": "error", "message": f"Erro ao inserir aluno, {err}"})
            
        
        
        finally:
            cursor.close()
            conn.close()

    return jsonify({"status": "error", "message": "Erro ao conectar ao banco de dados"})

#listar todos os alunos
@app.route('/aluno', methods=['GET'])
def listar_alunos():
    conn = conect_db()
    if conn and conn.is_connected():
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM alunos")
            alunos = cursor.fetchall()
            if not alunos:
                return jsonify({"status": "ok", "message": "Nenhum aluno encontrado"})
            return jsonify(alunos)

        except mysql.connector.Error as err:
            return jsonify({"status": "error", "message": f"Erro ao listar alunos, {err}"})
        finally:
            cursor.close()
            conn.close()
    return jsonify({"status": "error", "message": "Erro ao conectar ao banco de dados"})

#listar um aluno pelo id
@app.route('/aluno/<int:id>', methods=['GET'])
def listar_aluno(id):
    conn = conect_db()
    if conn and conn.is_connected():
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM alunos WHERE id = %s", (id,))
            aluno = cursor.fetchone()
            if not aluno:
                return jsonify({"status": "ok", "message": "Nenhum aluno encontrado"})
            return jsonify(aluno)
        except mysql.connector.Error as err:
            return jsonify({"status": "error", "message": f"Erro ao listar aluno, {err}"})
        finally:
            cursor.close()
            conn.close()
    return jsonify({"status": "error", "message": "Erro ao conectar ao banco de dados"})

#atualizar um aluno pelo id
@app.route('/aluno/<int:id>', methods=['PUT'])
def atualizar_aluno(id):
    data = request.get_json()
    conn = conect_db()
    if conn and conn.is_connected():
        try:
            cursor = conn.cursor()
            cursor.execute("UPDATE alunos SET nome = %s, cpf = %s, curso = %s WHERE id = %s", (data['nome'], data['cpf'], data['curso'], id))
            conn.commit()
            return jsonify({"status": "ok", "message": "Aluno atualizado com sucesso"})
        except mysql.connector.Error as err:
            return jsonify({"status": "error", "message": f"Erro ao atualizar aluno, {err}"})
        finally:
            cursor.close()
            conn.close()
    return jsonify({"status": "error", "message": "Erro ao conectar ao banco de dados"})

#deletar um aluno pelo id
@app.route('/aluno/<int:id>', methods=['DELETE'])
def deletar_aluno(id):
    conn = conect_db()
    if conn and conn.is_connected():
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM alunos WHERE id = %s", (id,))
            conn.commit()
            return jsonify({"status": "ok", "message": "Aluno deletado com sucesso"})
        except mysql.connector.Error as err:
            return jsonify({"status": "error", "message": f"Erro ao deletar aluno, {err}"})
        finally:
            cursor.close()
            conn.close()
    return jsonify({"status": "error", "message": "Erro ao conectar ao banco de dados"})


 








if __name__ == '__main__':
    app.run(debug=True)
