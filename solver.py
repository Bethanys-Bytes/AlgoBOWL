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