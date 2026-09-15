import json
import pandas as pd
import numpy as np
import datetime

def makePedidosFromXlsx(file, codigosMacetasMlibre):
    fileInfo = open("macetasInfo.xlsx", "rb")
    dictMeses = {
    "enero": "01",
    "febrero": "02",
    "marzo": "03",
    "abril": "04",
    "mayo": "05",
    "junio": "06",
    "julio": "07",
    "agosto": "08",
    "septiembre": "09",
    "octubre": "10",
    "noviembre": "11",
    "diciembre": "12"
    }


    ## Leo archivos

    dfs = pd.read_excel(file, header=1, sheet_name='Ventas AR', encoding="ascii")

    dfs = dfs[["Nombre del comprador", "Apellido del comprador", "Título de la publicación",
        "Estado", "Fecha de venta", "Descripción del estado", 
        "Unidades", "Ingresos (ARS)"]]


    ## columna de nombre

    dfs['nombre'] = dfs["Nombre del comprador"] + " " + dfs["Apellido del comprador"]

    def normalize(s):
        replacements = (
            ("á", "a"),
            ("é", "e"),
            ("í", "i"),
            ("ó", "o"),
            ("ú", "u"),
            ("ñ", "n")
        )
        for a, b in replacements:
            s = s.replace(a, b).replace(a.upper(), b.upper())
        return s

    dfs['nombre'] = dfs['nombre'].apply(lambda x: normalize(x))

    dfs = dfs[["nombre", "Título de la publicación",
        "Estado", "Fecha de venta", "Descripción del estado", 
        "Unidades", "Ingresos (ARS)"]]


    ## Obtengo codigoNew de cada venta
    dfTit3Aux = dfs['Título de la publicación'].str.split("- ", n = 3, expand = True)
    
    if(len(dfTit3Aux.columns) == 4):
        dfs['titulo'] = dfTit3Aux[3]
    else:
        dfs['titulo'] = pd.DataFrame(np.nan, index = np.arange(len(dfs)), columns = ['titulo'])
    
    serieAux = dfs.loc[dfs["titulo"].isnull(), "Título de la publicación"]
    frame = {'Título de la publicación': serieAux } 
    dfAux = pd.DataFrame(frame)
    dfs.loc[dfs["titulo"].isnull(), "titulo"] = dfAux["Título de la publicación"].str.split("- ", n = 2, expand = True)[2]

    serieAux2 = dfs.loc[dfs["titulo"].isnull(), "Título de la publicación"]
    frame2 = {'Título de la publicación': serieAux2 } 
    dfAux2 = pd.DataFrame(frame2)

    dfs.loc[dfs["titulo"].isnull(), "titulo"] = dfAux2["Título de la publicación"].str.split("- ", n = 1, expand = True)[1]

    modelosList = []
    for i, row in dfs.iterrows():
        titulo = row["titulo"]
        #dfInfoAux = dfsInfo.loc[dfsInfo["Titulo"] == titulo, "codigo nuevo"]
        #value = dfInfoAux.values[0]
        modelosList.append(codigosMacetasMlibre[titulo])

    dfs['codigoNew'] = pd.DataFrame(modelosList)

    ## Obtengo fechaSolicitud

    dfs["fechaSolicitudAux"] = dfs["Fecha de venta"].str.split(" de ", n = 3, expand = False)

    fechasSolicitudList = []
    for i, row in dfs.iterrows():
        value = row["fechaSolicitudAux"]
        dia = value[0] if (len(value[0]) == 2) else ("0" + value[0])
        mes = dictMeses[value[1]]
        anio = value[2][:4]
        fechasSolicitudList.append(dia + "/" + mes + "/" + anio)

    dfs['fechaSolicitud'] = pd.DataFrame(fechasSolicitudList)


    ## Obtengo fecha de Entrega

    def getFechaByArribo(descripcionEstado, fechaSolicitud):
        ##Llegó el 19 de julio
        if(descripcionEstado[:5]=="Llegó"):
            diaIsSingleDigit = (descripcionEstado[10] == " ")
            dia = ("0" + descripcionEstado[9]) if diaIsSingleDigit else descripcionEstado[9:11]
            mes = dictMeses[descripcionEstado[14:] if diaIsSingleDigit else descripcionEstado[15:]]
            anio = fechaSolicitud.split("/")[2]
            return dia + "/" + mes + "/" + anio
        else:
            return getFechaPasadoUnMes(fechaSolicitud)

    def getFechaPasadoUnMes(fechaSolicitud):
        fechaVec = fechaSolicitud.split("/")
        dateSolicitud = datetime.datetime(int(fechaVec[2]), int(fechaVec[1]), int(fechaVec[0]))
        dateEntrega = dateSolicitud + datetime.timedelta(days=28) 
        return dateEntrega.strftime("%d") + "/" + dateEntrega.strftime("%m") + "/" + dateEntrega.strftime("%Y")

    fechasEntregaList = []
    for i, row in dfs.iterrows():
        estado = row["Estado"]
        fechaEntrega = ""
        if(estado=="Entregado"):
            fechaEntrega = getFechaByArribo(row["Descripción del estado"], row["fechaSolicitud"])
        elif(estado=="Venta concretada"):
            fechaEntrega = getFechaPasadoUnMes(row["fechaSolicitud"])
        fechasEntregaList.append(fechaEntrega)

    dfs['fechaEntrega'] = pd.DataFrame(fechasEntregaList)
    dfs.drop(dfs[dfs["fechaEntrega"] == ""].index, axis=0, inplace=True)
    dfs = dfs.reset_index(drop=True) ##reseteo indices luego del drop
    
    # Renombro columnas
    dfs["totalAux"] = dfs["Ingresos (ARS)"] 
    dfs["cantidad"] = dfs["Unidades"]

    # Saco el punto "." de la columna de totales
    totalList = []
    for i, row in dfs.iterrows():
        value = row["totalAux"]
        ##totalList.append(str(int(round(float(value.replace(".","").replace(",","."))))))
        res = str(int(round(float(value.replace(".","").replace(",",".")))))
        totalList.append(res)

    dfs['total'] = pd.DataFrame(totalList)

    # Output
    dfs = dfs[["nombre", "codigoNew", "fechaSolicitud", "fechaEntrega", "cantidad", "total"]]

    dfs.to_excel("fileOutput.xlsx")  

    file.close()
    fileInfo.close()
    # Paso a string JSON
    return dfs.to_json(orient = "records").replace("\/","/")
