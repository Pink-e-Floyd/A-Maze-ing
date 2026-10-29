*This project has been created as part of the 42 curriculum by hesantan, tjulya-c*

# mazegen

Reusable maze generator for Python 3.10+. It builds rectangular mazes
(perfect or with loops), draws a "42" pattern in the center when the maze
is big enough, and finds the shortest path from entry to exit.

## Installation

```bash
pip install mazegen-1.0.0-py3-none-any.whl
```

To rebuild the package from the sources (at the repository root):

```bash
pip install build
python3 -m build
```

## Basic usage

```python
from mazegen import MazeGenerator

maze = MazeGenerator(20, 15)
maze.generate()
print(maze.solution_directions())  # e.g. "EESENEE..."
```

## Custom parameters

```python
maze = MazeGenerator(
    width=30,          # number of columns
    height=20,         # number of rows
    entry=(0, 0),      # (x, y) of the entry
    exit=(29, 19),     # (x, y) of the exit (default: bottom-right cell)
    perfect=True,      # True: one single path between any two cells
    seed=42,           # same seed = same maze (default: random)
)
maze.generate()
```

`ValueError` is raised if the size is invalid, if entry/exit are outside
the maze, equal, or inside the 42 pattern.

## Accessing the structure

`maze.grid` is a list of rows, indexed as `grid[y][x]`. Each cell is an int
whose bits are its **closed** walls:

| Bit | Value | Wall  |
|-----|-------|-------|
| 0   | 1     | North |
| 1   | 2     | East  |
| 2   | 4     | South |
| 3   | 8     | West  |

```python
cell = maze.grid[0][0]
has_north_wall = bool(cell & 1)
has_east_wall = bool(cell & 2)
```

Other attributes: `maze.seed`, `maze.entry`, `maze.exit_`,
`maze.has_pattern` (False if the maze is too small for the 42) and
`maze.pattern_cells` (cells of the 42, fully closed).

## Accessing the solution

```python
path = maze.solve()                 # [(0, 0), (1, 0), ..., exit]
moves = maze.solution_directions()  # "EESW..." (one letter per step)
```

Both use BFS, so the path returned is always the shortest one.
`solve()` raises `RuntimeError` if `generate()` was not called first.
