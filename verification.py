from utils import Stack
# GLOBALS
grid = [] # State of the output-world
gridDict = {} # Dictionary of all grid positions for verifying score
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
"""
readOutput() parses input similar how input is parsed in solver.py.
It also creates a key,value pair in gridDict in the form of (cell, cell_type)
where we can easily look up what a cell is (apples, bees, wall, water, etc.)
"""
def readOutput(): 
    global suggestedScore, numRows, numCols, horsePosition
    suggestedScore = int(input())
    numRows, numCols = map(int, input().split())

    for r in range(numRows):
        row = list(input().strip())
        grid.append(row)
        for c in range(numCols):
            cell_type = grid[r][c]
            if(type == "H"):
                horsePosition = (r,c)
            gridDict[(r,c)] = cell_type

"""
verifyOutput will be in charge of the heavy lifting for verification. It will run a modified DFS to check if the 
perimeter is accessible in the output. It will also be in charge of making sure that no new walls
were placed on cells that are also water, pre-placed walls, bees, apples, cherries, portals, horse.
"""
def verifyOutput(grid, horsePosition):
    verifiedScore = 0 # initialize the score which we will check against the suggestedScore after DFS has finished
    stack = Stack()
    visited = set()
    stack.push(horsePosition) # push horsePosition (start) onto stack
    while not stack.is_empty(): 
        current = stack.pop() # get the cell at the top of stack
        if current[0] == 0 or current[0] == numRows - 1 or \
            current[1] == 0 or current[1] == numCols - 1: # check if current cell is a perimeter grass cell, if it is output is invalid
            return False
        if current in visited: # skip neighbor if we already visited
            continue
        visited.add(current)
        verifiedScore+=pointsDict.get(gridDict.get(current)) # add score to verifiedScore
        neighbors = findNeighbors(grid, current) # find the neighbors of the current cell
        for cell in neighbors: # for each neighbor
            if cell not in visited:
                stack.push(cell) # push neighbor to stack if not already visited
    if suggestedScore == verifiedScore: # if both our calculated score and output suggestedScore are the same AND DFS completed, then the format of the output is valid
        return True
    return False
"""
findNeighbors is a helper function to finding grass cells adjacent to a given cell, it returns a list of all adjacent grass cells
"""
def findNeighbors(grid, cell):
    neighbors = set()
    directions = [(-1, 0), (1,0), (0, -1), (0,1)] # UP, DOWN, LEFT, RIGHT
    for dr, dc in directions:
        r, c = cell[0] + dr, cell[1] + dc
        if 0 <= r < numRows and 0 <= c < numCols:
            if grid[r][c] not in ("#", "W"): # skip walls and water
                neighbors.add((r,c))
    return neighbors

        
if __name__ == "__main__":
    readOutput()
    isValid = verifyOutput(grid, horsePosition)
    print(isValid)