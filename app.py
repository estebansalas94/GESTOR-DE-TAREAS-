from flask import Flask, render_template, request, session, redirect, url_for, flash
import config
from flask_mysqldb import MySQL
from sqlite3 import Cursor
from datetime import datetime


app = Flask(__name__)

app.config['SECRET_KEY'] = config.HEX_SEC_KEY
app.config['MYSQL_HOST'] = config.MYSQL_HOST
app.config['MYSQL_USER'] = config.MYSQL_USER
app.config['MYSQL_PASSWORD'] = config.MYSQL_PASSWORD
app.config['MYSQL_DB'] = config.MYSQL_DB

mysql = MySQL(app)

@app.route('/',methods=['GET'])
def home():
    return render_template('index.html')

@app.route('/login',methods=['POST'])
def login():
    correo = request.form['correo']
    contraseña = request.form['contraseña']
    
    cur = mysql.connection.cursor()
    cur.execute('SELECT * FROM usuarios WHERE correo = %s AND contraseña = %s',(correo,contraseña))
    usuario = cur.fetchone()
    cur.close()
    
    if usuario is not None:
        session['correo'] = correo
        session['nombre'] = usuario[3]
        session['apellidos'] = usuario[4]
        
        return redirect(url_for('tareas'))
    else:
        return render_template('index.html',mensaje = "Correo o Contraseña Incorrecta")
        

@app.route('/tareas', methods = ['GET'])
def tareas():
    correo = session['correo']
    cur = mysql.connection.cursor()
    cur.execute("select * from tareas where correo = %s",[correo])
    tarea = cur.fetchall()
    
    insertar = []
    columnas = [column[0] for column in cur.description]
    for recorrer in tarea:
        insertar.append(dict(zip(columnas, recorrer)))
    cur.close()
    return render_template('tareas.html', tarea = insertar)


@app.route('/salir')
def salir():
    session.clear()
    return redirect(url_for('home'))
    
@app.route('/nueva-tarea', methods = ['POST'])
def nuevatarea():
    correo = session['correo']
    titulo = request.form['titulo']
    descripcion = request.form['descripcion']
    d = datetime.now()
    fecha = d.strftime("%Y-%m-%d %H:%M:%S")
    
    if titulo and descripcion and correo:
        cur = mysql.connection.cursor()
        sql = "insert into tareas(correo,titulo,descripcion,fecha) values(%s,%s,%s,%s)"
        datos = (correo,titulo,descripcion,fecha)
        cur.execute(sql,datos)
        mysql.connection.commit()
        success_message ="Tarea registrada exitosamente" 
        flash(success_message)
    return redirect(url_for('tareas'))
        
    
@app.route('/nuevo-usuario', methods = ['POST'])
def nuevousuario():
    contraseña = request.form['contraseña']
    correo = request.form['correo']
    nombre = request.form['nombre']
    apellidos = request.form['apellidos']
    
    
    if contraseña and nombre and correo and apellidos:
        cur = mysql.connection.cursor()
        sql = "insert into usuarios(correo,contraseña,nombreusuario,apellidosusuario) values(%s,%s,%s,%s)"
        datos = (correo,contraseña,nombre,apellidos)
        cur.execute(sql,datos)
        mysql.connection.commit()
        success_message="Usuario registrado exitosamente"
        flash(success_message)
    return redirect(url_for('tareas'))

@app.route('/eliminar-tarea', methods=['POST'])
def eliminar():
    cur = mysql.connection.cursor()
    id = request.form['id']
    cur.execute("delete from tareas where id=%s",[id])
    mysql.connection.commit()
    return redirect(url_for('tareas'))
if __name__ == '__main__':
    app.run(debug=True)
    
    