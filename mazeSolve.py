import numpy as np
import cv2
import math

SURROUNDINGS_DISTANCE = 5
DIFFERENCE_THRESHOLD = 20
COLOR_DIFFERENCE_THRESHOLD = 20

def absoluteBrightness(color):
    return int(math.sqrt(color[0]**2 + color[1]**2 + color[2]**2))

def surroundingsAverage(brightnesses, row, col, surr_dist = SURROUNDINGS_DISTANCE):
    neighborBrightnesses = []
    for row in range(row - surr_dist, row + surr_dist + 1):
        for col in range(col - surr_dist, col + surr_dist + 1):
            try:
                neighborBrightnesses.append(brightnesses[row][col])
            except IndexError:
                pass
    return sum(neighborBrightnesses)/len(neighborBrightnesses)




# Create maze array in format wall = 0, free = 1, start = 2, end = 3
def createMaze(frame):
    brightnesses = []
    for row in range(len(frame)):
        brightnesses.append([])
        for col in range(len(frame[row])):
            brightnesses[row].append(absoluteBrightness(frame[row][col]))

    maze = []
    for row in range(len(frame)):
        maze.append([])
        for col in range(len(frame[row])):
            pixelBrightness = absoluteBrightness(frame[row][col])
            #Case for a red, starting area
            if frame[row][col][2] > frame[row][col][0] + COLOR_DIFFERENCE_THRESHOLD and frame[row][col][2] > frame[row][col][1] + COLOR_DIFFERENCE_THRESHOLD:
                maze[row].append(2)
                frame[row][col] = [0,0,255]
            #Case for a blue, ending area
            elif frame[row][col][0] > frame[row][col][1] + COLOR_DIFFERENCE_THRESHOLD and frame[row][col][0] > frame[row][col][2] + COLOR_DIFFERENCE_THRESHOLD:
                frame[row][col] = [255, 0, 0]
                maze[row].append(3)
            #Threshold for black pixel being a wall
            elif pixelBrightness < surroundingsAverage(brightnesses, row, col) - DIFFERENCE_THRESHOLD:
                maze[row].append(0)
                frame[row][col] = [0,0,0]
            #Turn pixel to white otherwise
            else:
                maze[row].append(1)
                frame[row][col] = [255, 255, 255]

    cv2.imshow('result', frame)
    if cv2.waitKey(0) == ord('q'):
        cv2.destroyWindow('result')
    return maze, frame

def solve(frame):
    createMaze(frame)
