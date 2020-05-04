import numpy as np
import cv2
import math
import statistics as st

ROW_CHUNK_AMOUNT = 16
COL_CHUNK_AMOUNT = 14
RED_THRESH = 30
BLUE_THRESH = 30
BLACK_THRESH = 120

def chunkMedian(values, startRow, startCol, chunkHeight, chunkWidth):
    chunkValues = []
    for row in range(startRow, startRow + chunkHeight):
        for col in range(startCol, startCol + chunkWidth):
            chunkValues.append(values[row][col])
    blueValues = [float(val[0]) for val in chunkValues]
    greenValues = [float(val[1]) for val in chunkValues]
    redValues = [float(val[2]) for val in chunkValues]
    return [int(st.median(blueValues)), int(st.median(greenValues)), int(st.median(redValues))], \
        [int(st.pstdev(blueValues)), int(st.pstdev(greenValues)), int(st.pstdev(redValues))]

def brightnessProcessFunc(pixel):
    return int(pixel[0]) + int(pixel[1]) + int(pixel[2])

def corrChunkMedian(frame, chunkMedians, row, col, processFunction):
    # Calculate the chunk corresponding to the given pixel
    chunkRow = row * ROW_CHUNK_AMOUNT // len(frame)
    chunkCol = col * COL_CHUNK_AMOUNT // len(frame[0])
    # Return the average of the found chunk (or the furthest one in case of overflow)
    median, dev = chunkMedians[min(chunkRow, len(chunkMedians))][min(chunkCol, len(chunkMedians[0]))]
    return processFunction(median), processFunction(dev)



# Create maze array in format wall = 0, free = 1, start = 2, end = 3
def createMaze(frame):
    # Construct the chunk matrix with the average values for each chunk
    chunkHeight = len(frame)//ROW_CHUNK_AMOUNT
    chunkWidth = len(frame[0])//COL_CHUNK_AMOUNT
    chunkValMeds = []
    for chunkY in range(ROW_CHUNK_AMOUNT):
        chunkValMeds.append([])
        for chunkX in range(COL_CHUNK_AMOUNT):
            chunkMed = chunkMedian(frame, chunkY*chunkHeight, chunkX*chunkWidth, chunkHeight, chunkWidth)
            chunkValMeds[chunkY].append(chunkMed)


    maze = []
    for row in range(len(frame)):
        maze.append([])
        for col in range(len(frame[row])):
            brightMed, brightDev = corrChunkMedian(frame, chunkValMeds, row, col, brightnessProcessFunc)

            if frame[row][col][2] >  frame[row][col][0] + RED_THRESH and frame[row][col][2] >  frame[row][col][1] + RED_THRESH:
                #Case for a red, starting area
                frame[row][col] = [0,0,255]
            elif frame[row][col][0] >  frame[row][col][1] + BLUE_THRESH and frame[row][col][0] >  frame[row][col][2] + BLUE_THRESH:
                #Case for a blue, ending area
                frame[row][col] = [255, 0, 0]
            elif brightnessProcessFunc(frame[row][col]) < brightMed - BLACK_THRESH:
                #Threshold for black pixel being a wall
                frame[row][col] = [0,0,0]
            else:
                #Turn pixel to white otherwise
                frame[row][col] = [255, 255, 255]

    cv2.imshow('result', frame)
    if cv2.waitKey(0) == ord('q'):
        cv2.destroyWindow('result')
    return maze, frame

def solve(frame):
    createMaze(frame)
