from mongoConnection import mongo
import pandas as pd

def getPedidosEntregados():
    listPedidos = list([{"_id":"23123123","id":"1","021":3,"030":4},{"_id":"23123124","id":"2","012":1,"003":2},{"_id":"23123141","id":"3","001":5}])
    dfPedidos = pd.DataFrame(listPedidos)
    return dfPedidos

dfPedidos = getPedidosEntregados()
