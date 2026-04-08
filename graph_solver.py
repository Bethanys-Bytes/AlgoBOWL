from utils.input_parser import FieldTiles, get_point_value, HorseField
from collections import deque


class Tile:
    def __init__(self, tile_type: FieldTiles, row, col):
        self.tile_type = tile_type
        self.row: int = row
        self.col: int = col
        self.adjacencies: set[Tile] = set()

    def add_adjacency(self, adjacent_tile: "Tile"):
        if self.tile_type in (FieldTiles.WALL, FieldTiles.WATER):
            return
        if adjacent_tile.tile_type in (FieldTiles.WALL, FieldTiles.WATER):
            return
        self.adjacencies.add(adjacent_tile)

    def __str__(self):
        return f"{self.tile_type}:({self.row},{self.col})"

    def __repr__(self):
        return f"{self.tile_type}:({self.row},{self.col})"


class SubField:
    def __init__(self, current_state: set[Tile], boundary: set[Tile] = None):
        self.state = current_state
        self.points = None
        if boundary:
            self.boundary = boundary
            return
        self.boundary: set[Tile] = set()
        for tile in self.state:
            outside_state = tile.adjacencies - self.state
            if len(outside_state) > 0:
                self.boundary |= outside_state

    def include(self, include_tile: Tile, sink_tile: Tile) -> bool:
        if include_tile not in self.boundary:
            print("INCLUDE ERROR")
            return
        stack = [include_tile]
        while stack:
            current = stack.pop()
            if current in self.state:
                self.boundary.remove(current)
                continue
            # Add to current state
            self.state.add(current)
            # Add adjacencies to new element to boundary
            new_boundary = current.adjacencies - self.state
            if sink_tile in new_boundary:
                return False
            self.boundary |= new_boundary
            self.boundary.remove(current)
            for next_tile in new_boundary:
                # If next_tile is not grass, cannot place a wall and more expansion is needed
                if next_tile.tile_type != FieldTiles.GRASS:
                    stack.append(next_tile)
                # TODO: If consuming the extended boundary tile does not increase the number of boundary tiles, consume
                # boundary_adjacent = next_tile.adjacencies - self.state
                # # If the boundary tile is adjacent to only one unknown tile
                # # and the following tile
                # if len(boundary_adjacent) == 1 and next(iter(boundary_adjacent)).tile_type == FieldTiles.GRASS:
                #     stack.append(next_tile)
        return True

    def next_possible_expansions(self) -> int:
        return len(self.boundary)

    def is_subset(self, *others: "SubField"):
        for other in others:
            if self.state.issubset(other.state):
                if len(self.boundary - other.state) == 1:
                    return True
        return False

    def get_points(self):
        if self.points == None:
            self.points = 0
            for tile in self.state:
                self.points += get_point_value(tile.tile_type)
        return self.points

    def __eq__(self, other: 'SubField'):
        return self.state == other.state

    def __hash__(self):
        return hash(frozenset(self.state))

if __name__ == "__main__":
    field_input = HorseField()
    sink_tile = Tile(FieldTiles.GRASS, -1, -1)  # Make an adjacent tile to all edges to track if escape is possible
    tile_grid: list[list[Tile]] = []
    for row_idx, row in enumerate(field_input.grid):
        tile_grid.append([])
        for col_idx, tile in enumerate(row):
            new_tile = Tile(FieldTiles(tile), row_idx, col_idx)
            adjacency_list = [
                (row_idx + 1, col_idx),
                (row_idx - 1, col_idx),
                (row_idx, col_idx + 1),
                (row_idx, col_idx - 1),
            ]
            for adjacent_row, adjacent_col in adjacency_list:
                if 0 <= adjacent_row < len(tile_grid) and 0 <= adjacent_col < len(tile_grid[adjacent_row]):
                    new_tile.add_adjacency(tile_grid[adjacent_row][adjacent_col])
                    tile_grid[adjacent_row][adjacent_col].add_adjacency(new_tile)
                elif adjacent_row < 0 or field_input.row_count <= adjacent_row:
                    new_tile.add_adjacency(sink_tile)
                elif adjacent_col < 0 or field_input.col_count <= adjacent_col:
                    new_tile.add_adjacency(sink_tile)
            tile_grid[row_idx].append(new_tile)
    for portal_coords, connected_portal in field_input.portals.items():
        portal1_row, portal1_col = portal_coords
        portal2_row, portal2_col = connected_portal
        tile_grid[portal1_row][portal1_col].add_adjacency(tile_grid[portal2_row][portal2_col])
        tile_grid[portal2_row][portal2_col].add_adjacency(tile_grid[portal1_row][portal1_col])

    subfields: set[SubField] = set()
    # valid_solutions: set[SubField] = set()
    expand_queue: deque[SubField] = deque()
    initial_state = SubField({tile_grid[field_input.horse[0]][field_input.horse[1]]})
    best_solution: SubField = initial_state
    expand_queue.append(initial_state)
    subfields.add(initial_state)
    # if initial_state.next_possible_expansions() <= field_input.wallBudget:
    #     valid_solutions.add(initial_state)
    expansions = 0
    duplicates = 0 #TODO: Minimize duplicates

    while len(expand_queue) > 0:
        expand_from = expand_queue.popleft()
        # if expand_from.is_subset(*subfields): # TODO: Is this valid?
        #     continue
        # field_input.display([(wall_tile.row, wall_tile.col) for wall_tile in expand_from.boundary])
        for boundary_tile in expand_from.boundary:
            expansions += 1
            expanded = SubField(set(expand_from.state), set(expand_from.boundary))
            if not expanded.include(boundary_tile, sink_tile):
                continue # Horse can escape if expanded here
            # field_input.display([(wall_tile.row, wall_tile.col) for wall_tile in expanded.boundary])
            if expanded in subfields:
                # print("DUP")
                duplicates += 1
                continue
            subfields.add(expanded)
            expand_queue.append(expanded)
            if expanded.next_possible_expansions() > field_input.wallBudget:
                continue
            if all([tile.tile_type == FieldTiles.GRASS for tile in expanded.boundary]):
                # valid_solutions.add(expanded)
                if expanded.get_points() > best_solution.get_points():
                    best_solution = expanded
    # print("Expansions: ", expansions)
    # print("Duplicates: ", duplicates)
    # Display possible valid outputs
    # TODO: Verify that this gets ALL possible solutions
    # for subfield in valid_solutions:
    #     field_input.display([(wall_tile.row, wall_tile.col) for wall_tile in subfield.boundary])
    #     print()
    #     subfield.display()
    print(best_solution.get_points())
    field_input.display([(wall_tile.row, wall_tile.col) for wall_tile in best_solution.boundary])
