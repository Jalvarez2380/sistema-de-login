from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
import os, json, csv
from Conexion.conexion import obtener_conexion
from models import Usuario

app = Flask(__name__)
app.secret_key = 'secreto_seguro'

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

@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('ruta_protegida'))
    return redirect(url_for('login'))

@app.route('/guardar_txt', methods=['POST'])
def guardar_txt():
    data = request.form.get('data')
    with open(os.path.join('datos', 'datos.txt'), 'w') as file:
        file.write(data)
    return redirect(url_for('ruta_protegida'))

@app.route('/leer_txt')
def leer_txt():
    with open(os.path.join('datos', 'datos.txt'), 'r') as file:
        contenido = file.read()
    return render_template('resultado.html', contenido=contenido)

@app.route('/guardar_json', methods=['POST'])
def guardar_json():
    data = {"data": request.form.get('data')}
    with open(os.path.join('datos', 'datos.json'), 'w') as file:
        json.dump(data, file, indent=4)
    return redirect(url_for('ruta_protegida'))

@app.route('/leer_json')
def leer_json():
    with open(os.path.join('datos', 'datos.json'), 'r') as file:
        data = json.load(file)
    return render_template('resultado.html', contenido=data)

@app.route('/guardar_csv', methods=['POST'])
def guardar_csv():
    nombre = request.form.get('nombre')
    edad = request.form.get('edad')
    ciudad = request.form.get('ciudad')
    with open(os.path.join('datos', 'datos.csv'), 'a', newline='') as file:
        csv.writer(file).writerow([nombre, edad, ciudad])
    return redirect(url_for('ruta_protegida'))

@app.route('/leer_csv')
def leer_csv():
    rows = []
    with open(os.path.join('datos', 'datos.csv'), 'r') as file:
        for row in csv.reader(file):
            rows.append(row)
    return render_template('resultado.html', contenido=rows)

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
@login_required
def listar_usuarios():
    conexion = obtener_conexion()
    if conexion:
        cursor = conexion.cursor(dictionary=True)
        cursor.execute("SELECT id_usuario, nombre, edad, ciudad, mail FROM usuarios")
        usuarios = cursor.fetchall()
        conexion.close()
        return render_template("usuarios.html", usuarios=usuarios)
    return "Error al conectar con MySQL"

@app.route('/usuarios_json')
@login_required
def usuarios_json():
    conexion = obtener_conexion()
    if conexion:
        cursor = conexion.cursor(dictionary=True)
        cursor.execute("SELECT id_usuario, nombre, edad, ciudad, mail FROM usuarios")
        usuarios = cursor.fetchall()
        conexion.close()
        return jsonify(usuarios)
    return jsonify({"error": "No se pudo conectar"}), 500

@app.route('/productos')
@login_required
def listar_productos():
    conexion = obtener_conexion()
    if conexion:
        cursor = conexion.cursor(dictionary=True)
        cursor.execute("SELECT * FROM productos")
        productos = cursor.fetchall()
        conexion.close()
        return render_template("listar.html", productos=productos)
    return "Error al cargar productos"

@app.route('/crear', methods=['GET', 'POST'])
@login_required
def crear_producto():
    if request.method == 'POST':
        nombre = request.form['nombre']
        precio = request.form['precio']
        stock = request.form['stock']
        conexion = obtener_conexion()
        cursor = conexion.cursor()
        cursor.execute("INSERT INTO productos (nombre, precio, stock) VALUES (%s, %s, %s)", (nombre, precio, stock))
        conexion.commit()
        conexion.close()
        return redirect(url_for('listar_productos'))
    return render_template('crear.html')

@app.route('/editar/<int:id>', methods=['GET', 'POST'])
@login_required
def editar_producto(id):
    conexion = obtener_conexion()
    cursor = conexion.cursor(dictionary=True)
    if request.method == 'POST':
        nombre = request.form['nombre']
        precio = request.form['precio']
        stock = request.form['stock']
        cursor.execute("UPDATE productos SET nombre=%s, precio=%s, stock=%s WHERE id_producto=%s", (nombre, precio, stock, id))
        conexion.commit()
        conexion.close()
        return redirect(url_for('listar_productos'))
    cursor.execute("SELECT * FROM productos WHERE id_producto = %s", (id,))
    producto = cursor.fetchone()
    conexion.close()
    return render_template('editar.html', producto=producto)

@app.route('/eliminar/<int:id>')
@login_required
def eliminar_producto(id):
    conexion = obtener_conexion()
    cursor = conexion.cursor()
    cursor.execute("DELETE FROM productos WHERE id_producto = %s", (id,))
    conexion.commit()
    conexion.close()
    return redirect(url_for('listar_productos'))

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

@app.route('/login', methods=['GET', 'POST'])
def login():
    mensaje = None
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
            else:
                mensaje = "Credenciales inválidas"
    return render_template('login.html', mensaje=mensaje)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/registro', methods=['GET', 'POST'])
def registro():
    mensaje = None
    if request.method == 'POST':
        nombre = request.form['nombre']
        mail = request.form['mail']
        password = request.form['password']
        ciudad = request.form['ciudad'] or 'No especificado'
        conexion = obtener_conexion()
        if conexion:
            cursor = conexion.cursor()
            cursor.execute("SELECT * FROM usuarios WHERE mail = %s", (mail,))
            if cursor.fetchone():
                mensaje = "El correo ya está registrado."
            else:
                cursor.execute("INSERT INTO usuarios (nombre, mail, password, ciudad) VALUES (%s, %s, %s, %s)", (nombre, mail, password, ciudad))
                conexion.commit()
                conexion.close()
                return redirect(url_for('login'))
    return render_template('registro.html', mensaje=mensaje)

@app.route('/ruta_protegida')
@login_required
def ruta_protegida():
    return render_template('index.html', nombre=current_user.nombre)

if __name__ == '__main__':
    app.run(debug=True)

