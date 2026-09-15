from flask import Flask, jsonify, request, Response
import traceback
import pandas as pd
from models.pedido import Pedido
from models.maceta import Maceta
from getPedidosFromXlsx import makePedidosFromXlsx
from pedidosMongoService import getPedidosEntregados, getListRecomOrderByProb
from mongoConnection import mongo
from flask_mysqldb import MySQL
import jwt
import datetime
from functools import wraps
from macetasSqlService import getCodigoByTituloMlibre, getFormatoByCodigoNew
from exceptions.singularMatException import SingularMatException
from exceptions.noPedidosRegistradosException import NoPedidosRegistradosException


def createAppOntivero(config_object='settings'):
    app = Flask(__name__)
    app.config.from_object(config_object)
    mongo.init_app(app)
    return app


app = createAppOntivero()
mysql = MySQL(app)
private_key = app.config.get('JWT_PRIVATE_KEY', '')
public_key = app.config.get('JWT_PUBLIC_KEY', '')


def token_verif(f):
    @wraps(f)
    def wrapped(*args, **kwargs):
        if 'access-token' in request.headers:
            token = request.headers['access-token']
        else:
            return jsonify({'message': 'No se encontró el Token'}), 403

        if not public_key:
            return jsonify({'message': 'JWT public key not configured'}), 500

        try:
            data = jwt.decode(token, public_key)
        except Exception:
            return jsonify({'message': 'Token inválido'}), 403

        if data['id'] != 'gtestino92':
            return jsonify({'message': 'Usuario no encontrado'}), 404

        return f(*args, **kwargs)

    return wrapped


@app.route('/pedidosEntregadosML', methods=['POST'])
def pedidosEntregadosML():
    try:
        pedidosXlsxFile = request.files['pedidosEntregados']
        codigosMacetasMlibre = getCodigoByTituloMlibre(mysql)
        return str(makePedidosFromXlsx(pedidosXlsxFile, codigosMacetasMlibre))
    except Exception as e:
        traceback.print_tb(e.__traceback__)
        print(e)
        return Response(status=400)


@app.route('/getPedidosEntregadosDb', methods=['GET'])
@token_verif
def getPedidosEntregadosDb():
    try:
        formatoByCodigoDict = getFormatoByCodigoNew(mysql)
        return str(getPedidosEntregados(formatoByCodigoDict))
    except Exception as e:
        traceback.print_tb(e.__traceback__)
        print(e)
        return Response(status=400)


@app.route('/getRecomendaciones', methods=['POST'])
def getCodigosRecomendacion():
    try:
        pedido = makePedidoByRequest(request)
        formatoByCodigoDict = getFormatoByCodigoNew(mysql)
        return str(getListRecomOrderByProb(pedido, formatoByCodigoDict))
    except SingularMatException as singMatE:
        return Response(status=singMatE.code)
    except NoPedidosRegistradosException as noPedidosE:
        return Response(status=noPedidosE.code)
    except Exception as e:
        traceback.print_tb(e.__traceback__)
        print(e)
        return Response(status=400)


@app.route('/getToken', methods=['GET'])
def getToken():
    if not private_key:
        return jsonify({'message': 'JWT private key not configured'}), 500

    idUser = request.args.get('id')
    token = jwt.encode(
        {'id': idUser, 'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=1)},
        private_key,
        algorithm='RS256'
    )
    return jsonify({'token': token.decode('UTF-8')})


def makePedidoByRequest(request):
    listadoMacetas = []
    for i in range(int(request.form['cantModelos'])):
        codigo = request.form['codigoNew' + str(i)]
        cantSolicitada = int(request.form['cantSolicitada' + str(i)])
        maceta = Maceta(codigo, cantSolicitada)
        listadoMacetas.append(maceta)
    return Pedido(listadoMacetas, '')


if __name__ == '__main__':
    app.run(debug=True, port=4000)
