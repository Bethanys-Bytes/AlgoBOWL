from collections import deque
import sys # Necessary for BFS.
import random # Necessary for current implementation of neighbor generation.
import math # Necessary for simulated annealing.



# BFS helper. Defines how much each kind of tile is worth once enclosed.
def tile_score(tile):
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
  rows = len(grid)
  cols = len(grid[0])

  queue = deque([horsePosition])
  visited = set([horsePosition])

  score = 0
  reachesBoundary = False

  while queue:
    r, c = queue.popleft()
    score += tile_score(grid[r][c])

    # Boundary check. Can the horse escape?
    if r == 0 or r == rows - 1 or c == 0 or c == cols - 1:
      reachesBoundary = True
    
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
  return score, not reachesBoundary


# Energy function. Needs to be negative to represent that this is a maximization problem.
# (Positive energy function for simulated annealing is typically a minimization)
def energy(grid, walls, horsePosition, portals):
  score, valid = bfsScore(grid, walls, horsePosition, portals)
  if valid:
    return -score
  else:
    # Because the simulated annealing relies on a greedy algorithm, don't return if it's invalid, just give it a huge penalty.
    # Greedy will avoid it, and since there MUST be a valid solution for other groups' inputs, greedy must favor something else that is valid.
    return sys.maxsize - score


# Neighbor node generation for the greedy algorithm and the simulated annealing.
def generateNeighbor(grid, walls, wallBudget):
  newWalls = set(walls)
  if not newWalls:
    return newWalls
  
  # Randomly select a wall to move
  oldWall = random.choice(list(newWalls))
  newWalls.remove(oldWall)

  rows = len(grid)
  cols = len(grid[0])
  # Iterate through picking a random spot in the world.
  while True:
    r = random.randint(0, rows - 1)
    c = random.randint(0, cols - 1)

    # If the new spot is not amenable to placing a new wall, try again.
    if grid[r][c] != '.':
      continue

    # If the the new spot is already in the set to check, try again.
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
def simulatedAnnealing(grid, walls, horsePosition, portals, wallBudget, initialTemp=50.0, coolingRate=0.998, iterations=10000):

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


# # TEST IMPLEMENTATION OF A GREEDY HILL CLIMBING ALGORITHM -- THIS WORKS!!! IT IS HERE AS A BACKUP IN CASE ANNEALING STOPS WORKING!
# def greedySearch(grid, walls, horsePosition, portals, wallBudget, iterations=1000):
#   currentWalls = set(walls)
#   currentEnergy = energy(grid, currentWalls, horsePosition, portals)

#   bestWalls = set(currentWalls)
#   bestEnergy = currentEnergy

#   for _ in range(iterations):
#     candidateWalls = generateNeighbor(grid, currentWalls, wallBudget)
#     candidateEnergy = energy(grid, candidateWalls, horsePosition, portals)

#     # If a neighboring node has a lower energy, accept as the better state
#     if candidateEnergy < currentEnergy:
#       currentWalls = candidateWalls
#       currentEnergy = candidateEnergy

#       # If the new solution is the best solution, accept the new state.
#       if currentEnergy < bestEnergy:
#         bestWalls = set(currentWalls)
#         bestEnergy = currentEnergy

#   return bestWalls, bestEnergy


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
        walls.add((r, c))
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

  # Run the simulated annealing
  bestWalls, bestEnergy = simulatedAnnealing(grid, walls, horsePosition, portals, wallBudget)

  # Print the final score and output. The score needs to be negated because of the weird stuff with simulated annealing and its energy.
  # Check that the final solution is indeed a valid one.
  finalScore, isValid = bfsScore(grid, bestWalls, horsePosition, portals)
  if not isValid:
    # :(
    print("ERROR: final solution is invalid")
    sys.exit(1)

  print(finalScore)

  # Print the world state corresponding to this score
  finalGrid = buildOutputGrid(grid, bestWalls)
  for row in finalGrid:
    print("".join(row))

  # # Test prints: final energy should always be lower than initial energy. If it's not, something is wrong with the simulated annealing algorithm.
  # print("Best energy:", bestEnergy)
  # print("Best score:", -bestEnergy)
  # print("Initial:", energy(grid, walls, horsePosition, portals))
  # print("Final:", bestEnergy)