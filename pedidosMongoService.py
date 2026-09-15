from mongoConnection import mongo
from pymongo import MongoClient
from models.pedido import Pedido
from models.maceta import Maceta
import pandas as pd
import numpy as np
import re
#from matplotlib import pyplot as plt
from ml.logRegGradDesc import getProbCompraEstimation
from exceptions.noPedidosRegistradosException import NoPedidosRegistradosException
from datetime import datetime

def getListRecomOrderByProb(pedidoSolicitado, formatoByCodigoDict):
    ontiveroDb = mongo.db
    pedidosCollection = ontiveroDb['pedidos']
    
    codigosConPedidosRegistrados = getCodigosConPedidos(pedidoSolicitado.listadoMacetas,pedidosCollection)
    
    if(len(codigosConPedidosRegistrados) == 0):
        raise NoPedidosRegistradosException(406)
    query = {"$or": []}
    for codNew in codigosConPedidosRegistrados:
        query["$or"].append({codNew : { "$exists": True }})
    listPedidos = list(pedidosCollection.find(query))

    ## obtengo lista codigos que no están en pedidoSolicitado
    dfsProbByCod = pd.DataFrame(list(formatoByCodigoDict))
    dfsProbByCod.columns = ["codigoNew"]

    for maceta in pedidoSolicitado.listadoMacetas:
        dfsProbByCod = dfsProbByCod.drop(dfsProbByCod[dfsProbByCod["codigoNew"]==maceta.codigo].index)
    dfsProbByCod = dfsProbByCod.reset_index(drop=True) ##reseteo indices luego del drop

    ## para cada uno busco la prob y armo otra columna en el df
    probsList = []
    hVals = getHMatrix(codigosConPedidosRegistrados,listPedidos)

    xVals = getXVals(pedidoSolicitado, codigosConPedidosRegistrados)
    

    for i, row in dfsProbByCod.iterrows():
        i=i
        codNew = row["codigoNew"]
        yVec = getYVec(codNew,listPedidos)
        if(yVec.sum()==0):
            prob = 0
        elif(yVec.sum()==len(yVec)):
            prob = 1
        else:
            prob = getProbCompraEstimation(hVals,yVec,xVals)
        probsList.append(prob)
    
    dfsProbByCod['probRec'] = pd.DataFrame(probsList)
    
    ## ordeno el df y paso a lista los codigos
    dfsProbByCod.sort_values(by=['probRec'], inplace=True, ascending=False)
    return dfsProbByCod["codigoNew"].to_json(orient = "records")


def getCodigosConPedidos(listMacetas, pedidosCollection):
    listCodigosConPedidos = []
    for maceta in listMacetas:
        codNew = maceta.codigo
        query = {codNew : { "$exists": True }}
        listPedidos = list(pedidosCollection.find(query))
        if(len(listPedidos)>0):
            listCodigosConPedidos.append(codNew)
    return listCodigosConPedidos


def getHMatrix(listCodigos,listPedidos):
    vecPedidosMat = []
    for pedido in listPedidos:
        vecCantByModelo = []
        for cod in listCodigos:
            if(cod in pedido):
                cant = pedido[cod]
            else:
                cant=0
            vecCantByModelo.append(cant)
        vecPedidosMat.append(vecCantByModelo) 
    return np.matrix(vecPedidosMat)

def getYVec(codNew,listPedidos):
    yVec = []
    for pedido in listPedidos:
        if(codNew in pedido):
            value = 1
        else:
            value=0
        yVec.append(value)
    return np.matrix(yVec).T

def getXVals(pedidoSolicitado, codigosConPedidos):
    xVals = []
    for maceta in pedidoSolicitado.listadoMacetas:
        if(maceta.codigo in codigosConPedidos):
            xVals.append(maceta.cantidad)
    return np.array(xVals)
    
def getPedidosEntregados(formatoByCodigoDict):
    ontiveroDb = mongo.db
    dfPedidosFecha = getFechas(ontiveroDb)
    dfPedidos = getPedidos(ontiveroDb)

    dfPedidosByFormato = getPedidosByFormato(dfPedidos, dfPedidosFecha, formatoByCodigoDict)

    #plt.figure(figsize=(10,4))
    listFormatos = pd.Series(list(formatoByCodigoDict.values())).unique()

    dfPedidosByTrimestre = dfPedidosByFormato.resample('3m').sum()
    
    dfPedidosByTrimestre['fechas'] = dfPedidosByTrimestre.index.strftime("%d/%m/%Y")
    
    #for formato in listFormatos:
    #    if(formato in dfPedidosByTrimestre):
            #plt.scatter(dfPedidosByTrimestre['fecha'],dfPedidosByTrimestre[formato])
    #        plt.plot(dfPedidosByTrimestre[formato])
            
    #plt.legend(listFormatos)
    #plt.show()

    return str(dfPedidosByTrimestre.to_dict(orient = "list")).replace("\'","\"").replace(".0","")

def getPedidosByFormato(dfPedidos, dfPedidosFecha, formatDict):
    dfPedidosFull = pd.merge(left=dfPedidos, right=dfPedidosFecha, how='left', left_index=True, right_index=True)
    dfPedidosFull.dropna(inplace=True)
    
    dfPedidosTransp = dfPedidosFull.T
    rowFechas = dfPedidosFull.iloc[:,-1]
    dfPedidosTransp.drop(dfPedidosTransp.tail(1).index, inplace = True)
    dfAux = pd.DataFrame(dfPedidosTransp.index.values)
    dfAux.columns = ['values']

    dfAux2 = pd.DataFrame(dfAux["values"].apply(lambda x: formatDict[x]))
    dfAux2 = dfAux2.set_index(dfPedidosTransp.index)
    dfPedidosTransp["formato"] = dfAux2
    
    dfPedidosFormato = dfPedidosTransp.groupby('formato').sum().T
    dfFechas = pd.DataFrame(rowFechas)
    dfFechas.columns = ['fecha']
    dfPedidosFormato["fecha"] = pd.to_datetime(dfFechas['fecha'], format="%d/%m/%Y")

    dfPedidosFormato = dfPedidosFormato.groupby('fecha').sum()
    dfPedidosFormato.dropna(inplace=True)
    return dfPedidosFormato
    
def getFechas(db):
    pedidosInfo = db['pedidos_info']
    listPedidosInfo = list(pedidosInfo.find({}))
    dfPedidosInfo = pd.DataFrame(listPedidosInfo)
    dfPedidosFecha = dfPedidosInfo[['fecha_entrega','id_pedido']]
    dfPedidosFecha = dfPedidosFecha.dropna()
    dfPedidosFecha['fecha_entrega'] = dfPedidosFecha['fecha_entrega'].apply(lambda x: datetime.strftime(x, "%d/%m/%Y"))
    dfPedidosFecha.set_index("id_pedido", inplace=True)
    dfPedidosFecha.columns=['fecha']
    return dfPedidosFecha

def getPedidos(db):
    pedidos = db['pedidos']
    listPedidos = list(pedidos.find({}))
    dfPedidos = pd.DataFrame(listPedidos)
    dfPedidos.drop('_id', axis=1, inplace=True)
    dfPedidos.set_index("id_pedido", inplace=True)
    dfPedidos.fillna(0, inplace=True)
    return dfPedidos