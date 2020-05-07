import numpy as np
import cv2
import math
import statistics as st
from mazeSquare import MazeSquare

ROW_CHUNK_AMOUNT = 16
COL_CHUNK_AMOUNT = 14
RED_THRESH = 30
BLUE_THRESH = 20
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

def checkFinished(currentSquares):
    for square in currentSquares:
        if square.type == "end":
            return True
    return False

def solutionPath(currentSquares):
    end = None
    for square in currentSquares:
        if square.type == "end":
            end = square
            break

    path = []
    currentSquare = end
    while currentSquare.type != "start":
        path.append(currentSquare)
        currentSquare = currentSquare.parent

    return path

def solutionFrame(frame, path):
    for square in path:
        frame[square.row][square.col] = [203, 192, 255]

    return frame

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
                maze[row].append(MazeSquare("start", row, col))
            elif frame[row][col][0] >  frame[row][col][1] + BLUE_THRESH and frame[row][col][0] >  frame[row][col][2] + BLUE_THRESH:
                #Case for a blue, ending area
                frame[row][col] = [255, 0, 0]
                maze[row].append(MazeSquare("end", row, col))
            elif brightnessProcessFunc(frame[row][col]) < brightMed - BLACK_THRESH:
                #Threshold for black pixel being a wall
                frame[row][col] = [0,0,0]
                maze[row].append(MazeSquare("wall", row, col))
            else:
                #Turn pixel to white otherwise
                frame[row][col] = [255, 255, 255]
                maze[row].append(MazeSquare("free", row, col))

    return maze, frame

def solve(frame):
    maze, procFrame = createMaze(frame)

    currentExploringSquares = []

    for row in range(len(maze)):
        for col in range(len(maze[row])):
            if maze[row][col].type == "start":
                currentExploringSquares.append(maze[row][col])
                maze[row][col].exploreState = "exploring"



    nextSquares = []
    while True:
        cv2.imshow('maze', frame)
        key = cv2.waitKey(1)
        if key == ord('q'):
            break


        if checkFinished(currentExploringSquares):
            path = solutionPath(currentExploringSquares)
            while True:
                cv2.imshow('maze', solutionFrame(frame, path))
                key = cv2.waitKey(0)
                if key == ord('q'):
                    return path


        # Find all the squares adjecent to an explored square
        for square in currentExploringSquares:
            frame[square.row][square.col] = [0, 255, 0]

            neighbors = [
                maze[square.row][square.col+1],
                maze[square.row][square.col-1],
                maze[square.row+1][square.col],
                maze[square.row-1][square.col]
            ]
            for candidate in neighbors:
                if candidate.explorable():
                    candidate.exploreState = "exploring"
                    candidate.parent = square
                    nextSquares.append(candidate)

            square.exploreState = "explored"

        # Replace the old current squares with the new ones
        currentExploringSquares = nextSquares
        nextSquares = []
