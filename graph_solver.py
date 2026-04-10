from utils.input_parser import FieldTiles, get_point_value, HorseField
from collections import deque
from argparse import ArgumentParser
import re


class Tile:
    def __init__(self, tile_type: FieldTiles, row, col):
        self.tile_type = tile_type if tile_type != FieldTiles.WALL else FieldTiles.GRASS
        self.points = None if tile_type == FieldTiles.EDGE else get_point_value(self.tile_type)
        self.row: int = row
        self.col: int = col
        self.adjacencies: set[Tile] = set()

    def add_adjacency(self, adjacent_tile: "Tile"):
        if self.tile_type in (FieldTiles.WALL, FieldTiles.WATER):
            return
        if adjacent_tile.tile_type in (FieldTiles.WALL, FieldTiles.WATER):
            return
        self.adjacencies.add(adjacent_tile)

    def __hash__(self):
        return hash((self.row, self.col))

    def __eq__(self, other):
        return (self.row, self.col) == (other.row, other.col)

    def __str__(self):
        return f"{self.tile_type}:({self.row},{self.col})"

    def __repr__(self):
        return f"{self.tile_type}:({self.row},{self.col})"

# Make an adjacent tile to all edges to track if escape is possible
SINK_TILE = Tile(FieldTiles.EDGE, -1, -1)
TILE_GRID: list[list[Tile]] = []

class SubField:
    def __init__(self, current_state: set[Tile]):
        self.state = current_state
        self.points = None
        self.boundary: set[Tile] = set()
        self.known: set[Tile] = set()
        self.build_boundary()

    def build_boundary(self):
        self.known: set[Tile] = set(self.state)
        self.boundary: set[Tile] = set()
        for tile in self.state:
            self.boundary.update(tile.adjacencies - self.state)
        self.known = self.state|self.boundary

    def validate_boundary(self):
        expand_required: set[Tile] = set()
        for tile in self.boundary:
            if tile.tile_type != FieldTiles.GRASS:
                expand_required.add(tile)
                continue
            boundary_adjacent = tile.adjacencies-self.known
            if len(boundary_adjacent) == 0:
                expand_required.add(tile)
            elif len(boundary_adjacent) == 1 and all(boundary_adj.tile_type == FieldTiles.GRASS for boundary_adj in boundary_adjacent):
                expand_required.add(tile)
        return expand_required

    def boundary_to_state(self, tile: Tile):
        adjacencies = tile.adjacencies - self.known
        self.state.add(tile)
        self.boundary.discard(tile)
        for adjacent_tile in adjacencies:
            self.known.add(adjacent_tile)
            self.boundary.add(adjacent_tile)

    def include(self, include_tile: Tile) -> bool:
        check_expand = deque([include_tile])
        while check_expand:
            current = check_expand.popleft()
            if current == SINK_TILE:
                return False
            if current in self.state:
                self.boundary.discard(current)
                continue
            # Add adjacencies to new element to boundary
            self.boundary_to_state(current)
            check_expand.extend(self.validate_boundary())
        return True

    def next_possible_expansions(self) -> int:
        return len(self.boundary)

    def get_points(self):
        if self.points is None:
            self.points = 0
            for tile in self.state:
                self.points += tile.points
        return self.points

    def copy(self) -> "SubField":
        new = SubField.__new__(SubField)
        new.state = set(self.state)
        new.boundary = set(self.boundary)
        new.known = set(self.known)
        new.points = None
        return new

    def __eq__(self, other: "SubField"):
        if isinstance(other, SubField):
            return self.state == other.state and self.known == other.known
        if isinstance(other, frozenset):
            return other == frozenset(self.known)
        return False

def file_record(record_function, grid_state):
    walls = [(wall_tile.row, wall_tile.col) for wall_tile in grid_state.boundary]
    record_function(f"{grid_state.get_points()}")
    for row_idx, row in enumerate(TILE_GRID):
        line = ""
        for col_idx, tile in enumerate(row):
            if (row_idx, col_idx) in walls:
                line += "W"
            else:
                line += tile.tile_type
        record_function(line)


def record_best(wall_limit: int, best_solution: SubField, new_solution: SubField, filename=None):
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
            file_record(lambda line: f.write(line + "\n"), new_solution)
    else:
        file_record(lambda line: print(line), new_solution)
        print()
    return new_solution


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("-fin", "--filename_in", default=None)
    parser.add_argument("-fout", "--filename_out", default=None)
    args = parser.parse_args()

    field_input = HorseField(args.filename_in)
    for row_idx, row in enumerate(field_input.grid):
        TILE_GRID.append([])
        for col_idx, tile in enumerate(row):
            new_tile = Tile(FieldTiles(tile), row_idx, col_idx)
            adjacency_list = [
                (row_idx + 1, col_idx),
                (row_idx - 1, col_idx),
                (row_idx, col_idx + 1),
                (row_idx, col_idx - 1),
            ]
            for adjacent_row, adjacent_col in adjacency_list:
                if 0 <= adjacent_row < len(TILE_GRID) and 0 <= adjacent_col < len(TILE_GRID[adjacent_row]):
                    new_tile.add_adjacency(TILE_GRID[adjacent_row][adjacent_col])
                    TILE_GRID[adjacent_row][adjacent_col].add_adjacency(new_tile)
                elif adjacent_row < 0 or field_input.row_count <= adjacent_row:
                    new_tile.add_adjacency(SINK_TILE)
                elif adjacent_col < 0 or field_input.col_count <= adjacent_col:
                    new_tile.add_adjacency(SINK_TILE)
            TILE_GRID[row_idx].append(new_tile)
    for portal_coords, connected_portal in field_input.portals.items():
        portal1_row, portal1_col = portal_coords
        portal2_row, portal2_col = connected_portal
        TILE_GRID[portal1_row][portal1_col].add_adjacency(TILE_GRID[portal2_row][portal2_col])
        TILE_GRID[portal2_row][portal2_col].add_adjacency(TILE_GRID[portal1_row][portal1_col])

    horse_tile: Tile = TILE_GRID[field_input.horse[0]][field_input.horse[1]]
    initial_state = SubField({horse_tile})
    subfields: list[SubField] = [initial_state]
    subfields_by_size: dict[int:list[SubField]] = {len(initial_state.boundary): [initial_state]}
    expand_queue: deque[SubField] = deque([initial_state])
    best_solution: SubField = record_best(field_input.wallBudget, None, initial_state, args.filename_out)

    # TODO: Minimize duplicates
    duplicates = 0
    expansions = 0
    synonyms = 0

    while expand_queue:
        expand_from = expand_queue.popleft()
        for boundary_tile in expand_from.boundary:
            expanded = expand_from.copy()
            expansions += 1
            if not expanded.include(boundary_tile):
                continue  # Horse can escape if expanded here
            # Determine if this field should be tracked
            track = True
            subsets = []
            if len(expanded.boundary) not in subfields_by_size:
                subfields_by_size[len(expanded.boundary)] = []
            for idx, subfield in enumerate(subfields_by_size[len(expanded.boundary)]):
                # If expanded has been seen before, don't track
                if expanded == subfield:
                    duplicates += 1
                    track = False
                    break
                # expanded.known is a subset of the known subfield's known, don't track
                if expanded.known.issubset(subfield.known):
                    track = False
                    synonyms += 1
                # the known subfield's known is a subset of expanded.known, track
                if subfield.known.issubset(expanded.known):
                    subsets.append(idx)
                    synonyms += 1
            # Don't track subfields that are subsets of other subfields
            for i in range(len(subfields_by_size[len(expanded.boundary)])-1, -1, -1):
                subfields_by_size[len(expanded.boundary)].pop(i)
            if not track:
                continue
            subfields_by_size[len(expanded.boundary)].append(expanded)
            expand_queue.append(expanded)
            best_solution = record_best(field_input.wallBudget, best_solution, expanded, args.filename_out)
    if args.filename_in:
        group_number = ""
        for group_number_match in re.findall(r"\d+", args.filename_in):
            group_number = group_number_match
        print("Group     : ", group_number)
    print("Expansions: ", expansions)
    print("Duplicates: ", duplicates)
    print("Synonyms  : ", synonyms)
