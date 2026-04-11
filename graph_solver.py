from utils.input_parser import FieldTiles, get_point_value, HorseField
from collections import deque
from argparse import ArgumentParser
import re
from datetime import datetime


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

TILE_GRID: list[list[Tile]] = []

class SubField:
    def __init__(self, current_state: set[Tile]):
        self.state: set[Tile] = current_state
        self.points: int = 0
        self.known: set[Tile] = set()
        self.boundary: set[Tile] = set()
        for tile in self.state:
            self.points += tile.points
            self.boundary.update(tile.adjacencies - self.state)
        self.known = self.state|self.boundary
        self.boundary_len = len(self.boundary)

    def copy(self) -> "SubField":
        new = SubField.__new__(SubField)
        new.state = set(self.state)
        new.boundary = set(self.boundary)
        new.known = set(self.known)
        new.points = self.points
        new.boundary_len = self.boundary_len
        return new

    def freeze(self):
        self.state = frozenset(self.state)
        self.boundary = frozenset(self.boundary)
        self.boundary_len = len(self.boundary)
        self.known = frozenset(self.known)

    def validate_boundary_tile(self, tile: Tile) -> bool:
        if tile.tile_type != FieldTiles.GRASS:
            return True
        boundary_adjacent = tile.adjacencies-self.known
        num_adjacent = len(boundary_adjacent)
        if num_adjacent == 0:
            return True
        if num_adjacent == 1 and all(boundary_adj.tile_type == FieldTiles.GRASS for boundary_adj in boundary_adjacent):
            return True
        return False

    def boundary_to_state(self, tile: Tile) -> list[Tile]:
        adjacencies = tile.adjacencies - self.known
        self.state.add(tile)
        self.known.add(tile)
        self.points += tile.points
        self.boundary.remove(tile)
        for adjacent_tile in adjacencies:
            self.known.add(adjacent_tile)
            self.boundary.add(adjacent_tile)
        return [tile for tile in adjacencies if self.validate_boundary_tile(tile)]

    def include(self, include_tile: Tile) -> bool:
        check_expand = deque([include_tile])
        while check_expand:
            while check_expand:
                current = check_expand.popleft()
                if current.tile_type == FieldTiles.EDGE:
                    return False
                if current in self.state:
                    # Happens when added to state from boundary in multiple paths
                    self.boundary.discard(current)
                    continue
                # Move from boundary to state and update boundary accordingly
                check_expand.extend(self.boundary_to_state(current))
            # If expansion is still required for any boundary tile, add to queue
            check_expand.extend([tile for tile in self.boundary if self.validate_boundary_tile(tile)])
        if self.state|self.boundary != self.known:
            raise ValueError("State+Boundary != Known")
        # Do not expand this version of subfield again
        self.freeze()
        return True

    def is_synonym(self, other: "SubField") -> bool:
        if self.known.issubset(other.known) and self.points <= other.points:
            return True
        return False

    def __eq__(self, other: "SubField"):
        if isinstance(other, SubField):
            return self.state == other.state and self.boundary == other.boundary
        if isinstance(other, frozenset):
            return other == frozenset(self.state|self.boundary)
        return False

    def __hash__(self):
        return hash((self.state, self.boundary))

def file_record(record_function, grid_state: SubField):
    walls = [(wall_tile.row, wall_tile.col) for wall_tile in grid_state.boundary]
    record_function(f"{grid_state.points}")
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
    if new_solution.points <= best_solution.points:
        return best_solution
    if filename:
        with open(filename, "w", encoding="utf-8") as f:
            file_record(lambda line: f.write(line + "\n"), new_solution)
    else:
        file_record(lambda line: print(line), new_solution)
        print()
    return new_solution

def build_tile_grid(field_input):
    # Make an adjacent tile to all edges to track if escape is possible
    sink_tile = Tile(FieldTiles.EDGE, -1, -1)

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
                    new_tile.add_adjacency(sink_tile)
                elif adjacent_col < 0 or field_input.col_count <= adjacent_col:
                    new_tile.add_adjacency(sink_tile)
            TILE_GRID[row_idx].append(new_tile)
    for portal_coords, connected_portal in field_input.portals.items():
        portal1_row, portal1_col = portal_coords
        portal2_row, portal2_col = connected_portal
        TILE_GRID[portal1_row][portal1_col].add_adjacency(TILE_GRID[portal2_row][portal2_col])
        TILE_GRID[portal2_row][portal2_col].add_adjacency(TILE_GRID[portal1_row][portal1_col])

if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("-fin", "--filename_in", default=None)
    parser.add_argument("-fout", "--filename_out", default=None)
    args = parser.parse_args()

    print()
    if args.filename_in:
        group_number = ""
        for group_number_match in re.findall(r"\d+", args.filename_in):
            group_number = group_number_match
        print("Group     : ", group_number)
    start = datetime.now()
    print("Start:     ", start)

    field_input = HorseField(args.filename_in)
    build_tile_grid(field_input)
    horse_tile: Tile = TILE_GRID[field_input.horse[0]][field_input.horse[1]]
    initial_state = SubField({horse_tile})
    initial_state.freeze()
    subfields: list[SubField] = [initial_state]
    subfields_by_size: dict[int,set[SubField]] = {len(initial_state.boundary): set([initial_state])}
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
            bucket = subfields_by_size.setdefault(expanded.boundary_len, set())
            # If expanded has been seen before, don't track
            if expanded in bucket:
                duplicates += 1
                continue
            track = True
            subsets: set[SubField] = set()
            # Don't track subfields that are subsets of other subfields
            for idx, subfield in enumerate(bucket):
                # expanded is a worse version of subfield, don't track
                if expanded.is_synonym(subfield):
                    track = False
                    synonyms += 1
                    break
                # subfield is a worse version of expanded, track expanded and don't track subfield
                if subfield.is_synonym(expanded):
                    subsets.add(subfield)
                    synonyms += 1
            for subfield_synonym in subsets:
                subfields_by_size[expanded.boundary_len].remove(subfield_synonym)
            if not track:
                continue
            subfields_by_size[expanded.boundary_len].add(expanded)
            expand_queue.append(expanded)
            best_solution = record_best(field_input.wallBudget, best_solution, expanded, args.filename_out)

    print("Expansions: ", expansions)
    print("Duplicates: ", duplicates)
    print("Synonyms  : ", synonyms)
    end = datetime.now()
    print("End       :", end)
    print("Duration  :", end-start)
