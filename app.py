# app.py

from flask import Flask, render_template, request, redirect, url_for, jsonify
import os, json, csv
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# CONFIGURACIÓN DE LA BASE DE DATOS (SQLite)
# ------------------------------------------
# Usamos una ruta absoluta para evitar problemas de "unable to open database file"
basedir = os.path.abspath(os.path.dirname(__file__))
db_path = os.path.join(basedir, 'database', 'usuarios.db')
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{db_path}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# MODELO PARA LA TABLA DE USUARIOS
# --------------------------------
class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), nullable=False)
    edad = db.Column(db.Integer, nullable=False)
    ciudad = db.Column(db.String(50), nullable=False)

    def __repr__(self):
        return f'<Usuario {self.nombre}>'

# CREAR LAS TABLAS AL INICIAR
# ---------------------------
with app.app_context():
    db.create_all()

# RUTA PRINCIPAL
# --------------
@app.route('/')
def index():
    return render_template('index.html')


# ----------------------------------
# 1) PERSISTENCIA CON ARCHIVO TXT
# ----------------------------------
@app.route('/guardar_txt', methods=['POST'])
def guardar_txt():
    # Se asume que en el formulario se envía un campo 'data'
    data = request.form.get('data')
    ruta_txt = os.path.join('datos', 'datos.txt')
    with open(ruta_txt, 'w') as file:
        file.write(data)
    return redirect(url_for('index'))

@app.route('/leer_txt')
def leer_txt():
    ruta_txt = os.path.join('datos', 'datos.txt')
    with open(ruta_txt, 'r') as file:
        contenido = file.read()
    return render_template('resultado.html', contenido=contenido)


# ----------------------------------
# 2) PERSISTENCIA CON ARCHIVO JSON
# ----------------------------------
@app.route('/guardar_json', methods=['POST'])
def guardar_json():
    # Suponemos que el formulario tiene un campo 'data'
    data = {"data": request.form.get('data')}
    ruta_json = os.path.join('datos', 'datos.json')
    with open(ruta_json, 'w') as file:
        json.dump(data, file, indent=4)
    return redirect(url_for('index'))

@app.route('/leer_json')
def leer_json():
    ruta_json = os.path.join('datos', 'datos.json')
    with open(ruta_json, 'r') as file:
        data = json.load(file)
    return render_template('resultado.html', contenido=data)


# ----------------------------------
# 3) PERSISTENCIA CON ARCHIVO CSV
# ----------------------------------
@app.route('/guardar_csv', methods=['POST'])
def guardar_csv():
    # Se asume que el formulario envía 'nombre', 'edad', 'ciudad'
    nombre = request.form.get('nombre')
    edad = request.form.get('edad')
    ciudad = request.form.get('ciudad')

    ruta_csv = os.path.join('datos', 'datos.csv')
    with open(ruta_csv, 'a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([nombre, edad, ciudad])
    return redirect(url_for('index'))

@app.route('/leer_csv')
def leer_csv():
    ruta_csv = os.path.join('datos', 'datos.csv')
    rows = []
    with open(ruta_csv, 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            rows.append(row)
    return render_template('resultado.html', contenido=rows)


# ----------------------------------
# 4) PERSISTENCIA CON SQLite
# ----------------------------------
@app.route('/agregar_usuario', methods=['POST'])
def agregar_usuario():
    nombre = request.form.get('nombre')
    edad = request.form.get('edad')
    ciudad = request.form.get('ciudad')

    usuario = Usuario(nombre=nombre, edad=int(edad), ciudad=ciudad)
    db.session.add(usuario)
    db.session.commit()
    return redirect(url_for('listar_usuarios'))

@app.route('/listar_usuarios')
def listar_usuarios():
    usuarios = Usuario.query.all()
    return render_template('usuarios.html', usuarios=usuarios)

@app.route('/usuarios_json')
def usuarios_json():
    usuarios = Usuario.query.all()
    lista = [{
        "id": u.id,
        "nombre": u.nombre,
        "edad": u.edad,
        "ciudad": u.ciudad
    } for u in usuarios]
    return jsonify(lista)

# EJECUTAR LA APLICACIÓN
# ----------------------
if __name__ == '__main__':
    app.run(debug=True)
