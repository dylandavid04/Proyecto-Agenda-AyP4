from flask import Flask, render_template, request, redirect, url_for, flash
import re
from collections import defaultdict

app = Flask(__name__)
app.secret_key = 'la_api_de_florez'

def cargar_contactos():
    contactos = []
    try:
        with open('contactos.txt', 'r', encoding='utf-8') as file:
            for line in file:
                data = line.strip().split(',')
                while len(data) < 5:
                    data.append('')  # Añadir un valor por defecto para los campos faltantes
                data[1] = data[1].split(';') if data[1] else []
                contactos.append(data)
    except FileNotFoundError:
        pass
    # Ordenar contactos por nombre
    contactos.sort(key=lambda x: x[0].lower())
    return contactos

def guardar_contactos(contactos):
    with open('contactos.txt', 'w', encoding='utf-8') as file:
        for contacto in contactos:
            contacto[1] = ';'.join(contacto[1])
            file.write(','.join(contacto) + '\n')

def validar_telefono(telefono):
    return telefono.isdigit() and len(telefono) == 10

def validar_email(email):
    return re.match(r"[^@]+@[^@]+\.[^@]+", email)

def contacto_duplicado(contactos, nombre, telefono, email):
    for contacto in contactos:
        if contacto[0] == nombre and contacto[2] == telefono and contacto[3] == email:
            return True
    return False

@app.route('/', methods=['GET', 'POST'])
def index():
    contactos = cargar_contactos()
    # Asegúrate de que cada contacto tenga una URL de foto
    for contacto in contactos:
        if len(contacto) < 5 or not contacto[4]:
            contacto.append('https://via.placeholder.com/150')
    return render_template('index.html', contactos=contactos)

@app.route('/grupos', methods=['GET', 'POST'])
def ver_grupos():
    contactos = cargar_contactos()
    grupos = defaultdict(list)
    for contacto in contactos:
        for grupo in contacto[1]:  # Iterar sobre cada grupo del contacto
            grupos[grupo].append(contacto)

    # Filtrar grupos vacíos
    grupos = {grupo: contactos for grupo, contactos in grupos.items() if contactos}

    if request.method == 'POST':
        nombre_grupo = request.form['nombre_grupo'].strip()
        if nombre_grupo:
            flash(f"Grupo '{nombre_grupo}' agregado exitosamente.", "success")
        else:
            flash("El nombre del grupo no puede estar vacío.", "error")

    return render_template('grupos.html', grupos=grupos, contactos=contactos)

@app.route('/agregar_grupo', methods=['POST'])
def agregar_grupo():
    nombre_grupo = request.form['nombre_grupo'].strip()
    if nombre_grupo:
        # Aquí podrías agregar lógica para guardar el grupo
        flash(f"Grupo '{nombre_grupo}' agregado exitosamente.", "success")
    else:
        flash("El nombre del grupo no puede estar vacío.", "error")
    return redirect(url_for('ver_grupos'))

@app.route('/agregar_contacto_a_grupo', methods=['POST'])
def agregar_contacto_a_grupo():
    nombre_contacto = request.form['nombre_contacto'].strip()
    telefono_contacto = request.form['telefono_contacto'].strip()
    email_contacto = request.form['email_contacto'].strip()
    grupo = request.form.get('grupo', '').strip()

    contactos = cargar_contactos()

    if not nombre_contacto or not telefono_contacto or not email_contacto:
        flash("Todos los campos son obligatorios para agregar un contacto.", "error")
    elif not validar_telefono(telefono_contacto):
        flash("El teléfono debe tener 10 dígitos numéricos.", "error")
    elif not validar_email(email_contacto):
        flash("El email no es válido. Debe tener el formato usuario@dominio.com.", "error")
    else:
        for contacto in contactos:
            if contacto[0] == nombre_contacto and contacto[2] == telefono_contacto and contacto[3] == email_contacto:
                if grupo not in contacto[1]:
                    contacto[1].append(grupo)
                break
        else:
            contactos.append([nombre_contacto, [grupo], telefono_contacto, email_contacto, 'https://via.placeholder.com/150'])
        
        guardar_contactos(contactos)
        flash(f"Contacto '{nombre_contacto}' agregado al grupo '{grupo}' exitosamente.", "success")

    return redirect(url_for('ver_grupos'))

@app.route('/remove_from_group/<int:index>')
def remove_from_group(index):
    contactos = cargar_contactos()
    if 0 <= index < len(contactos):
        contactos[index][1] = ''  # Eliminar el grupo del contacto
        guardar_contactos(contactos)
        flash("Contacto eliminado del grupo exitosamente.", "success")
    return redirect(url_for('ver_grupos'))

@app.route('/delete/<int:index>', methods=['POST'])
def delete_contact(index):
    contactos = cargar_contactos()
    if 0 <= index < len(contactos):
        contactos.pop(index)
        guardar_contactos(contactos)
        flash("Contacto eliminado exitosamente.", "success")
    return redirect(url_for('index'))

@app.route('/edit/<int:index>', methods=['POST'])
def edit_contact(index):
    contactos = cargar_contactos()
    if 0 <= index < len(contactos):
        nombre = request.form['nombre'].strip()
        grupo = request.form['grupo'].strip()
        telefono = request.form['telefono'].strip()
        email = request.form['email'].strip()
        foto = request.form['foto'].strip() or 'https://via.placeholder.com/150'

        if not nombre or not telefono or not email:
            flash("Todos los campos son obligatorios.", "error")
        elif not validar_telefono(telefono):
            flash("El teléfono debe tener 10 dígitos numéricos.", "error")
        elif not validar_email(email):
            flash("El email no es válido.", "error")
        else:
            contactos[index] = [nombre, grupo, telefono, email, foto]
            guardar_contactos(contactos)
            flash("Contacto editado exitosamente.", "success")

    return redirect(url_for('index'))

@app.route('/add_contact', methods=['POST'])
def add_contact():
    nombre = request.form['nombre'].strip()
    grupo = request.form['grupo'].strip()
    telefono = request.form['telefono'].strip()
    email = request.form['email'].strip()
    foto = request.form['foto'].strip() or 'https://via.placeholder.com/150'
    
    contactos = cargar_contactos()

    if contacto_duplicado(contactos, nombre, telefono, email):
        flash("El contacto ya existe.", "error")
    else:
        contactos.append([nombre, grupo, telefono, email, foto])
        guardar_contactos(contactos)
        flash("Contacto agregado exitosamente.", "success")

    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)