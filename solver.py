from collections import deque
import sys # Necessary for BFS.
import random # Necessary for current implementation of neighbor generation.



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
