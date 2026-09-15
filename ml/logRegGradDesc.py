import numpy as np
import math
import time
from exceptions.singularMatException import SingularMatException

MAX_ITER = 100
MIN_DIST = 0.1
GRAF_STEP = 10

def getProbCompraEstimation(hVals,yVec,xVals):
    n = hVals.shape[0]
    d = hVals.shape[1] + 1
    wVecInit = np.matrix(np.zeros(d)).reshape(-1,1)
    A = getAMatrix(hVals)
    if(np.linalg.matrix_rank(A) != d):
        raise SingularMatException(406)
    wVecOpt = getOptwVec(A,yVec,hVals,wVecInit,n)
    return alfaVal(wVecOpt,getxVec(xVals))

def alfaVal(wVec, xVec):
    return 1/(1 + math.exp(-(wVec.T*xVec).item()))

def getxVec(hVals):
    xList = [1]
    for hVal in hVals:
        xList.append(hVal)
    return np.matrix(xList).reshape(-1,1)

def getAlfaVec(wVec,hVals,n):
    alfaVec = []
    for i in range(n):
        alfaVec.append(alfaVal(wVec,getxVec(np.ravel(hVals[i][:]))))
    return np.matrix(alfaVec).reshape(-1,1)

def getBMatrix(alfaVec):
    vecDiag = []
    for alfa in alfaVec:
        auxDiag = alfa * (1 - alfa)
        vecDiag.append(auxDiag.item())
    return np.matrix(np.diag(vecDiag))

def getAMatrix(hVals):
    listX = []
    for h in hVals:
        xVec = getxVec(np.ravel(h)).T
        listX.append(xVec.tolist()[0])
    return np.matrix(listX)

def getNextwVec(wVec,A,B,alfaVec,yVec):
    return wVec - ( np.linalg.inv(A.T * B * A) * (A.T) * (alfaVec - yVec))

def getOptwVec(A, yVec, hVals, wVecInit,n):
    wVec = wVecInit
    alfaVec = getAlfaVec(wVec,hVals,n)
    B = getBMatrix(alfaVec)
    i = 0
    while i < MAX_ITER:    
        likelihoodOld = calcLikelihood(alfaVec, yVec)
        wVec = getNextwVec(wVec,A,B,alfaVec,yVec)
        alfaVec = getAlfaVec(wVec,hVals,n)
        B = getBMatrix(alfaVec)
        likelihood = calcLikelihood(alfaVec,yVec)
        dist = np.absolute((likelihood-likelihoodOld)*100/likelihoodOld)
        if(dist<MIN_DIST): 
            break
        i+=1
    return wVec

def calcLikelihood(alfaVec, yVec):
    likelihood = 1
    for i in range(len(alfaVec)):
        alfa = alfaVec[i].item()
        y = yVec[i].item()
        likelihood *= math.pow(alfa,y) * math.pow((1-alfa), (1-y))
    return likelihood

hVals1A = np.transpose(np.matrix([[1, 60, 20, 30, 80, 50, 50, 40, 30, 20, 10, 30, 100, 120, 140, 100, 20, 10]]))

yVecA = np.matrix(np.array([0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 1, 0, 1, 0, 1, 1, 0, 1])).reshape(-1,1)

xVals1 = np.array([0])
#p = getProbCompraEstimation(hVals1A,yVecA,xVals1)
