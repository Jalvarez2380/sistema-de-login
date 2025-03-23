from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
import os, json, csv
from Conexion.conexion import obtener_conexion
from models import Usuario

app = Flask(__name__)
app.secret_key = 'secreto_seguro'

# Configuración de login
login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    conexion = obtener_conexion()
    if conexion:
        cursor = conexion.cursor(dictionary=True)
        cursor.execute("SELECT * FROM usuarios WHERE id_usuario = %s", (user_id,))
        usuario = cursor.fetchone()
        conexion.close()
        if usuario:
            return Usuario(usuario['id_usuario'], usuario['nombre'], usuario['mail'], usuario['password'])
    return None

# RUTA PRINCIPAL
@app.route('/')
def index():
    return render_template('index.html')

# 1) TXT
@app.route('/guardar_txt', methods=['POST'])
def guardar_txt():
    data = request.form.get('data')
    with open(os.path.join('datos', 'datos.txt'), 'w') as file:
        file.write(data)
    return redirect(url_for('index'))

@app.route('/leer_txt')
def leer_txt():
    with open(os.path.join('datos', 'datos.txt'), 'r') as file:
        contenido = file.read()
    return render_template('resultado.html', contenido=contenido)

# 2) JSON
@app.route('/guardar_json', methods=['POST'])
def guardar_json():
    data = {"data": request.form.get('data')}
    with open(os.path.join('datos', 'datos.json'), 'w') as file:
        json.dump(data, file, indent=4)
    return redirect(url_for('index'))

@app.route('/leer_json')
def leer_json():
    with open(os.path.join('datos', 'datos.json'), 'r') as file:
        data = json.load(file)
    return render_template('resultado.html', contenido=data)

# 3) CSV
@app.route('/guardar_csv', methods=['POST'])
def guardar_csv():
    nombre = request.form.get('nombre')
    edad = request.form.get('edad')
    ciudad = request.form.get('ciudad')
    with open(os.path.join('datos', 'datos.csv'), 'a', newline='') as file:
        csv.writer(file).writerow([nombre, edad, ciudad])
    return redirect(url_for('index'))

@app.route('/leer_csv')
def leer_csv():
    rows = []
    with open(os.path.join('datos', 'datos.csv'), 'r') as file:
        for row in csv.reader(file):
            rows.append(row)
    return render_template('resultado.html', contenido=rows)

# 4) MySQL (Usuarios CRUD + Login)
@app.route('/agregar_usuario', methods=['POST'])
def agregar_usuario():
    nombre = request.form.get('nombre')
    edad = request.form.get('edad')
    ciudad = request.form.get('ciudad')
    conexion = obtener_conexion()
    if conexion:
        cursor = conexion.cursor()
        cursor.execute("INSERT INTO usuarios (nombre, edad, ciudad) VALUES (%s, %s, %s)", (nombre, edad, ciudad))
        conexion.commit()
        conexion.close()
    return redirect(url_for('listar_usuarios'))

@app.route('/listar_usuarios')
def listar_usuarios():
    conexion = obtener_conexion()
    if conexion:
        cursor = conexion.cursor(dictionary=True)
        cursor.execute("SELECT id_usuario, nombre, edad, ciudad FROM usuarios")
        usuarios = cursor.fetchall()
        conexion.close()
        return render_template("usuarios.html", usuarios=usuarios)
    return "Error al conectar con MySQL"

@app.route('/usuarios_json')
def usuarios_json():
    conexion = obtener_conexion()
    if conexion:
        cursor = conexion.cursor(dictionary=True)
        cursor.execute("SELECT id_usuario, nombre, edad, ciudad FROM usuarios")
        usuarios = cursor.fetchall()
        conexion.close()
        return jsonify(usuarios)
    return jsonify({"error": "No se pudo conectar"}), 500

@app.route('/test_db')
def test_db():
    try:
        conexion = obtener_conexion()
        if conexion:
            conexion.close()
            return "✅ Conexión a MySQL exitosa"
        return "❌ No se pudo conectar"
    except Exception as e:
        return f"❌ Error: {e}", 500

# LOGIN
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        mail = request.form['mail']
        password = request.form['password']
        conexion = obtener_conexion()
        if conexion:
            cursor = conexion.cursor(dictionary=True)
            cursor.execute("SELECT * FROM usuarios WHERE mail = %s AND password = %s", (mail, password))
            usuario = cursor.fetchone()
            conexion.close()
            if usuario:
                user = Usuario(usuario['id_usuario'], usuario['nombre'], usuario['mail'], usuario['password'])
                login_user(user)
                return redirect(url_for('ruta_protegida'))
        return "Credenciales inválidas"
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        nombre = request.form['nombre']
        mail = request.form['mail']
        password = request.form['password']
        conexion = obtener_conexion()
        if conexion:
            cursor = conexion.cursor()
            cursor.execute("INSERT INTO usuarios (nombre, mail, password) VALUES (%s, %s, %s)", (nombre, mail, password))
            conexion.commit()
            conexion.close()
        return redirect(url_for('login'))
    return render_template('registro.html')

@app.route('/ruta_protegida')
@login_required
def ruta_protegida():
    return f"Hola, {current_user.nombre}. Esta es una ruta protegida."

if __name__ == '__main__':
    app.run(debug=True)