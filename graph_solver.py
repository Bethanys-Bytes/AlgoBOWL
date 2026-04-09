from utils.input_parser import FieldTiles, get_point_value, HorseField
from collections import deque
from argparse import ArgumentParser


class Tile:
    def __init__(self, tile_type: FieldTiles, row, col):
        self.tile_type = tile_type if tile_type != FieldTiles.WALL else FieldTiles.GRASS
        self.points = get_point_value(self.tile_type)
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
        self._hash = None
        self.boundary: set[Tile] = set()
        if boundary is None:
            self.validate_boundary()
        else:
            self.boundary = boundary

    def validate_boundary(self):
        self.boundary: set[Tile] = set()
        for tile in self.state:
            outside_state = tile.adjacencies - self.state
            if len(outside_state) > 0:
                self.boundary |= outside_state

    def include(self, include_tile: Tile, sink_tile: Tile):
        if include_tile not in self.boundary:
            print("INCLUDE ERROR")
            return
        added_to_state: set[Tile] = set()
        added_to_boundary: set[Tile] = set()
        stack = [include_tile]
        while stack:
            current = stack.pop()
            if current in self.state:
                self.boundary.discard(current)
                continue
            # Add to current state
            self.state.add(current)
            added_to_state.add(current)
            # Add adjacencies to new element to boundary
            new_boundary = current.adjacencies - self.state
            added_to_boundary |= new_boundary
            if sink_tile in new_boundary:
                return (added_to_state, added_to_boundary)
            self.boundary |= new_boundary
            self.boundary.discard(current)
            for next_tile in new_boundary:
                # If next_tile is not grass, cannot place a wall and more expansion is needed
                if next_tile.tile_type != FieldTiles.GRASS:
                    stack.append(next_tile)
                # If consuming the extended boundary tile does not increase the number of boundary tiles, consume
                boundary_adjacent = next_tile.adjacencies - self.state
                # If the boundary tile is adjacent to only one unknown tile
                if len(boundary_adjacent) == 1:
                    adjacent_next = next(iter(boundary_adjacent))
                    # If the tile the boundary is adjacent to is not the sink and is grass
                    if (
                        sink_tile != adjacent_next
                        and next(iter(boundary_adjacent)).tile_type == FieldTiles.GRASS
                    ):
                        stack.append(next_tile)
        return (added_to_state, added_to_boundary)

    def include_precompute(self, added_to_state, added_to_boundary):
        self.state |= added_to_state
        self.boundary |= added_to_boundary
        self.validate_boundary()

    def next_possible_expansions(self) -> int:
        return len(self.boundary)

    def get_points(self):
        if self.points is None:
            self.points = 0
            for tile in self.state:
                self.points += tile.points
        return self.points

    def __eq__(self, other: "SubField"):
        if isinstance(other, SubField):
            return self.state == other.state
        if isinstance(other, frozenset):
            return other == frozenset(self.state)
        return False

    def __hash__(self):
        if self._hash is None:
            self._hash = hash(frozenset(self.state))
        return self._hash


def file_record(record_function, tile_grid, grid_state):
    walls = [(wall_tile.row, wall_tile.col) for wall_tile in grid_state.boundary]
    record_function(f"{grid_state.get_points()}")
    for row_idx, row in enumerate(tile_grid):
        line = ""
        for col_idx, tile in enumerate(row):
            if (row_idx, col_idx) in walls:
                line += "W"
            else:
                line += tile.tile_type
        record_function(line)


def record_best(tile_grid: list[list[Tile]], wall_limit: int, best_solution: SubField, new_solution: SubField, filename=None):
    if len(new_solution.boundary) > wall_limit:
        return best_solution
    if not any(tile.tile_type == FieldTiles.GRASS for tile in new_solution.boundary):
        return best_solution
    if best_solution is None:
        return new_solution
    if new_solution.get_points() <= best_solution.get_points():
        return best_solution
    if filename:
        with open(filename, "w", encoding="utf-8") as f:
            file_record(lambda line: f.write(line + "\n"), tile_grid, new_solution)
    else:
        file_record(lambda line: print(line), tile_grid, new_solution)
        print()
    return new_solution


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("-fin", "--filename_in", default=None)
    parser.add_argument("-fout", "--filename_out", default=None)
    args = parser.parse_args()

    field_input = HorseField(args.filename_in)
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

    horse_tile: Tile = tile_grid[field_input.horse[0]][field_input.horse[1]]
    initial_state = SubField({horse_tile})
    subfields: set[SubField] = set([initial_state])
    expand_queue: deque[SubField] = deque([initial_state])
    boundary_expanded: dict[Tile : tuple[set[Tile], set[Tile]]] = {}
    best_solution: SubField = record_best(tile_grid, field_input.wallBudget, None, initial_state, args.filename_out)

    # TODO: Minimize duplicates
    duplicates = 0
    expansions = 0

    while expand_queue:
        expand_from = expand_queue.popleft()
        for boundary_tile in expand_from.boundary:
            expanded = SubField(set(expand_from.state), set(expand_from.boundary))
            if boundary_tile in boundary_expanded:
                if sink_tile in boundary_expanded[boundary_tile][1]:
                    continue  # Horse can escape if expanded here
                expansions += 1
                expanded.include_precompute(*boundary_expanded[boundary_tile])
            else:
                expansions += 1
                boundary_expanded[boundary_tile] = expanded.include(boundary_tile, sink_tile)
                if sink_tile in boundary_expanded[boundary_tile][1]:
                    continue  # Horse can escape if expanded here
            if expanded in subfields:
                duplicates += 1
                continue
            subfields.add(expanded)
            expand_queue.append(expanded)
            best_solution = record_best(tile_grid, field_input.wallBudget, best_solution, expanded, args.filename_out)

    print("Expansions: ", expansions)
    print("Duplicates: ", duplicates)
