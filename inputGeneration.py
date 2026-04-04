from abc import ABC, abstractmethod
import random


class Obstacle(ABC):
    @property
    @abstractmethod
    def pass_through(self) -> bool:
        pass

    @property
    @abstractmethod
    def points(self) -> int:
        pass

    @property
    @abstractmethod
    def __str__(self) -> str:
        pass

    def __eq__(self, compare_to) ->bool:
        return compare_to == self.__str__()


class Water(Obstacle):
    def pass_through(self) -> bool:
        return False

    def points(self) -> int:
        return 0

    def __str__(self) -> str:
        return "#"


class Grass(Obstacle):
    def pass_through(self) -> bool:
        return True

    def points(self) -> int:
        return 1

    def __str__(self) -> str:
        return "."


class Wall(Obstacle):
    def pass_through(self) -> bool:
        return False

    def points(self) -> int:
        return 0

    def __str__(self) -> str:
        return "W"


class Apple(Obstacle):
    def pass_through(self) -> bool:
        return True

    def points(self) -> int:
        return 11

    def __str__(self) -> str:
        return "a"


class Bees(Obstacle):
    def pass_through(self) -> bool:
        return True

    def points(self) -> int:
        return -4

    def __str__(self) -> str:
        return "b"


class Cherry(Obstacle):
    def pass_through(self) -> bool:
        return True

    def points(self) -> int:
        return 4

    def __str__(self) -> str:
        return "c"


class Portal(Obstacle):
    def pass_through(self) -> bool:
        return True

    def points(self) -> int:
        return 1

    def __str__(self) -> str:
        return "p"

def show_grid(grid):
    display_str = ""
    for row in grid:
        for cell in row:
            display_str += str(cell)
        display_str += "\n"
    print(display_str)

def random_build():
    n, x, y = map(int, input().split())
    grid = []
    for i in range(n):
        grid.append([])
        for _ in range(n):
            rand = random.randrange(0, 100, 1)
            if rand < 2:
                grid[i].append(Apple())
            elif rand < 5:
                grid[i].append(Cherry())
            elif rand < 8:
                grid[i].append(Bees())
            elif rand < 18:
                grid[i].append(Wall())
            elif rand < 28:
                grid[i].append(Water())
            elif rand < 100:
                grid[i].append(Grass())
        grid[i] = grid[i]*x
    grid = grid*y
    return grid

def guided_build(walls):
    obstacle_types = [Water(), Grass(), Wall(), Apple(), Bees(), Cherry(), Portal()]
    grid = []
    rows, columns = map(int, input().split())
    for i in range(rows):
        grid.append([])
        row_str = input()
        if len(row_str) != columns:
            print("BAD INPUT")
            return []
        for char in row_str:
            for obstacle in obstacle_types:
                if char == obstacle:
                    grid[i].append(obstacle)
                    break
    x, y = map(int, input().split())
    for idx, row in enumerate(grid):
        grid[idx] = row * x
    grid = grid * y
    return grid


if __name__ == "__main__":
    first_in = input()
    if "r" == first_in:
        grid = random_build()
    else:
        grid = guided_build(int(first_in))
    show_grid(grid)
