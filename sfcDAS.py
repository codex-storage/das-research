from hilbertcurve.hilbertcurve import HilbertCurve
import plotly.express as px
import numpy as np
from random import *

dimension = 2

def plotMatrix(matrix, fileName):
    fig = px.imshow(matrix)
    fig.update_xaxes(side="top")
    fig.update_layout(height=700, width=700)
    fig.write_image(fileName)


def expandMatrix(matrix, expandIndex):
    xlen = len(matrix)
    ylen = len(matrix[0])
    #print(f'x = {xlen} y = {ylen}')
    newMatrix = np.zeros((xlen * expandIndex, ylen * expandIndex))
    for i in range(xlen * expandIndex):
        for j in range(ylen * expandIndex):
            newMatrix[i][j] = matrix[int(i/expandIndex)][int(j/expandIndex)]
    return newMatrix


def doHilbert(depth, custSize, DASsize):

    # Compute Hilbert curve
    HdistMatrix = np.zeros((2**depth, 2**depth))
    HcustMatrix = np.zeros((2**depth, 2**depth))
    Hcurve = HilbertCurve(depth, dimension)
    distances = list(range(2**(depth*2)))
    points = Hcurve.points_from_distances(distances)

    # Compute custody tiles
    custList = []
    startPosition = randint(0, 2**(depth*2))
    for i in range(custSize):
        custList.append((startPosition+i)%(2**(depth*2)))
    print(f'Start position = {startPosition}')
    for point, dist in zip(points, distances):
        j, i = point
        HdistMatrix[i][j] = dist
        if dist in custList:
            HcustMatrix[i][j] = 1
    #print(HdistMatrix)
    #print(HcustMatrix)

    # From Hilbert curve depth to DAS size
    HcustMatrix = expandMatrix(HcustMatrix, int(DASsize/(2**depth)))

    return(HcustMatrix)


def doTile(depth, custSize, DASsize):
    tileMatrix = np.zeros((2**depth, 2**depth))
    for i in range(custSize):
        tileMatrix[randint(0, 2**depth)][randint(0, 2**depth)] = 1
    tileMatrix = expandMatrix(tileMatrix, int(DASsize/(2**depth)))
    return(tileMatrix)


def doRowCol(custSize, DASsize):
    custList = []
    for x in range(custSize):
        custList.append(randint(0, DASsize))
    half = int(custSize/2)
    rows = custList[:half]
    cols = custList[half:]
    matrix = np.zeros((DASsize, DASsize))
    for r in rows:
        for x in range(DASsize):
            matrix[r][x] = 1
    for c in cols:
        for x in range(DASsize):
            matrix[x][c] = 1
    return(matrix)


def doDiagonal(custSize, DASsize):
    custList = []
    for x in range(custSize):
        custList.append(randint(0, DASsize))
    matrix = np.zeros((DASsize, DASsize))
    for c in custList:
        cc = c
        for x in range(DASsize):
            matrix[x][cc] = 1
            cc = (cc + 1) % DASsize
    return(matrix)




depth = 5
custSize = 4
DASsize = 512

HilbertMatrix = doHilbert(depth, custSize, DASsize)
plotMatrix(HilbertMatrix, "hilbertCust.png")

rowColMatrix = doRowCol(custSize, DASsize)
plotMatrix(rowColMatrix, "rowColCust.png")

diagonalMatrix = doDiagonal(custSize, DASsize)
plotMatrix(diagonalMatrix, "diagonalCust.png")

tileMatrix = doTile(depth, custSize, DASsize)
plotMatrix(tileMatrix, "tileCust.png")







