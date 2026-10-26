Cell = tuple[int, int]
Grid = list[list[int]]
N, E, S, W = 1, 2, 4, 8
DELTA = {N: (0, -1), E: (1, 0), S: (0, 1), W: (-1, 0)}
OPPOSITE = {N: S, S: N, E: W, W: E}

PATTERN_42 = (
    "#...###",
    "#.....#",
    "###.###",
    "..#.#..",
    "..#.###",
)

class MazeGenerator:
    def __init__(self, width: int, height: int, entry: Cell = (0, 0),
                exit: Cell | None = None, perfect: bool = False,
                seed: int | None = None) -> None:
        if width < 1 or height < 1:
            raise ValueError("blabblabla")
        self.width = width
        self.height = height
        self.entry = entry
        self.exit = exit
        self.perfect = perfect
        self.seed = seed

    def generate(self) -> None:
        pass

    @property
    def grid(self) -> Grid:
        pass

    @property
    def seed(self) -> int:
        pass

    @property
    def has_pattern(self) -> bool:
        pass

    @property
    def pattern_cells(self) -> frozenset[Cell]:
        pass

    def solve(self) -> list[Cell]:
        pass

    def solution_directions(self) -> str:
        pass

    def _in_bounds(self, cell: Cell) -> bool:
        pass

    def _neighbors(self, cell: Cell) -> list[tuple[int, Cell]]:
        pass

    def _remove_wall(self, cell: Cell, direction: int) -> None:
        pass

    def _place_pattern(self) -> bool:
        pass

    def _carve(self) -> None:
        pass

    def _add_loops(self) -> None:
        pass