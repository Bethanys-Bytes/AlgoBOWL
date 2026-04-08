from collections import deque
import sys # Necessary for BFS.
import random # Necessary for current implementation of neighbor generation.
import math # Necessary for simulated annealing.



# BFS helper. Defines how much each kind of tile is worth once enclosed.
def tileScore(tile):
  if tile == '.':
    return 1
  elif tile == 'H':
    return 1
  elif tile == 'a':
    return 11
  elif tile == 'b':
    return -4
  elif tile == 'c':
    return 4
  elif tile == 'p':
    return 1
  return 0


# BFS function. Answers "Given the current state of the world, can the horse escape?" and "What is the score of the current enclosure?"
def bfsScore(grid, walls, horsePosition, portals):
  boundaryTilesReached = 0
  rows = len(grid)
  cols = len(grid[0])

  queue = deque([horsePosition])
  visited = set([horsePosition])

  score = 0
  reachesBoundary = False
  while queue:
    r, c = queue.popleft()
    score += tileScore(grid[r][c])

    # Boundary check. Can the horse escape?
    if r == 0 or r == rows - 1 or c == 0 or c == cols - 1:
      boundaryTilesReached+=1
    
    # Check for a portal at the current position. Treat it as an edge in the graph for possible traversal.
    if (r, c) in portals:
      pr, pc = portals[(r, c)]
      if (pr, pc) not in visited and (pr, pc) not in walls:
        visited.add((pr, pc))
        queue.append((pr, pc))
    
    # Check all four surrounding directions
    for dr, dc in [(-1,0), (1,0), (0,-1), (0,1)]:
      nr, nc = r + dr, c + dc
      # Check that each new tile is within bounds
      if 0 <= nr < rows and 0 <= nc < cols:
        # Check that it's unvisited
        if (nr, nc) in visited:
          continue
        # Check that it's not a wall. If a horse runs through a wall, god help us.
        if (nr, nc) in walls:
          continue
        # Check that it's not a water tile. Horses can't move through water
        if grid[nr][nc] == '#':
          continue
        # Else the horse is able to move to the new tile, so add it
        visited.add((nr, nc))
        queue.append((nr, nc))
  return score, boundaryTilesReached == 0, boundaryTilesReached


# Energy function. Needs to be negative to represent that this is a maximization problem.
# (Positive energy function for simulated annealing is a minimization)
def energy(grid, walls, horsePosition, portals):
  # Update the state of the world
  #currentGrid = buildOutputGrid(grid, walls)
  #score, valid = bfsScore(currentGrid, walls, horsePosition, portals)
  score, valid, boundaryTilesReached = bfsScore(grid, walls, horsePosition, portals)
  if valid:
    return -score
  else:
    # Because the simulated annealing relies on a greedy algorithm, don't return if it's invalid, just give it a huge penalty.
    # Greedy will avoid it, and since there MUST be a valid solution for other groups' inputs, greedy must favor something else that is valid.
    return 1000 * boundaryTilesReached - score


# Neighbor node generation for the greedy algorithm and the simulated annealing.
# Neighbor generation is currently made by moving a wall to a random spot. We should probably consider finding a better way to add neighbor nodes
# Might be better if we try moving walls by one in each direction? It's worth a shot.
def generateNeighbor(grid, walls, wallBudget):
  newWalls = set(walls)

  # At any point in time, we can add a new wall if under budget, remove a wall, or move an existing wall.
  probabilities = [1]
  possibleMoves = ["move"]
  numM = 1
  if len(newWalls) < wallBudget:
    possibleMoves.append("add")
    numM += 1
  if len(newWalls) > 0:
    possibleMoves.append("remove")
    numM += 1

  # Probabilities of picking (move, add, remove). Probabilities are tunable.
  # Currently favor moving a wall most of the time.
  if numM == 2:
    # Either no walls left in budget or no walls on map.
    probabilities = [0.4, 0.6]
  elif numM == 3:
    # Still walls left in budget and 1 or more walls on map.
    probabilities = [0.2, 0.5, 0.3]

  moveType = "move"

  rand = random.random()
  for i in range(numM):
    if rand < probabilities[numM - i - 1]:
      moveType = possibleMoves[i]

  # If using probabilities becomes more optimal, comment out this line
  # moveType = random.choice(possibleMoves)

  if moveType == "add":
    # Either chooses to add to a chokepoint tile or choose a random tile.
    # % Chance is tunable.
    nextType = random.random()
    if nextType < 0.5:
      # Pick a random new tile for the wall.
      rows = len(grid)
      cols = len(grid[0])

      while True:
        r = random.randint(0, rows - 1)
        c = random.randint(0, cols - 1)

        if grid[r][c] != '.':
          continue

        if (r, c) in newWalls:
          continue

        newWalls.add((r, c))
        break
    # Select a chokepoint tile to add it
    else:
      while True:
        choke = random.choice(chokePoints)
        r = choke[0]
        c = choke[1]

        if grid[r][c] != '.':
          continue

        if (r, c) in newWalls:
          continue

        newWalls.add((r, c))
        break

  elif moveType == "remove":
    wallToRemove = random.choice(list(newWalls))
    newWalls.remove(wallToRemove)

  else:
    if not newWalls:
      return newWalls

    oldWall = random.choice(list(newWalls))
    newWalls.remove(oldWall)

    # Either chooses to move to a neighboring tile or choose a random tile.
    # % Chance is tunable.
    nextType = random.random()
    if nextType < 0.35:
      # Pick a random new tile for the wall.
      rows = len(grid)
      cols = len(grid[0])

      while True:
        r = random.randint(0, rows - 1)
        c = random.randint(0, cols - 1)

        if grid[r][c] != '.':
          continue

        if (r, c) in newWalls:
          continue

        newWalls.add((r, c))
        break
    # Select a chokepoint to move to
    elif nextType < 0.7:
      while True:
        choke = random.choice(chokePoints)
        r = choke[0]
        c = choke[1]

        if grid[r][c] != '.':
          continue

        if (r, c) in newWalls:
          continue

        newWalls.add((r, c))
        break
    else:
      # Else pick a tile next to itself.
      while True:
        rd = (oldWall[0], oldWall[0] - 1, oldWall[0] + 1)
        cd = (oldWall[1], oldWall[1] - 1, oldWall[1] + 1)
        r = random.choice(rd)
        c = random.choice(cd)

        if r < 0 or c < 0 or r >= numRow or c >= numCol:
          continue

        if grid[r][c] != '.':
          continue

        if (r, c) in newWalls:
          continue

        newWalls.add((r, c))
        break

  # Return all the new possibilities for neighboring nodes
  return newWalls


# Run a greedy search to determine the best places to put the walls.
# Limit the number of iterations so that the algorithm actually finishes. We can increase or decrease the number as needed.
# The term "energy" refers to the score of a particular solution in simulated annealing. It may seem backwards, but we're looking for a minimum energy.
# "Temperature" refers to the current acceptance. High temp means more exploration and accepts "worse" local decision. Low temp means being more greedy and only accepting the "best" local decisions. Initially, we'll start high to try and escape local optima and search for global optima.
# initialTemp, coolingRate, AND iterations ARE TUNABLE VARIABLES!!! THE REST ARE NOT!!!
def simulatedAnnealing(grid, walls, horsePosition, portals, wallBudget, initialTemp=80.0, coolingRate=0.9995, iterations=1000000):

  currentWalls = set(walls)
  currentEnergy = energy(grid, currentWalls, horsePosition, portals)

  bestWalls = set(currentWalls)
  bestEnergy = currentEnergy
  temperature = initialTemp

  for _ in range(iterations):
    candidateWalls = generateNeighbor(grid, currentWalls, wallBudget)
    candidateEnergy = energy(grid, candidateWalls, horsePosition, portals)

    # Determine how much better/worse the neighboring node is
    delta = candidateEnergy - currentEnergy

    # ALWAYS accept if it is a better state
    if delta < 0:
      currentWalls = candidateWalls
      currentEnergy = candidateEnergy
    
    # Otherwise, accept the "worse" state with probability P
    else:
      probability = math.exp(-delta / temperature)
      if random.random() < probability:
        currentWalls = candidateWalls
        currentEnergy = candidateEnergy
    
    # Keep track of the best
    if currentEnergy < bestEnergy:
      bestWalls = set(currentWalls)
      bestEnergy = currentEnergy
    
    # As we get further along, it's more likely that we've already escaped local optima, so don't explore as much. 
    # But never go all the way down to 0
    temperature *= coolingRate
    if temperature < 0.01:
      temperature = 0.01

  return bestWalls, bestEnergy


# Output function. There is NO algorithm logic in this. If something stops working that's not related to printing outputs, don't change this shit! 
def buildOutputGrid(grid, finalWalls):
  rows = len(grid)
  cols = len(grid[0])

  # We need a new grid, but everything except select "." and "W" tiles should remain the same from the old grid.
  outputGrid = [row[:] for row in grid]

  for r in range(rows):
    for c in range(cols):
      # Clear all existing walls back to grass tiles
      if outputGrid[r][c] == 'W':
        outputGrid[r][c] = '.'
  
  # Put the new wall state into the output grid
  for r, c in finalWalls:
    if outputGrid[r][c] == '.':
      outputGrid[r][c] = 'W'

  return outputGrid

if __name__ == "__main__":
  wallBudget = int(input())
  numRow, numCol = map(int, input().split())

  # Create the data structures
  grid = [] # State of the world
  walls = set() # Walls and their positions
  horsePosition = None # HORSE 
  
  for r in range(numRow):
    row = list(input().strip())
    # Put rows into the global grid
    grid.append(row)
    for c in range(numCol):
      # Keep track of the wall positions
      if row[c] == 'W':
        row[c] = '.'
        walls.add((r,c))
        #walls.add((r, c))
      # and where the horse is
      elif row[c] == 'H':
        horsePosition = (r, c)

  # Store portal mappings
  numPortals = int(input())
  portals = {}

  for _ in range(numPortals):
    r1, c1, r2, c2 = map(int, input().split())
    # A (row, col) is a key for where the position of the corresponding portal is
    portals[(r1, c1)] = (r2, c2)
    portals[(r2, c2)] = (r1, c1)
  
  chokePoints = set() # Tiles on the map that only have one spot between two tiles of water.
  # Check for and keep track of chokepoints caused by water.
  # Chokepoints are important because they note spots where it is potentially very cheap to put a wall to enclose an area.
  for r in range(1, numRow - 1):
    print(f"Still working...{r}")
    for c in range(1, numCol - 1):
      if grid[r][c] != "." and grid[r][c] != "W":
        continue
      # Water in upper left corner
      if grid[r - 1][c - 1] == "#":
        if grid[r + 1][c - 1] == "#" or grid[r + 1][c] == "#" or grid[r + 1][c + 1] == "#" or grid[r - 1][c + 1] == "#" or grid[r][c + 1] == "#":
          chokePoints.add((r, c))
      # Water in top middle
      if grid[r - 1][c] == "#":
        if grid[r + 1][c - 1] == "#" or grid[r + 1][c] == "#" or grid[r + 1][c + 1] == "#" or grid[r][c - 1] == "#" or grid[r][c + 1] == "#":
          chokePoints.add((r, c))
      # Water in upper right corner
      if grid[r - 1][c + 1] == "#":
        if grid[r + 1][c - 1] == "#" or grid[r + 1][c] == "#" or grid[r + 1][c + 1] == "#" or grid[r - 1][c - 1] == "#" or grid[r][c - 1] == "#":
          chokePoints.add((r, c))
      # Water in middle left
      if grid[r][c - 1] == "#":
        if grid[r - 1][c] == "#" or grid[r - 1][c + 1] == "#" or grid[r + 1][c] == "#" or grid[r + 1][c + 1] == "#" or grid[r][c + 1] == "#":
          chokePoints.add((r, c))
      # Water in middle right
      if grid[r][c + 1] == "#":
        if grid[r - 1][c] == "#" or grid[r - 1][c - 1] == "#" or grid[r + 1][c] == "#" or grid[r + 1][c - 1] == "#" or grid[r][c - 1] == "#":
          chokePoints.add((r, c))
      # Water in bottom left corner
      if grid[r + 1][c - 1] == "#":
        if grid[r + 1][c + 1] == "#" or grid[r - 1][c + 1] == "#" or grid[r][c + 1] == "#" or grid[r - 1][c - 1] == "#" or grid[r - 1][c] == "#":
          chokePoints.add((r, c))
      # Water in bottom middle
      if grid[r + 1][c] == "#":
        if grid[r][c + 1] == "#" or grid[r][c - 1] == "#" or grid[r - 1][c - 1] == "#" or grid[r - 1][c] == "#" or grid[r - 1][c + 1] == "#":
          chokePoints.add((r, c))
      # Water in bottom right corner
      if grid[r + 1][c + 1] == "#":
        if grid[r + 1][c - 1] == "#" or grid[r - 1][c - 1] == "#" or grid[r][c - 1] == "#" or grid[r - 1][c + 1] == "#" or grid[r - 1][c] == "#":
          chokePoints.add((r, c))
  chokePoints = list(chokePoints)
  print("Exitted Loops.")

  # Run the simulated annealing
  # Do it with five restarts in order to ensure we got the best possible outcome.
  # Number of restarts is tunable.
  numStarts = 3
  bestWalls = ()
  bestEnergy = sys.maxsize
  for _ in range(numStarts):
    print("Beginning SA!")
    scoredWalls, scoredEnergy = simulatedAnnealing(grid, walls, horsePosition, portals, wallBudget)
    print("SA COMPLETE!")
    if scoredEnergy < bestEnergy:
      bestWalls = scoredWalls
      bestEnergy = scoredEnergy

  # Print the final score and output. The score needs to be negated because of the weird stuff with simulated annealing and its energy.
  # Check that the final solution is indeed a valid one.
  # Must build the final world state before running final BFS.
  finalGrid = buildOutputGrid(grid, bestWalls)
  finalScore, isValid, _ = bfsScore(finalGrid, bestWalls, horsePosition, portals)
  if not isValid:
    print(":(")
    sys.exit(1)

  print(finalScore)

  # Print the world state corresponding to the best score
  for row in finalGrid:
    print("".join(row))