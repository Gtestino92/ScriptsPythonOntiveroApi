
def getCodigoByTituloMlibre(mysql):
    query = '''SELECT nombre_publicacion, codigo_nuevo FROM codigos_mlibre'''
    result = executeSelect(mysql,query)
    return resultSQLToDict(result, 'nombre_publicacion', 'codigo_nuevo')

def getFormatoByCodigoNew(mysql):
    query = '''SELECT codigo_nuevo, formato FROM lista_macetas WHERE estado="A"'''
    result = executeSelect(mysql,query)
    return resultSQLToDict(result, 'codigo_nuevo', 'formato')

def executeSelect(sqlConn, query):
    cur = sqlConn.connection.cursor()
    cur.execute(query)
    return cur.fetchall()

def resultSQLToDict(sqlRes, key, value):
    return {elem[key]:elem[value] for elem in sqlRes}
   