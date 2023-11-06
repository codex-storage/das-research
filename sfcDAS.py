from hilbertcurve.hilbertcurve import HilbertCurve
import plotly.express as px
import numpy as np
from random import *

dimension = 2

def plotMatrix(matrix, fileName):
    fig = px.imshow(matrix, color_continuous_scale="hot")
    fig.update_xaxes(side="top")
    fig.update_layout(height=700, width=700)
    fig.write_image(fileName)


def expandMatrix(newMatrix, matrix, expandIndex):
    xlen = len(matrix)
    ylen = len(matrix[0])
    #print(f'x = {xlen} y = {ylen}')
    for i in range(xlen * expandIndex):
        for j in range(ylen * expandIndex):
            if matrix[int(i/expandIndex)][int(j/expandIndex)] > 0:
                newMatrix[i][j] = matrix[int(i/expandIndex)][int(j/expandIndex)]
    return newMatrix


def doHilbert(hilbMatrix, depth, custSize, DASsize, nbVal):

    # Compute Hilbert curve
    HdistMatrix = np.zeros((2**depth, 2**depth))
    HcustMatrix = np.zeros((2**depth, 2**depth))
    Hcurve = HilbertCurve(depth, dimension)
    distances = list(range(2**(depth*2)))
    points = Hcurve.points_from_distances(distances)

    # Compute custody tiles
    for v in range(nbVal):
        custList = []
        startPosition = randint(0, (2**(depth*2))-1)
        for i in range(custSize):
            custList.append((startPosition+i)%(2**(depth*2)))
        #print(f'Start position = {startPosition}')
        for point, dist in zip(points, distances):
            j, i = point
            HdistMatrix[i][j] = dist
            if dist in custList:
                HcustMatrix[i][j] = v+1
    #print(HdistMatrix)
    #print(HcustMatrix)

    # From Hilbert curve depth to DAS size
    HcustMatrix = expandMatrix(hilbMatrix, HcustMatrix, int(DASsize/(2**depth)))

    return(hilbMatrix)


def doTile(tileMatrix, depth, custSize, DASsize, nbVal):
    ttMatrix = np.zeros((2**depth, 2**depth))
    for v in range(nbVal):
        for i in range(custSize):
            ttMatrix[randint(0, (2**depth)-1)][randint(0, (2**depth)-1)] = v+1
    tileMatrix = expandMatrix(tileMatrix, ttMatrix, int(DASsize/(2**depth)))
    return(tileMatrix)


def doRowCol(matrix, custSize, DASsize, nbVal):
    for v in range(nbVal):
        custList = []
        for x in range(custSize):
            custList.append(randint(0, DASsize-1))
        half = int(custSize/2)
        rows = custList[:half]
        cols = custList[half:]
        for r in rows:
            for x in range(DASsize):
                matrix[r][x] = v+1
        for c in cols:
            for x in range(DASsize):
                matrix[x][c] = v+1
    return(matrix)


def doDiagonal(matrix, custSize, DASsize, nbVal):
    for v in range(nbVal):
        custList = []
        for x in range(custSize):
            custList.append(randint(0, DASsize-1))
        for c in custList:
            cc = c
            for x in range(DASsize):
                matrix[x][cc] = v+1
                cc = (cc + 1) % DASsize
    return(matrix)



custStart = 4
custStop = 39
custStep = 4
cs = 4
nbVal = 10
depth = 5
DASsize = 512
totalVal = 0

diagMatrix = np.zeros((DASsize, DASsize))
rocoMatrix = np.zeros((DASsize, DASsize))
tileMatrix = np.zeros((DASsize, DASsize))
hilbMatrix = np.zeros((DASsize, DASsize))

for i in range(50):
    nbVal = 5
    totalVal += nbVal
    print(f'Number of validators: {totalVal}')

    HilbertMatrix = doHilbert(hilbMatrix, depth, cs, DASsize, nbVal)
    plotMatrix(HilbertMatrix, "frames/4hilbertCust"+str(i)+".png")

    rowColMatrix = doRowCol(rocoMatrix, cs, DASsize, nbVal)
    plotMatrix(rowColMatrix, "frames/1rowColCust"+str(i)+".png")

    diagonalMatrix = doDiagonal(diagMatrix, cs, DASsize, nbVal )
    plotMatrix(diagonalMatrix, "frames/2diagonalCust"+str(i)+".png")

    tileMatrix = doTile(tileMatrix, depth, cs, DASsize, nbVal)
    plotMatrix(tileMatrix, "frames/3tileCust"+str(i)+".png")







