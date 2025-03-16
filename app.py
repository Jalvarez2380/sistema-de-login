from flask import Flask, render_template, request, redirect, url_for, jsonify
import os, json, csv
from Conexion.conexion import obtener_conexion

app = Flask(__name__)


# RUTA PRINCIPAL
@app.route('/')
def index():
    return render_template('index.html')


# ----------------------------------
# 1) PERSISTENCIA CON ARCHIVO TXT
# ----------------------------------
@app.route('/guardar_txt', methods=['POST'])
def guardar_txt():
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
# 4) PERSISTENCIA CON MySQL
# ----------------------------------
@app.route('/agregar_usuario', methods=['POST'])
def agregar_usuario():
    nombre = request.form.get('nombre')
    mail = request.form.get('mail')  # Corregido para coincidir con la BD

    conexion = obtener_conexion()
    if conexion:
        cursor = conexion.cursor()
        cursor.execute("INSERT INTO usuarios (nombre, mail) VALUES (%s, %s)", (nombre, mail))
        conexion.commit()
        conexion.close()
    return redirect(url_for('listar_usuarios'))


@app.route('/listar_usuarios')
def listar_usuarios():
    conexion = obtener_conexion()
    if conexion:
        cursor = conexion.cursor(dictionary=True)
        cursor.execute("SELECT id_usuario, nombre, mail FROM usuarios")
        usuarios = cursor.fetchall()
        conexion.close()
        return render_template("usuarios.html", usuarios=usuarios)
    else:
        return "Error al conectar con MySQL"


@app.route('/usuarios_json')
def usuarios_json():
    conexion = obtener_conexion()
    if conexion:
        cursor = conexion.cursor(dictionary=True)
        cursor.execute("SELECT id_usuario, nombre, mail FROM usuarios")
        usuarios = cursor.fetchall()
        conexion.close()
        return jsonify(usuarios)
    else:
        return jsonify({"error": "No se pudo conectar a la base de datos"}), 500


# TEST DE CONEXIÓN A MySQL
@app.route('/test_db')
def test_db():
    try:
        conexion = obtener_conexion()
        if conexion:
            conexion.close()
            return "✅ Conexión a MySQL exitosa"
        else:
            return "❌ No se pudo conectar a MySQL"
    except Exception as e:
        return f"❌ Error en la conexión: {e}", 500


# EJECUTAR LA APLICACIÓN
if __name__ == '__main__':
    app.run(debug=True)