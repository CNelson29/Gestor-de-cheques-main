from urllib.parse import urlparse
from flask import Flask, make_response, render_template, request, redirect, session, url_for, flash ,send_file
from config import Config
from models import init_db, query_db
from models import User,get_user
from io import BytesIO
from MySQLdb import IntegrityError
import pprint
#-------------------------------------------------------------------------------------------------------v--------------------------------------------------------------------
app = Flask(__name__)
app.config.from_object(Config)
init_db(app)
app.config['SECRET_KEY'] = '7110c8ae51a4b5af97be6534caef90e4bb9bdcb3380af008f90b23a5d1616bf319bc298105da20fe'




proveedores = query_db('SELECT id_proveedor, nombre FROM proveedores')
pprint.pprint(proveedores)