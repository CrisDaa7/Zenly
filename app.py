from flask import Flask, render_template, request, redirect, url_for, session, flash
from database import get_db_connection  

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# ruta para el login
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        db = get_db_connection()
        cursor = db.cursor(dictionary=True)

        
        query = "SELECT * FROM usuarios WHERE email = %s AND password = %s"
        cursor.execute(query, (email, password))
        user = cursor.fetchone()

        cursor.close()
        db.close()

        if user:
            session['loggedin'] = True
            session['id'] = user['id']
            session['nombre'] = user['nombre']
            session['email'] = user['email']  
            session['password'] = user['password']  
            session['rol_id'] = user['rol_id']

            if user['rol_id'] == 1:  
                return redirect(url_for('admin_dashboard'))
            else:  
                return redirect(url_for('user_dashboard'))
        else:
            flash('Credenciales incorrectas, intenta nuevamente.')
    
    return render_template('login.html')


# Cerrar sesión
@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('nombre', None)
    session.pop('rol_id', None)
    return redirect(url_for('login'))

# ruta para los juegos
@app.route('/juegos')
def juegos():
    return render_template('juegos.html')

# ruta para los test
@app.route('/test')
def test():
    return render_template('test.html')


# ruta para el administrador
@app.route('/admi')
def admin_dashboard():
    if 'loggedin' in session and session['rol_id'] == 1:
        return render_template('admi.html', nombre=session['nombre'], email=session['email'], password=session['password'])
    else:
        return redirect(url_for('login'))

# ruta para el usuario
@app.route('/usuario')
def user_dashboard():
    if 'loggedin' in session and session['rol_id'] == 2:
        return render_template('usuario.html', nombre=session['nombre'], email=session['email'], password=session['password'])
    else:
        return redirect(url_for('login'))


# ruta para editar el perfil
@app.route('/editar_perfil', methods=['GET', 'POST'])
def editar_perfil():
    if 'loggedin' in session:
        if request.method == 'POST':
            new_email = request.form['email']
            new_password = request.form['password']

            db = get_db_connection()
            cursor = db.cursor()
            query = "UPDATE usuarios SET email = %s, password = %s WHERE id = %s"
            cursor.execute(query, (new_email, new_password, session['id']))
            db.commit()
            cursor.close()
            db.close()

            session['email'] = new_email  # Actualizar el email en la sesión
            session['password'] = new_password  # Actualizar la contraseña en la sesión
            flash('Perfil actualizado correctamente.')
            return redirect(url_for('admin_dashboard'))

        return render_template('editar_perfil.html', email=session['email'], password=session['password'])
    else:
        return redirect(url_for('login'))

# CRUD 
#ruta para agregar usuarios
@app.route('/add_user', methods=['GET', 'POST'])
def add_user():
    if 'loggedin' in session and session['rol_id'] == 1:
        if request.method == 'POST':
            nombre = request.form['nombre']
            email = request.form['email']
            password = request.form['password']
            rol_id = request.form['rol_id']  

            db = get_db_connection()
            cursor = db.cursor()
            query = "INSERT INTO usuarios (nombre, email, password, rol_id) VALUES (%s, %s, %s, %s)"
            cursor.execute(query, (nombre, email, password, rol_id))
            db.commit()
            cursor.close()
            db.close()

            flash('Usuario agregado correctamente.')
            return redirect(url_for('admin_dashboard'))

        return render_template('agregar_usuario.html')
    else:
        return redirect(url_for('login'))

@app.route('/admin_dashboard')
def user_management():
    if 'loggedin' in session and session['rol_id'] == 1:
        db = get_db_connection()
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM usuarios")
        users = cursor.fetchall()
        cursor.close()
        db.close()
        return render_template('user_management.html', users=users)
    else:
        return redirect(url_for('login'))

@app.route('/delete_user/<int:id>', methods=['GET'])
def delete_user(id):
    if 'loggedin' in session and session['rol_id'] == 1:
        db = get_db_connection()
        cursor = db.cursor()
        cursor.execute("DELETE FROM usuarios WHERE id = %s", (id,))
        db.commit()
        cursor.close()
        db.close()
        flash('Usuario eliminado correctamente.')
        return redirect(url_for('user_management'))
    else:
        return redirect(url_for('login'))

@app.route('/edit_user/<int:id>', methods=['GET', 'POST'])
def edit_user(id):
    if 'loggedin' in session and session['rol_id'] == 1:  # Asegúrate de que solo un administrador pueda acceder
        db = get_db_connection()
        cursor = db.cursor(dictionary=True)

        if request.method == 'POST':
            # Obtener los nuevos datos del formulario
            new_nombre = request.form['nombre']
            new_email = request.form['email']
            new_password = request.form['password']

            # Actualizar la base de datos
            query = "UPDATE usuarios SET nombre = %s, email = %s, password = %s WHERE id = %s"
            cursor.execute(query, (new_nombre, new_email, new_password, id))
            db.commit()

            cursor.close()
            db.close()
            flash('Usuario actualizado correctamente.')
            return redirect(url_for('user_management'))

        # Obtener los datos del usuario para mostrarlos en el formulario
        cursor.execute("SELECT * FROM usuarios WHERE id = %s", (id,))
        user = cursor.fetchone()
        cursor.close()
        db.close()
        return render_template('edit_user.html', user=user)
    else:
        return redirect(url_for('login'))



if __name__ == "__main__":
    app.run(debug=True, port=5003)