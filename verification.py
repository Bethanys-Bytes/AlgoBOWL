from utils.Stack import Stack
from utils.input_parser import FieldTiles, get_point_value, HorseField
from argparse import ArgumentParser

# GLOBALS
inputGrid = []
inputGridDict = {}
wallBudget = 0
outputGrid = [] # State of the output-world
outputGridDict = {} # Dictionary of all outputGrid positions for verifying score
suggestedScore = 0 # score from unverified output
horsePosition = None # horsePosition we can use to begin DFS search
numRows = 0
numCols = 0
portals = {}
"""
readOutput() parses input similar how input is parsed in solver.py.
It also creates a key,value pair in outputGridDict in the form of (cell, cell_type)
where we can easily look up what a cell is (apples, bees, wall, water, etc.)
"""
def readInput(filename=None):
    global wallBudget, numRows, numCols, inputGrid, portals
    fieldInput = HorseField(filename)
    wallBudget = fieldInput.wallBudget
    numRows = fieldInput.row_count
    numCols = fieldInput.col_count
    inputGrid = fieldInput.grid
    portals = fieldInput.portals
    for r in range(numRows):
        for c in range(numCols):
            cell_type = inputGrid[r][c]
            if(cell_type == FieldTiles.HORSE):
                horsePosition = (r,c)
            inputGridDict[(r,c)] = cell_type

def _readOutput(input_function):
    global suggestedScore, horsePosition
    suggestedScore = int(input_function())

    for r in range(numRows):
        row = list(input_function().strip())
        outputGrid.append(row)
        for c in range(numCols):
            cell_type = outputGrid[r][c]
            if(cell_type == FieldTiles.HORSE):
                horsePosition = (r,c)
            outputGridDict[(r,c)] = cell_type

def readOutput(filename):
    if filename:
        with open(filename, "r", encoding="utf-8") as f:
            _readOutput(lambda : f.readline().replace("\n",""))
    else:
        _readOutput(lambda : input())

""" 
verifyOutput will be in charge of the heavy lifting for verification. It will run a modified DFS to check if the 
perimeter is accessible in the output. It will also be in charge of making sure that no new walls
were placed on cells that are also water, pre-placed walls, bees, apples, cherries, portals, horse.
"""
def verifyNoEscape(outputGrid, horsePosition):
    verifiedScore = 0 # initialize the score which we will check against the suggestedScore after DFS has finished
    stack = Stack()
    visited = set()
    stack.push(horsePosition) # push horsePosition (start) onto stack
    while not stack.is_empty():
        current = stack.pop() # get the cell at the top of stack
        if current[0] == 0 or current[0] == numRows - 1 or \
            current[1] == 0 or current[1] == numCols - 1: # check if current cell is a perimeter grass cell, if it is output is invalid
            print("Perimeter Breached!")
            return False
        if current in visited: # skip neighbor if we already visited
            continue
        visited.add(current)
        verifiedScore+=get_point_value(outputGridDict.get(current)) # add score to verifiedScore
        neighbors = findNeighbors(outputGrid, current) # find the neighbors of the current cell
        for cell in neighbors: # for each neighbor
            if cell not in visited:
                stack.push(cell) # push neighbor to stack if not already visited
    print(f"suggested score: {suggestedScore}\nverified score: {verifiedScore}")
    if suggestedScore == verifiedScore: # if both our calculated score and output suggestedScore are the same AND DFS completed, then the format of the output is valid
        return True
    print(f"Suggested Score {suggestedScore} does not match Verified Score {verifiedScore}. Invalid!")
    return False
"""
findNeighbors is a helper function to finding grass cells adjacent to a given cell, it returns a list of all adjacent grass cells
"""
def findNeighbors(outputGrid, cell):
    neighbors = set()
    directions = [(-1, 0), (1,0), (0, -1), (0,1)] # UP, DOWN, LEFT, RIGHT
    for dr, dc in directions:
        r, c = cell[0] + dr, cell[1] + dc
        if 0 <= r < numRows and 0 <= c < numCols:
            if outputGrid[r][c] not in (FieldTiles.WATER, FieldTiles.WALL): # skip walls and water
                neighbors.add((r,c))
    if(outputGridDict.get((cell[0], cell[1])) == FieldTiles.PORTAL):
        neighbors.add(portals.get((cell[0], cell[1])))
    return neighbors

def verifyOutputFormat():
    usedWalls = 0
    for i in range(numRows):
        for j in range(numCols):
            input_cell = inputGridDict.get((i,j))
            output_cell = outputGridDict.get((i,j))
            if input_cell != output_cell:
                if input_cell == FieldTiles.GRASS and output_cell == FieldTiles.WALL:
                    usedWalls+=1
                    continue
                elif input_cell == FieldTiles.WALL and output_cell == FieldTiles.GRASS:
                    continue  # valid to remove a pre-placed wall
                else:
                    print(f"Illegal wall placement at: ({i}, {j}). It was a {input_cell}. Now it is a {output_cell}.")
                    return False
    if usedWalls <= wallBudget:
        return True
    else:
        print(f"Output walls exceeded wall budget! Wall budgert is: {wallBudget}. The output grid used: {usedWalls} new walls.")
        return False




if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument('-fin', '--filename_in', default=None)
    parser.add_argument('-fout', '--filename_out', default=None)
    args = parser.parse_args()
    readInput(args.filename_in)
    readOutput(args.filename_out)
    isEscapeable = verifyNoEscape(outputGrid, horsePosition)
    isValidFormat = verifyOutputFormat()
    print(f"No escape routes? -> {isEscapeable}\nValid format? -> {isValidFormat}")
