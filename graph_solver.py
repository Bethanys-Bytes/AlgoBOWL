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
    def __init__(self, current_state: set[Tile], edges: set[Tile] = None):
        self.state = current_state
        self.edge_tiles: set[Tile] = set()
        self.boundary: set[Tile] = set()
        for tile in self.state:
            outside_state = tile.adjacencies - self.state
            if len(outside_state) > 0:
                self.edge_tiles.add(tile)
                self.boundary |= outside_state

    def expand(self, sink_tile) -> set["SubField"]:
        expansions = set()
        for edge_tile in self.edge_tiles:
            adjacent_tiles = edge_tile.adjacencies - self.state
            # other_edges = self.edge_tiles - {edge_tile}
            for adjacent_tile in adjacent_tiles:
                if sink_tile in adjacent_tile.adjacencies:
                    continue
                current = adjacent_tile
                new_state = self.state.union([adjacent_tile])
                while True:
                    next_tiles = current.adjacencies - new_state
                    if len(next_tiles) != 1 or sink_tile in next_tiles:
                        break
                    current = next(iter(next_tiles))
                    new_state.add(current)
                expansions.add(SubField(new_state))
        return expansions

    def next_possible_expansions(self) -> int:
        return len(self.boundary)

    def is_subset(self, *others: "SubField"):
        for other in others:
            if self.state.issubset(other.state):
                return (self.boundary - other.state).issubset(other.boundary)
        return False

    def __eq__(self, other):
        return self.state == other.state

    def __hash__(self):
        return hash(frozenset(self.state))

    def display(self):
        min_x = None
        max_x = None
        min_y = None
        max_y = None
        for tile in self.state:
            if min_x == None or tile.row < min_x:
                min_x = tile.row
            if max_x == None or tile.row > max_x:
                max_x = tile.row
            if min_y == None or tile.col < min_y:
                min_y = tile.col
            if max_y == None or tile.col > max_y:
                max_y = tile.col
        for tile in self.boundary:
            if min_x == None or tile.row < min_x:
                min_x = tile.row
            if max_x == None or tile.row > max_x:
                max_x = tile.row
            if min_y == None or tile.col < min_y:
                min_y = tile.col
            if max_y == None or tile.col > max_y:
                max_y = tile.col
        sub_grid = [["#" for _ in range(max_y + 1)] for _ in range(max_x + 1)]
        for tile in self.state:
            sub_grid[tile.row][tile.col] = tile.tile_type
        for tile in self.boundary:
            sub_grid[tile.row][tile.col] = "W"
        for i in range(max_x + 1):
            for j in range(max_y + 1):
                if min_x <= i <= max_x and min_y <= j <= max_y and sub_grid[i][j] == "":
                    sub_grid[i][j] = "#"
        for row in sub_grid:
            if row:
                print("".join(row))
        print()


if __name__ == "__main__":
    field_input = HorseField()
    sink_tile = Tile(
        FieldTiles.GRASS, -1, -1
    )  # Make an adjacent tile to all edges to track if escape is possible
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
                if 0 <= adjacent_row < len(tile_grid) and 0 <= adjacent_col < len(
                    tile_grid[adjacent_row]
                ):
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
        tile_grid[portal1_row][portal1_col].add_adjacency(
            tile_grid[portal2_row][portal2_col]
        )
        tile_grid[portal2_row][portal2_col].add_adjacency(
            tile_grid[portal1_row][portal1_col]
        )

    subfields: set[SubField] = set()
    valid_solutions: set[SubField] = set()
    expand_queue: deque[SubField] = deque()
    initial_state = SubField({tile_grid[field_input.horse[0]][field_input.horse[1]]})
    expand_queue.append(initial_state)
    subfields.add(initial_state)
    if initial_state.next_possible_expansions() <= field_input.wallBudget:
        valid_solutions.add(initial_state)
    while len(expand_queue) > 0:
        expand_from = expand_queue.pop()
        possible_expansions = expand_from.expand(sink_tile)
        for possible_expansion in possible_expansions:
            if possible_expansion in subfields or possible_expansion.is_subset(
                *subfields
            ):
                continue
            subfields.add(possible_expansion)
            if sink_tile in possible_expansion.boundary:
                continue
            expand_queue.append(possible_expansion)
            if possible_expansion.next_possible_expansions() > field_input.wallBudget:
                continue
            if all(
                [
                    tile.tile_type == FieldTiles.GRASS
                    for tile in possible_expansion.boundary
                ]
            ):
                valid_solutions.add(possible_expansion)
    # Display possible valid outputs
    # TODO: Verify that this gets ALL possible solutions
    for subfield in valid_solutions:
        subfield.display()
