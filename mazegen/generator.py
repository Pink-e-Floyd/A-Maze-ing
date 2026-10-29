"""Maze generator with BFS solver and an optional "42" pattern."""

import random
from collections import deque

Cell = tuple[int, int]
Grid = list[list[int]]
N, E, S, W = 1, 2, 4, 8
DELTA = {N: (0, -1), E: (1, 0), S: (0, 1), W: (-1, 0)}
OFFSET_LETTER = {(0, -1): "N", (1, 0): "E", (0, 1): "S", (-1, 0): "W"}
OPPOSITE = {N: S, S: N, E: W, W: E}

PATTERN_42 = (
    "#...###",
    "#.....#",
    "#.....#",
    "###.###",
    "..#.#..",
    "..#.#..",
    "..#.###",
)


class MazeGenerator:
    """Generate and solve rectangular mazes.

    Each cell of the grid is an int whose bits are its closed walls:
    N=1, E=2, S=4, W=8 (0xF means all four walls closed).

    Args:
        width: Number of columns.
        height: Number of rows.
        entry: (x, y) of the entry cell.
        exit: (x, y) of the exit cell. Defaults to the bottom-right cell.
        perfect: If True, only one path exists between any two cells.
        seed: Random seed. A random one is chosen if None.
    """

    def __init__(self, width: int, height: int, entry: Cell = (0, 0),
                 exit: Cell | None = None, perfect: bool = False,
                 seed: int | None = None) -> None:
        """Validate the parameters and set up the generator.

        Raises:
            ValueError: If the size is invalid, or entry/exit are out of
                bounds or equal.
        """
        if width < 1 or height < 1:
            raise ValueError("width and height must be positive")
        self._width = width
        self._height = height
        self._entry = entry
        self._exit = exit if exit is not None else (width - 1, height - 1)
        if not self._in_bounds(self._entry):
            raise ValueError(f"entry {self._entry} is outside the maze")
        if not self._in_bounds(self._exit):
            raise ValueError(f"exit {self._exit} is outside the maze")
        if self._entry == self._exit:
            raise ValueError("entry and exit must be different")
        self._perfect = perfect
        self._seed = seed if seed is not None else random.randrange(2**32)
        self._rng = random.Random(self._seed)
        self._grid: Grid = []
        self._pattern: frozenset[Cell] = frozenset()
        self._generated = False
        self._center: Cell = (width // 2, height // 2)

    @property
    def grid(self) -> Grid:
        """Grid of wall bits, indexed as grid[y][x]."""
        return self._grid

    @property
    def seed(self) -> int:
        """Seed used by the random generator."""
        return self._seed

    @property
    def entry(self) -> Cell:
        """Entry cell (x, y)."""
        return self._entry

    @property
    def exit_(self) -> Cell:
        """Exit cell (x, y)."""
        return self._exit

    @property
    def center(self) -> Cell:
        """Center cell of the maze or of the 42 pattern."""
        return self._center

    @property
    def has_pattern(self) -> bool:
        """True if the 42 pattern fits in the maze."""
        return bool(self._pattern)

    @property
    def pattern_cells(self) -> frozenset[Cell]:
        """Cells that form the 42 pattern (fully closed)."""
        return self._pattern

    def generate(self) -> None:
        """Build a new maze, with loops if perfect is False.

        Raises:
            ValueError: If entry or exit is inside the 42 pattern.
        """
        self._generated = False
        self._grid = [[0xF] * self._width for _ in range(self._height)]
        self._place_pattern()
        if self._entry in self._pattern or self._exit in self._pattern:
            raise ValueError("entry and exit must not be in the 42 pattern")
        self._carve()
        if not self._perfect:
            self._add_loops()
        self._generated = True

    def _place_pattern(self) -> None:
        """Place the 42 pattern in the center if the maze is big enough."""
        ph = len(PATTERN_42)
        pw = len(PATTERN_42[0])
        if self._height < ph + 2 or self._width < pw + 2:
            return
        placement_y = (self._height - ph) // 2
        placement_x = (self._width - pw) // 2
        self._center = (placement_x + pw // 2, placement_y + ph // 2)
        pattern = set()
        for row, line in enumerate(PATTERN_42):
            for col, char in enumerate(line):
                if char == "#":
                    pattern.add((col + placement_x, row + placement_y))
        self._pattern = frozenset(pattern)

    def solve(self) -> list[Cell]:
        """Find the shortest path from entry to exit using BFS.

        Returns:
            List of cells from entry to exit, both included.

        Raises:
            RuntimeError: If the maze was not generated yet.
            ValueError: If there is no path between entry and exit.
        """
        if not self._generated:
            raise RuntimeError("maze not generated")
        parent: dict[Cell, Cell | None] = {self._entry: None}
        queue = deque([self._entry])
        while queue:
            current = queue.popleft()
            x, y = current
            if current == self._exit:
                break
            for d, cell in self._neighbors(current):
                if cell not in parent and not self._grid[y][x] & d:
                    queue.append(cell)
                    parent[cell] = current
        solution: list[Cell] = []
        last: Cell | None = self._exit
        if self._exit not in parent:
            raise ValueError("no path exists between entry and exit")
        while last is not None:
            solution.append(last)
            last = parent[last]
        return solution[::-1]

    def solution_directions(self) -> str:
        """Convert the shortest path into directions.

        Returns:
            String of N, E, S and W letters, one per step.
        """
        path = self.solve()
        directions: str = ""
        for a, b in zip(path, path[1:]):
            ax, ay = a
            bx, by = b
            step = (bx - ax, by - ay)
            directions += OFFSET_LETTER[step]
        return directions

    def _in_bounds(self, cell: Cell) -> bool:
        """Return True if the cell is inside the maze."""
        x, y = cell
        return 0 <= x < self._width and 0 <= y < self._height

    def _neighbors(self, cell: Cell) -> list[tuple[int, Cell]]:
        """Return (direction, cell) pairs for neighbors inside the maze."""
        x, y = cell
        result = []
        for d, (dx, dy) in DELTA.items():
            nxt = (x + dx, y + dy)
            if self._in_bounds(nxt):
                result.append((d, nxt))
        return result

    def _remove_wall(self, cell: Cell, d: int) -> None:
        """Open the wall in direction d on both sides."""
        x, y = cell
        dx, dy = DELTA[d]
        self._grid[y][x] &= ~d
        self._grid[y + dy][x + dx] &= ~OPPOSITE[d]

    def _carve(self) -> None:
        """Carve a perfect maze with iterative DFS (recursive backtracker)."""
        visited = set(self._pattern)
        visited.add(self._entry)
        stack = [self._entry]
        while stack:
            current = stack[-1]
            candidates: list[tuple[int, Cell]] = []
            for d, cell in self._neighbors(current):
                if cell not in visited:
                    candidates.append((d, cell))
            if candidates:
                d, cell = self._rng.choice(candidates)
                self._remove_wall(current, d)
                visited.add(cell)
                stack.append(cell)
            else:
                stack.pop()

    def _add_wall(self, cell: Cell, d: int) -> None:
        """Close the wall in direction d on both sides."""
        x, y = cell
        dx, dy = DELTA[d]
        self._grid[y][x] |= d
        self._grid[y + dy][x + dx] |= OPPOSITE[d]

    def _is_dead_end(self, cell: Cell) -> bool:
        """Return True if the cell has exactly three walls."""
        x, y = cell
        return self._grid[y][x].bit_count() == 3

    def _block_is_open(self, x0: int, y0: int) -> bool:
        """Return True if the 3x3 block at (x0, y0) has no inner walls."""
        for y in range(y0, y0 + 3):
            for x in range(x0, x0 + 3):
                if self._grid[y][x] & E and x != x0 + 2:
                    return False
                if self._grid[y][x] & S and y != y0 + 2:
                    return False
        return True

    def _creates_open_area(self, cell: Cell) -> bool:
        """Return True if any 3x3 block containing the cell is open."""
        x, y = cell
        for x0 in range(x - 2, x + 1):
            for y0 in range(y - 2, y + 1):
                if x0 < 0 or y0 < 0:
                    continue
                if x0 + 2 >= self._width or y0 + 2 >= self._height:
                    continue
                if self._block_is_open(x0, y0):
                    return True
        return False

    def _add_loops(self) -> None:
        """Open walls of dead ends to create loops without 3x3 open areas."""
        dead_ends = [
            (x, y) for x in range(self._width)
            for y in range(self._height) if self._is_dead_end((x, y))
        ]
        self._rng.shuffle(dead_ends)
        for dead_end in dead_ends:
            x, y = dead_end
            if not self._is_dead_end(dead_end):
                continue
            options: list[tuple[int, Cell]] = []
            for d, cell in self._neighbors(dead_end):
                if self._grid[y][x] & d and cell not in self._pattern:
                    options.append((d, cell))
            self._rng.shuffle(options)
            for d, cell in options:
                self._remove_wall(dead_end, d)
                if self._creates_open_area(dead_end):
                    self._add_wall(dead_end, d)
                else:
                    break
