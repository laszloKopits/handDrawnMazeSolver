import numpy as np

class MazeSquare:

    def __init__(self, type, row, col):
        self.type = type
        self.exploreState = "unexplored"
        self.parent = None
        self.row = row
        self.col = col

    def explorable(self):
        return (self.type == "free" and self.exploreState == "unexplored") or self.type == "end"

    def __repr__(self):
        return str(self.type) + ", " + str(exploreState) + ": " + str(self.row) + ", " + str(self.col)
