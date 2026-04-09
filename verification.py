from utils.Stack import Stack
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
pointsDict = { # Dictionary for calculating score
    "." : 1,
    "a" : 11,
    "b" : -4,
    "c" : 4,
    "H" : 1,
    "p" : 1,
    "#" : 0,
    "W" : 0
}
portals = {}
"""
readOutput() parses input similar how input is parsed in solver.py.
It also creates a key,value pair in outputGridDict in the form of (cell, cell_type)
where we can easily look up what a cell is (apples, bees, wall, water, etc.)
"""
def readInput():
    global wallBudget, numRows, numCols
    wallBudget = int(input())
    numRows, numCols = map(int, input().split())
    for r in range(numRows):
        row = list(input().strip())
        inputGrid.append(row)
        for c in range(numCols):
            cell_type = inputGrid[r][c]
            inputGridDict[(r,c)] = cell_type
    numPortals = int(input())
    for r in range(numPortals):
        r1, c1, r2, c2 = map(int, input().split())
        # A (row, col) is a key for where the position of the corresponding portal is
        portals[(r1, c1)] = (r2, c2)
        portals[(r2, c2)] = (r1, c1)

def readOutput(): 
    global suggestedScore, horsePosition
    suggestedScore = int(input())

    for r in range(numRows):
        row = list(input().strip())
        outputGrid.append(row)
        for c in range(numCols):
            cell_type = outputGrid[r][c]
            if(cell_type == "H"):
                horsePosition = (r,c)
            outputGridDict[(r,c)] = cell_type
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
        verifiedScore+=pointsDict.get(outputGridDict.get(current)) # add score to verifiedScore
        neighbors = findNeighbors(outputGrid, current) # find the neighbors of the current cell
        for cell in neighbors: # for each neighbor
            if cell not in visited:
                stack.push(cell) # push neighbor to stack if not already visited
    print(f"DEBUG: suggested score: {suggestedScore}\nverified score: {verifiedScore}")
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
            if outputGrid[r][c] not in ("#", "W"): # skip walls and water
                neighbors.add((r,c))
    if(outputGridDict.get((cell[0], cell[1])) == "p"):
        neighbors.add(portals.get((cell[0], cell[1])))
    return neighbors

def verifyOutputFormat():
    usedWalls = 0
    for i in range(numRows):
        for j in range(numCols):
            input_cell = inputGridDict.get((i,j))
            output_cell = outputGridDict.get((i,j))
            if input_cell != output_cell:
                if input_cell == "." and output_cell == "W":
                    usedWalls+=1
                    continue
                elif input_cell == "W" and output_cell == ".":
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
    readInput()
    readOutput()
    isEscapeable = verifyNoEscape(outputGrid, horsePosition)
    isValidFormat = verifyOutputFormat()
    print(f"No escape routes? -> {isEscapeable}\nValid format? -> {isValidFormat}")
    