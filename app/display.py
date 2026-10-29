"""Draw the maze in the terminal and run the interactive menu."""

from mazegen import MazeGenerator
import shutil
Cell = tuple[int, int]
N, E, S, W = 1, 2, 4, 8
DEFAULT_PALETTE = {
    "wall": "224", "entry": "34", "exit": "198", "path": "14", "pattern": "135"
}
WALL_COLORS = ["225", "211", "159", "15"]


def _slots(grid: list[list[int]]) -> list[list[bool]]:
    """Turn the cell grid into a grid of wall slots.

    Args:
        grid: Rows of cells, each cell a 4-bit wall mask (N, E, S, W).

    Returns:
        A (2H+1) x (2W+1) grid where True means wall and False means open.
    """
    h = 2 * len(grid) + 1
    w = 2 * len(grid[0]) + 1
    slots: list[list[bool]] = [[True for _ in range(w)] for _ in range(h)]

    for y, line in enumerate(grid):
        for x, value in enumerate(line):
            slots[y * 2 + 1][x * 2 + 1] = False
            if not (value & E):
                slots[y * 2 + 1][x * 2 + 2] = False
            if not (value & S):
                slots[y * 2 + 2][x * 2 + 1] = False

    return slots


def _to_slot(cell: Cell) -> Cell:
    """Convert a cell (x, y) to its slot coordinates."""
    x, y = cell
    return (x * 2 + 1, y * 2 + 1)


def _block(code: str) -> str:
    """Return a two-space block painted with a 256-colour background."""
    return f"\033[48;5;{code}m  \033[0m"


def render(grid: list[list[int]], entry: Cell, exit_: Cell,
           path: list[Cell] | None, pattern_cells: frozenset[Cell],
           palette: dict[str, str]) -> str:
    """Draw the maze as a string of emoji, ready to print.

    Args:
        grid: Rows of cells, each cell a 4-bit wall mask (N, E, S, W).
        entry: (x, y) of the entry cell.
        exit_: (x, y) of the exit cell.
        path: Cells of the shortest path, or None to hide it.
        pattern_cells: Cells of the 42 pattern.
        palette: Emoji for "wall", "entry", "exit", "path" and "pattern".

    Returns:
        One line of text per slot row, joined with newlines.
    """
    slots = _slots(grid)
    new_entry = _to_slot(entry)
    new_exit = _to_slot(exit_)
    new_pattern = {_to_slot(c) for c in pattern_cells}
    new_path: set[Cell] = set()
    for x, y in pattern_cells:
        if (x + 1, y) in pattern_cells:
            new_pattern.add((2 * x + 2, 2 * y + 1))
        if (x, y + 1) in pattern_cells:
            new_pattern.add((2 * x + 1, 2 * y + 2))

    if path:
        new_path = {_to_slot(c) for c in path}
        for a, b in zip(path, path[1:]):
            ax, ay = a
            bx, by = b
            hole = (ax + bx + 1, ay + by + 1)
            new_path.add(hole)

    lines: list[str] = []
    for row, line in enumerate(slots):
        pieces: list[str] = []
        for col, is_wall in enumerate(line):
            pos = (col, row)
            if pos == new_entry:
                pieces.append(_block(palette["entry"]))
            elif pos == new_exit:
                pieces.append(_block(palette["exit"]))
            elif pos in new_pattern:
                pieces.append(_block(palette["pattern"]))
            elif pos in new_path:
                pieces.append(_block(palette["path"]))
            elif is_wall:
                pieces.append(_block(palette["wall"]))
            else:
                pieces.append("  ")
        lines.append("".join(pieces))

    return "\n".join(lines)


def run_interactive(generator: MazeGenerator) -> None:
    """Show the maze and a menu until the user quits.

    The user can generate a new maze, show or hide the shortest path,
    and rotate the wall colour. Ctrl+C or Ctrl+D also quits.

    Args:
        generator: A MazeGenerator whose maze is already generated.
    """
    palette = dict(DEFAULT_PALETTE)
    show_path = True
    color_index = 0

    while True:
        path = generator.solve() if show_path else None
        cols = shutil.get_terminal_size().columns
        needed = (2 * len(generator.grid[0]) + 1) * 2
        if needed > cols:
            print(
                f"Maze too wide for this terminal "
                f"(needs {needed} columns, has {cols}). "
                "Zoom out or enlarge the window."
            )
        else:
            print(render(generator.grid, generator.entry, generator.exit_,
                         path, generator.pattern_cells, palette))
        print(
            "=== A-Maze-ing ===\n"
            "1. Re-generate a new maze\n"
            "2. Show / Hide the shortest path\n"
            "3. Rotate the wall colours\n"
            "4. Quit\n"
        )

        try:
            choice = input("Choice? (1-4) ").strip()
        except (KeyboardInterrupt, EOFError):
            break

        if choice == "1":
            generator.generate()
        elif choice == "2":
            show_path = not show_path
        elif choice == "3":
            color_index = (color_index + 1) % len(WALL_COLORS)
            palette["wall"] = WALL_COLORS[color_index]
        elif choice == "4":
            break
        else:
            print("Please, choose an available choice.")
