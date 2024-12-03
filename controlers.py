from urllib.parse import urlparse
from flask import Flask, make_response, render_template, request, redirect, session, url_for, flash ,send_file
from config import Config
from models import User, mysql, init_db, query_db, execute_db
from models import User,get_user
from io import BytesIO
from MySQLdb import IntegrityError
import random
#-------------------------------------------------------------------------------------------------------v--------------------------------------------------------------------
app = Flask(__name__)
app.config.from_object(Config)
init_db(app)
app.config['SECRET_KEY'] = '7110c8ae51a4b5af97be6534caef90e4bb9bdcb3380af008f90b23a5d1616bf319bc298105da20fe'

#-------------------------------------------------------------------------------------------------------------------------------------------------- parte nueva
@app.route('/home')
def home():
    return render_template('layout.html')

@app.route('/home/conceptos')
def concepto():
    conceptos = query_db('SELECT * FROM conceptos')
    return render_template('conceptos/index.html',conceptos=conceptos)

@app.route('/home/conceptos/Agregar', methods=['POST'])
def concepto_agregar():
    descripcion = request.form['descripcion']
    estado = request.form.get('estado', '0')  # Valor predeterminado '0' si no está marcado

    execute_db('''
        INSERT INTO conceptos (descripcion, estado)
        VALUES (%s, %s)
    ''', (descripcion, estado))
    flash('Concepto agregado exitosamente')
    return redirect(url_for('concepto'))


@app.route('/home/conceptos/eliminar/<int:id>')
def eliminar_concepto(id):
    execute_db('DELETE FROM conceptos WHERE id_concepto = %s', (id,))
    flash('Concepto eliminado exitosamente')
    return redirect(url_for('concepto'))

@app.route('/home/proveedores')
def proveedor():
# Consulta para obtener las ventas y detalles de los productos
    proveedor = query_db('''
        SELECT v.id, p.nombre AS producto, v.cantidad, v.fecha 
        FROM ventas v
        JOIN productos p ON v.producto_id = p.id
    ''')
    
    # Consulta para obtener todos los productos disponibles
    proveedores = query_db('SELECT * FROM proveedores')

    return render_template('proveedores/index.html', proveedores=proveedores)

@app.route('/home/proveedores/agregar', methods=['GET', 'POST'])
def agregar_proveedor():
    if request.method == 'POST':
        # Recuperar los datos del formulario
        nombre = request.form.get('nombre')
        tipo_persona = request.form.get('tipo_persona')
        identificacion = request.form.get('identificacion')
        balance = request.form.get('balance', 0.0)  # Balance opcional, valor predeterminado 0.0
        cuenta_contable = request.form.get('cuenta_contable', None)  # Campo opcional
        estado = request.form.get('estado', '1')  # Estado activo por defecto ('1' para activo, '0' para inactivo)

        # Validación simple
        if not nombre or not tipo_persona or not identificacion:
            flash("Por favor, completa todos los campos obligatorios.")
            return redirect(url_for('proveedor'))  # Redirige si falta algún campo obligatorio

        # Insertar el proveedor en la base de datos
        execute_db('''
            INSERT INTO proveedores (nombre, tipo_persona, identificacion, balance, cuenta_contable, estado)
            VALUES (%s, %s, %s, %s, %s, %s)
        ''', (nombre, tipo_persona, identificacion, balance, cuenta_contable, estado))

        flash('Proveedor agregado exitosamente')
        return redirect(url_for('proveedor'))

    # GET request para mostrar el formulario de agregar
    return render_template('proveedores/index.html')


@app.route('/home/proveedores/eliminar/<int:id>')
def eliminar_proveedor(id):
    execute_db('DELETE FROM proveedores WHERE id_proveedor = %s', (id,))
    flash('proveedor eliminado exitosamente')
    return redirect(url_for('proveedor'))

#-------------------------------------------------------------------------------------------------------------------------------------------------------------------




@app.route('/home/solicitudes_de_cheques')
def cheques():
    per_page = 10  # Elementos por página
    page = int(request.args.get('page', 1))
    offset = (page - 1) * per_page

    # Consultar la cantidad total de registros
    result = query_db('SELECT COUNT(*) AS total FROM solicitudes_cheques')
    total_cheques = result[0]['total'] if result else 0

    total_pages = (total_cheques + per_page - 1) // per_page

    # Consultar los cheques para la página actual
    cheques = query_db("SELECT * FROM solicitudes_cheques WHERE estado = 'Pendiente' LIMIT %s OFFSET %s", (per_page, offset))

    # Obtener todos los proveedores para mostrar en el formulario
    proveedores = query_db("SELECT * FROM proveedores ")
    
    return render_template('cheques/index.html', cheques=cheques, page=page, total_pages=total_pages,proveedores=proveedores)

@app.route('/home/cheques')
def Aprovados_cheques():
    per_page = 10  # Elementos por página
    page = int(request.args.get('page', 1))
    offset = (page - 1) * per_page

    # Consultar la cantidad total de registros
    result = query_db('SELECT COUNT(*) AS total FROM cheques_generados')
    total_cheques = result[0]['total'] if result else 0

    total_pages = (total_cheques + per_page - 1) // per_page

    # Consultar los cheques para la página actual
    cheques = query_db("SELECT * FROM cheques_generados LIMIT %s OFFSET %s", (per_page, offset))

    # Obtener todos los proveedores para mostrar en el formulario
    proveedores = query_db("SELECT * FROM proveedores ")
    
    return render_template('cheques/index1.html', cheques=cheques, page=page, total_pages=total_pages,proveedores=proveedores)

@app.route('/home/cheques/agregar', methods=['GET', 'POST'])
def agregar_cheque():
    if request.method == 'POST':
        # Obtener datos del formulario
        numero = request.form.get('numero_solicitud')
        proveedor_id = request.form.get('proveedor_id')
        monto = request.form.get('monto')
        fecha = request.form.get('fecha_registro')
        estado = request.form.get('estado', 'Pendiente')
        cuenta_banco = request.form.get('cuenta_contable_banco', None)

        # Consultar la cuenta contable del proveedor desde la base de datos
        proveedor = query_db('SELECT cuenta_contable FROM proveedores WHERE id_proveedor = %s', (proveedor_id,), one=True)
        if not proveedor:
            flash('El proveedor seleccionado no existe.')
            return redirect(url_for('cheques'))

        cuenta_proveedor = proveedor['cuenta_contable']

        # Insertar los datos en la tabla
        try:
            execute_db('''
                INSERT INTO solicitudes_cheques (numero_solicitud, proveedor_id, monto, fecha_registro, estado, cuenta_contable_proveedor, cuenta_contable_banco)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            ''', (numero, proveedor_id, monto, fecha, estado, cuenta_proveedor, cuenta_banco))
        except Exception as e:
            print(f"Error al insertar datos: {str(e)}")
            raise

    # Obtener todos los proveedores para mostrar en el formulario
    proveedores = query_db('SELECT * FROM proveedores')

    return redirect(url_for('cheques'))



@app.route('/home/solicitud/eliminar/<int:id>', methods=['POST'])
def eliminar_solicitud(id):
    execute_db('DELETE FROM solicitudes_cheques WHERE id = %s', (id,))
    flash('Solicitud de cheque eliminada exitosamente')
    return redirect(url_for('cheques'))


@app.route('/home/cheques/eliminar/<int:id>', methods=['POST'])
def eliminar_cheque(id):
    execute_db('DELETE FROM cheques_generados WHERE id = %s', (id,))
    flash('Solicitud de cheque eliminada exitosamente')
    return redirect(url_for('Aprovados_cheques'))

@app.route('/home/solicitud/edicion/<int:id>', methods=['GET', 'POST'])
def editar_solicitud(id):
    if request.method == 'POST':
        # Obtener los datos enviados desde el formulario
        numero = request.form.get('numero_solicitud')
        proveedor_id = request.form.get('proveedor_id')
        monto = request.form.get('monto')
        fecha = request.form.get('fecha_registro')
        estado = request.form.get('estado')
        cuenta_banco = request.form.get('cuenta_contable_banco')

        # Validar datos obligatorios
        if not (numero and proveedor_id and monto and fecha):
            flash('Todos los campos obligatorios deben ser completados.')
            return redirect(url_for('editar_cheque', id=id))

        # Actualizar los datos del cheque en la base de datos
        try:
            execute_db('''
                UPDATE solicitudes_cheques
                SET numero_solicitud = %s, proveedor_id = %s, monto = %s, fecha_registro = %s, estado = %s, cuenta_contable_banco = %s
                WHERE id = %s
            ''', (numero, proveedor_id, monto, fecha, estado, cuenta_banco, id))
            flash('Solicitud de cheque actualizada exitosamente.')
        except Exception as e:
            flash(f'Error al actualizar el cheque: {str(e)}')
            return redirect(url_for('editar_cheque', id=id))

        return redirect(url_for('cheques'))

    # Método GET: Cargar los datos actuales del cheque para el formulario
    cheque = query_db('SELECT * FROM solicitudes_cheques WHERE id = %s', (id,), one=True)
    if not cheque:
        flash('El cheque no existe.')
        return redirect(url_for('cheques'))

    # Obtener todos los proveedores para mostrar en el formulario
    proveedores = query_db('SELECT * FROM proveedores')

    return render_template('cheques/editar.html', cheque=cheque, proveedores=proveedores)

@app.route('/home/cheques/edicion/<int:id>', methods=['GET', 'POST'])
def editar_cheque(id):
    if request.method == 'POST':
        # Obtener los datos enviados desde el formulario
        numero_cheque = request.form.get('numero_cheque')  # Cambiado de numero_solicitud a numero_cheque
        proveedor_id = request.form.get('proveedor_id')
        monto = request.form.get('monto')
        fecha = request.form.get('fecha_registro')
        cuenta_proveedor = request.form.get('cuenta_contable_proveedor')  # Campo nuevo para cuenta_contable_proveedor
        cuenta_banco = request.form.get('cuenta_contable_banco')

        # Validar datos obligatorios
        if not (numero_cheque and proveedor_id and monto and fecha):
            flash('Todos los campos obligatorios deben ser completados.')
            return redirect(url_for('editar_cheque', id=id))

        # Actualizar los datos del cheque en la base de datos
        try:
            execute_db(''' 
                UPDATE cheques_generados
                SET numero_cheque = %s, proveedor_id = %s, monto = %s, fecha_registro = %s, cuenta_contable_proveedor = %s, cuenta_contable_banco = %s
                WHERE id = %s
            ''', (numero_cheque, proveedor_id, monto, fecha, cuenta_proveedor, cuenta_banco, id))
            flash('Cheque actualizado exitosamente.')
        except Exception as e:
            flash(f'Error al actualizar el cheque: {str(e)}')
            return redirect(url_for('editar_cheque', id=id))

        return redirect(url_for('Aprovados_cheques'))  # Redirige a la lista de cheques aprobados (ajusta según tu ruta)

    # Método GET: Cargar los datos actuales del cheque para el formulario
    cheque = query_db('SELECT * FROM cheques_generados WHERE id = %s', (id,), one=True)
    if not cheque:
        flash('El cheque no existe.')
        return redirect(url_for('Aprovados_cheques'))  # Redirige si no se encuentra el cheque

    # Obtener todos los proveedores para mostrar en el formulario
    proveedores = query_db('SELECT * FROM proveedores')

    return render_template('cheques/editar1.html', cheque=cheque, proveedores=proveedores)


#--------------------------------------------------------------------------------------------------------------------Pruebas-----------------------
def generate_random_number():
    """Genera un número aleatorio de 6 dígitos como string."""
    return str(random.randint(100000, 999999))

@app.route('/home/cheques/mover/<int:cheque_id>', methods=['POST'])
def mover_cheque_especifico(cheque_id):
    try:
        # Verificar si el cheque existe y tiene el estado correcto
        cheque = query_db(
            "SELECT * FROM solicitudes_cheques WHERE id = %s AND estado = 'Cheque Generado'",
            (cheque_id,),
            one=True
        )
        
        if not cheque:
            flash('El cheque no existe o ya fue movido.')
            return redirect(url_for('Aprovados_cheques'))

        # Generar un nuevo número de cheque
        nuevo_numero_cheque = generate_random_number()

        # Iniciar una transacción manualmente
        execute_db('START TRANSACTION')

        # Insertar el cheque en la tabla `cheques_generados`
        execute_db('''
            INSERT INTO cheques_generados 
            (numero_cheque, proveedor_id, monto, fecha_registro, cuenta_contable_proveedor, cuenta_contable_banco)
            VALUES (%s, %s, %s, %s, %s, %s)
        ''', (
            nuevo_numero_cheque,
            cheque['proveedor_id'],
            cheque['monto'],
            cheque['fecha_registro'],
            cheque['cuenta_contable_proveedor'],
            cheque['cuenta_contable_banco']
        ))

        # Actualizar el estado del cheque original
        execute_db(
            "UPDATE solicitudes_cheques SET estado = 'Cheque Generado' WHERE id = %s",
            (cheque_id,)
        )

        # Confirmar la transacción
        execute_db('COMMIT')
        flash(f'Cheque {cheque_id} movido exitosamente.')
    except Exception as e:
        # Si ocurre un error, revertir la transacción
        execute_db('ROLLBACK')
        flash(f'Error al mover el cheque: {str(e)}')

    return redirect(url_for('Aprovados_cheques'))


def generate_random_number():
    """Genera un número aleatorio de 6 dígitos como string."""
    import random
    return str(random.randint(100000, 999999))

from flask import request

@app.route('/mover_cheques', methods=['GET', 'POST'])
def mover_cheques():
    if request.method == 'POST':  # Verificar si la solicitud es POST
        try:
            # Seleccionar los cheques que están en estado 'Cheque Generado'
            cheques_generados = query_db(
                "SELECT * FROM solicitudes_cheques WHERE estado = 'Cheque Generado'"
            )

            for cheque in cheques_generados:
                # Verificar si ya existe en la tabla cheques_generados
                existe = query_db(
                    "SELECT COUNT(*) AS total FROM cheques_generados WHERE numero_cheque = %s AND proveedor_id = %s",
                    (cheque['numero_solicitud'], cheque['proveedor_id']),
                    one=True
                )

                if existe and existe['total'] > 0:
                    # Si ya existe, omitir este cheque
                    continue

                # Generar un nuevo número de cheque
                nuevo_numero_cheque = generate_random_number()

                # Insertar en la tabla cheques_generados
                execute_db('''
                    INSERT INTO cheques_generados 
                    (numero_cheque, proveedor_id, monto, fecha_registro, cuenta_contable_proveedor, cuenta_contable_banco)
                    VALUES (%s, %s, %s, %s, %s, %s)
                ''', (nuevo_numero_cheque, cheque['proveedor_id'], cheque['monto'], cheque['fecha_registro'], cheque['cuenta_contable_proveedor'], cheque['cuenta_contable_banco']))

                # Actualizar el estado del cheque en solicitudes_cheques
                execute_db(
                    "UPDATE solicitudes_cheques SET estado = 'Movido' WHERE id = %s",
                    (cheque['id'],)
                )

            flash('Cheques generados movidos correctamente.', 'success')
        except Exception as e:
            flash(f'Error al mover cheques: {str(e)}', 'danger')
        return redirect(url_for('cheques'))

    # Si es GET, redirigir o devolver un mensaje
    flash('Esta operación solo se puede realizar mediante POST.', 'info')
    return redirect(url_for('cheques'))




#---------------------------------------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':
    app.run(debug=True)