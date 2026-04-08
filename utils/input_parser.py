from enum import StrEnum

class FieldTiles(StrEnum):
    HORSE   = "H"
    WALL    = "W"
    WATER   = "#"
    CHERRY  = "c"
    APPLE   = "a"
    BEES    = "b"
    PORTAL  = "p"
    GRASS   = "."

def get_point_value(tile: FieldTiles) -> int:
    if tile in (FieldTiles.GRASS, FieldTiles.HORSE, FieldTiles.PORTAL):
        return 1
    elif tile in (FieldTiles.WALL, FieldTiles.WATER):
        return 0
    elif tile == FieldTiles.APPLE:
        return 11
    elif tile == FieldTiles.CHERRY:
        return 4
    elif tile == FieldTiles.BEES:
        return -4
    print("Invalid Tile for Point Assignment", tile)
    return 0

class HorseField:
  def __init__(self):
    self.wallBudget = int(input())
    self.row_count, self.col_count = map(int, input().split())
    self.grid = []
    self.walls = set()
    self.portals = {}
    self.horse = None
    self.valid = True
    for row_idx in range(self.row_count):
        row = list(input().strip())
        # Put rows into the global grid
        self.grid.append(row)
        for col_idx in range(self.col_count):
            current_cell = (row_idx, col_idx)
            # Keep track of the wall positions
            if row[col_idx] == FieldTiles.WALL:
                self.walls.add(current_cell)
            # and where the horse is
            elif row[col_idx] == FieldTiles.HORSE:
                self.horse = current_cell
    # Store portal mappings
    numPortals = int(input())
    for _ in range(numPortals):
        r1, c1, r2, c2 = map(int, input().split())
        p1 = (r1, c1)
        p2 = (r2, c2)
        # A (row, col) is a key for where the position of the corresponding portal is
        self.portals[p1] = p2
        self.portals[p2] = p1
    if len(self.grid) != self.row_count or len(self.grid[0]) != self.col_count:
       print("Invalid Input (grid dimension)")
       self.valid = False
    for portal_row, portal_col in self.portals.keys():
       if FieldTiles.PORTAL != self.grid[portal_row][portal_col]:
            print("Invalid Input (portal placement)")
            self.valid = False