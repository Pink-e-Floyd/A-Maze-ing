*This project has been created as part of the 42 curriculum by tjulya-c, hesantan.*

# A-Maze-ing

## Description

A-Maze-ing is a maze generator written in Python 3.10+. It reads a
configuration file, builds a random rectangular maze, writes it to an output
file using a hexadecimal wall format, and shows it in the terminal with an
interactive menu.

Main features:

- **Perfect mazes** (exactly one path between any two cells) or **mazes with
  loops** (several paths, but never a 3x3 open area).
- A **"42" pattern** made of fully closed cells drawn in the center of the
  maze when it is big enough.
- The **shortest path** from entry to exit, found with BFS.
- **Reproducible mazes**: the same seed always gives the same maze.
- A coloured **terminal display** where you can regenerate the maze, show or
  hide the shortest path and change the wall colours.

The generation logic lives in a reusable package, `mazegen`, that can be
installed with pip and used in other projects.

## Instructions

### Requirements

- Python 3.10 or newer
- A terminal with 256-colour support

### Installation

```bash
python3 -m venv .venv
source .venv/bin/activate
make install          # installs flake8, mypy and build
```

### Running

```bash
make run              # same as: python3 a_maze_ing.py config.txt
```

You can also pass another configuration file:

```bash
python3 a_maze_ing.py my_config.txt
```

### Other Makefile rules

| Rule               | What it does                                           |
|--------------------|--------------------------------------------------------|
| `make install`     | Installs the dev tools from `requirements-dev.txt`     |
| `make run`         | Runs the program with `config.txt`                     |
| `make debug`       | Runs the program with `pdb`                            |
| `make lint`        | Runs `flake8` and `mypy` with the mandatory flags      |
| `make lint-strict` | Runs `flake8` and `mypy --strict`                      |
| `make build`       | Builds the `mazegen` package and copies the `.whl` here |
| `make clean`       | Removes caches and build files                         |

### Interactive menu

```
=== A-Maze-ing ===
1. Re-generate a new maze
2. Show / Hide the shortest path
3. Rotate the wall colours
4. Quit
```

`Ctrl+C` or `Ctrl+D` also quits.

## Configuration file

The configuration file is a text file with one `KEY=VALUE` per line.

- Lines starting with `#` and empty lines are ignored.
- Keys are case-insensitive (`width` and `WIDTH` are the same).
- Spaces around keys, values and commas are ignored.
- An unknown key, a duplicated key or an empty value is an error.

| Key           | Required | Format          | Description                                   |
|---------------|----------|-----------------|-----------------------------------------------|
| `WIDTH`       | yes      | integer 2..200  | Number of columns                             |
| `HEIGHT`      | yes      | integer 2..200  | Number of rows                                |
| `ENTRY`       | yes      | `x,y`           | Entry cell, must be inside the maze           |
| `EXIT`        | yes      | `x,y`           | Exit cell, inside the maze and not the entry  |
| `OUTPUT_FILE` | yes      | file name       | Where the maze is written                     |
| `PERFECT`     | yes      | `True`/`False`  | `True`: perfect maze. `False`: maze with loops |
| `SEED`        | no       | integer >= 0    | Random seed. Omit it to get a random maze     |

Coordinates start at `0,0` in the top-left corner. `x` is the column and `y`
is the row. The entry and the exit cannot be inside the 42 pattern.

Example (`config.txt`):

```
# A-Maze-ing default configuration
# Mandatory keys
WIDTH=15
HEIGHT=15
ENTRY=0 , 0
EXIT=14 , 14
OUTPUT_FILE=maze.txt
PERFECT=True

# Optional keys
SEED=42
```

If the file is missing or invalid, the program prints a clear error message
(with the line number when possible) and exits with status 1.

### Output file format

Each cell is written as one hexadecimal digit whose bits are its **closed**
walls (1 = North, 2 = East, 4 = South, 8 = West), one row per line. After an
empty line come the entry, the exit and the shortest path as letters
(`N`, `E`, `S`, `W`):

```
d539553955553d3
97c6d3c69397c52
a95154396c6953a
...

0,0
14,14
EESENEEESENEEEEESEESSSWSS...
```

## Maze generation algorithm

We use the **randomized depth-first search**, also called the
**recursive backtracker**, written with an explicit stack (no recursion, so
big mazes do not hit Python's recursion limit):

1. Start with every cell having its 4 walls closed. The cells of the 42
   pattern are marked as already visited, so they stay closed.
2. Push the entry cell on the stack and mark it as visited.
3. Look at the cell on top of the stack. If it has unvisited neighbours,
   pick one at random, remove the wall between them, mark it visited and
   push it.
4. If it has no unvisited neighbours, pop it (backtrack).
5. Repeat until the stack is empty.

The result is a perfect maze (a spanning tree of the grid).

When `PERFECT=False`, a second step adds loops: dead ends are visited in
random order and one of their walls is opened, but only if this does not
create a 3x3 open area. If it does, the wall is closed again.

The shortest path is found with **breadth-first search (BFS)**, which always
returns the shortest path in an unweighted grid.

## Why this algorithm

- **Simple**: it is easy to understand, write and explain.
- **Fast**: each cell is visited once, so it runs in O(width x height).
- **Nice mazes**: it makes long, winding corridors with few short dead ends,
  which look good and are fun to solve.
- **Works with the 42 pattern**: marking the pattern cells as visited is
  enough to keep them closed.
- **Reproducible**: all random choices use one `random.Random(seed)`, so the
  same seed gives the same maze.

## Reusable code

The `mazegen/` folder is a standalone package. It has no dependencies and
does not know anything about the config file, the output file or the
display (those live in `app/`). It is packaged as
`mazegen-1.0.0-py3-none-any.whl`, available at the root of this repository.

### Installation

```bash
pip install mazegen-1.0.0-py3-none-any.whl
```

To rebuild the package from the sources (at the repository root):

```bash
pip install build
python3 -m build      # or: make build
```

The files are created in `dist/`.

### Basic usage

```python
from mazegen import MazeGenerator

maze = MazeGenerator(20, 15)
maze.generate()
print(maze.solution_directions())  # e.g. "EESENEE..."
```

### Custom parameters

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

### Accessing the structure

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

### Accessing the solution

```python
path = maze.solve()                 # [(0, 0), (1, 0), ..., exit]
moves = maze.solution_directions()  # "EESW..." (one letter per step)
```

Both use BFS, so the path returned is always the shortest one.
`solve()` raises `RuntimeError` if `generate()` was not called first.

## Advanced features

- **Loops without open areas**: when `PERFECT=False`, loops are added but no
  3x3 area is ever fully open.
- **Seed**: the optional `SEED` key makes any maze reproducible.
- **Colour themes**: option 3 of the menu rotates between several wall
  colours; entry, exit, path and the 42 pattern each have their own colour.

## Team & project management

### Roles

- **tjulya-c**: `mazegen` package (generation, loops, 42 pattern, BFS
  solver), output file writer (`app/writer.py`) and terminal display
  (`app/display.py`).
- **hesantan**: configuration parser (`app/config.py`), `config.txt` and
  the main program (`a_maze_ing.py`).
- **Both**: Makefile, packaging, README and reviews of each other's pull
  requests.

### Planning

We split the project into small modules, one GitHub issue each:
generator, writer, display, config and main. Each module was developed on
its own branch and merged with a pull request.

The first plan was to finish the config first. In practice the generator
and the writer were ready before it, so we used hard-coded values to test
them and plugged the config in at the end, together with the main program.
Packaging and the README were left for the last step.

### Tools

- Git and GitHub (issues, branches, pull requests)
- `flake8` and `mypy` for code quality
- `build` and `setuptools` for packaging
- `pdb` for debugging
- Claude (AI assistant), see below

## Resources

- [Maze generation algorithm (Wikipedia)](https://en.wikipedia.org/wiki/Maze_generation_algorithm)
- [Jamis Buck, "Maze Generation: Recursive Backtracking"](https://weblog.jamisbuck.org/2010/12/27/maze-generation-recursive-backtracking)
- [Breadth-first search (Wikipedia)](https://en.wikipedia.org/wiki/Breadth-first_search)
- [Python documentation: `random`](https://docs.python.org/3/library/random.html)
  and [`collections.deque`](https://docs.python.org/3/library/collections.html#collections.deque)
- [Python Packaging User Guide: writing `pyproject.toml`](https://packaging.python.org/en/latest/guides/writing-pyproject-toml/)
- [PEP 257: Docstring conventions](https://peps.python.org/pep-0257/)
- [ANSI escape codes: 256 colours](https://en.wikipedia.org/wiki/ANSI_escape_code#8-bit)

### How AI was used

We used Claude (Anthropic) as a tutor during the project:

- **Explanations**: maze algorithms (DFS, BFS), bitmasks for the walls, how
  Python packaging works and what the subject asks for.
- **Code review**: we wrote the code of the modules ourselves and asked the
  AI to review it, point out bugs, `flake8`/`mypy` errors and missing
  docstrings.
- **Documentation and packaging**: the AI wrote the first draft of this
  README, the `pyproject.toml` and the `requirements-dev.txt`, which we then
  reviewed.

Every part of the code was read and understood by both of us before being
merged.
