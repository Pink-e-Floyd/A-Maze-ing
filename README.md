*This project has been created as part of the 42 curriculum by tjulya-c, hesantan.*

# A-Maze-ing

## Description

A-Maze-ing is a maze generator written in Python 3.10+. It reads a
configuration file, generates a random rectangular maze, writes it to a file
in a hexadecimal wall format and draws it in the terminal, with an
interactive menu to regenerate it, show its solution and change its colours.

Features:

- **Two modes**: a *perfect* maze (exactly one path between any two cells)
  or a *Pac-Man-like board* with loops, full connectivity and no 3x3 open
  area.
- **"42" pattern**: a "42" made of fully closed cells is drawn in the centre
  of the maze when it fits.
- **Shortest path** from entry to exit, computed with BFS.
- **Reproducible output**: the same seed always produces the same maze.
- **Reusable package**: the generator is a standalone pip-installable
  package, `mazegen`, with no dependencies.

### Project structure

```
a_maze_ing.py        Entry point: config -> generation -> output file -> display
app/
  config.py          Parses and validates the configuration file
  writer.py          Formats and writes the output file
  display.py         Terminal rendering and interactive menu
mazegen/
  generator.py       MazeGenerator: generation, loops, 42 pattern, BFS solver
mazegen-1.0.0-py3-none-any.whl   Built package (see "Reusable code")
```

`mazegen` knows nothing about the config file, the output format or the
terminal: it only builds and solves mazes. Everything specific to this
program lives in `app/`.

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
make run                            # python3 a_maze_ing.py config.txt
python3 a_maze_ing.py my_config.txt # any other configuration file
```

The program exits with status `0` on success and `1` on error (invalid
config, impossible maze, unwritable output file). Errors are printed as a
single message on `stderr`, without a traceback.

### Makefile rules

| Rule               | What it does                                            |
|--------------------|---------------------------------------------------------|
| `make install`     | Installs the dev tools from `requirements-dev.txt`      |
| `make run`         | Runs the program with `config.txt`                      |
| `make debug`       | Runs the program under `pdb`                            |
| `make lint`        | Runs `flake8` and `mypy` with the mandatory flags       |
| `make lint-strict` | Runs `flake8` and `mypy --strict`                       |
| `make build`       | Builds `mazegen` and copies the `.whl` to the repo root |
| `make clean`       | Removes caches and build files                          |

### Interactive menu

```
=== A-Maze-ing ===
1. Re-generate a new maze
2. Show / Hide the shortest path
3. Rotate the wall colours
4. Quit
```

`Ctrl+C` and `Ctrl+D` also quit. Each wall is drawn two characters wide; if
the maze does not fit in the terminal, a message tells you how many columns
are needed instead of printing a broken drawing.

Colours: walls rotate between several shades, while the entry, the exit,
the path and the 42 pattern each have a fixed colour.

## Configuration file

One `KEY=VALUE` per line.

- Empty lines and lines starting with `#` are ignored.
- Keys are case-insensitive. Spaces around keys, values and commas are
  ignored.
- An unknown key, a duplicated key, a missing mandatory key or an empty
  value is an error.

| Key           | Required | Format         | Description                                     |
|---------------|----------|----------------|-------------------------------------------------|
| `WIDTH`       | yes      | integer 2..200 | Number of columns                               |
| `HEIGHT`      | yes      | integer 2..200 | Number of rows                                  |
| `ENTRY`       | yes      | `x,y`          | Entry cell, inside the maze                     |
| `EXIT`        | yes      | `x,y`          | Exit cell, inside the maze, different from entry |
| `OUTPUT_FILE` | yes      | path           | File the maze is written to                     |
| `PERFECT`     | yes      | `True`/`False` | `True`: perfect maze. `False`: board with loops |
| `SEED`        | no       | integer >= 0   | Random seed. Omit it for a different maze each run |

Coordinates start at `0,0` in the top-left corner; `x` is the column and `y`
the row. The entry and the exit cannot be on a cell of the 42 pattern.

The size is capped at 200 to avoid freezing the program; the real limit for
the display is the terminal width.

Example (`config.txt`):

```
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

Error messages point to the faulty line when possible, for example:

```
Config error: line 3: WIDTH must be an integer, got 'abc'
```

## Output file format

One hexadecimal digit per cell, one row per line. The bits of each digit are
the **closed** walls of the cell:

| Bit | Value | Wall  |
|-----|-------|-------|
| 0   | 1     | North |
| 1   | 2     | East  |
| 2   | 4     | South |
| 3   | 8     | West  |

So `f` is a fully closed cell and `0` a cell with no walls. After an empty
line come the entry, the exit and the shortest path as `N`/`E`/`S`/`W`
letters:

```
d539553955553d3
97c6d3c69397c52
...

0,0
14,14
EESENEEESENEEEEESEESSSWSS...
```

Walls are always coherent: if a cell has its east wall closed, its east
neighbour has its west wall closed.

## Maze generation algorithm

**Step 1: perfect maze, randomized depth-first search** (recursive
backtracker), with an explicit stack instead of recursion so large mazes do
not hit Python's recursion limit.

1. Every cell starts with its 4 walls closed. The cells of the 42 pattern
   are marked as visited before starting, so they are never opened.
2. Push the entry on the stack and mark it as visited.
3. Look at the top of the stack. If it has unvisited neighbours, pick one at
   random, remove the wall between them, mark it visited and push it.
4. Otherwise pop it (backtrack).
5. Stop when the stack is empty.

Every non-pattern cell is reached exactly once, so the result is a spanning
tree of the grid: one single path between any two cells.

**Step 2 (only when `PERFECT=False`): loops.** Dead ends are visited in
random order. For each one, a closed wall leading to a non-pattern cell is
opened; if that creates a 3x3 open area, the wall is closed again and the
next wall is tried. This turns every dead end into a loop while keeping
corridors at most 2 cells wide.

**Solving: breadth-first search.** BFS explores the maze level by level from
the entry, so the first time it reaches the exit it has found a shortest
path. The path is rebuilt from a `parent` dictionary and converted to
`N`/`E`/`S`/`W` letters.

**42 pattern.** A 7x7 template is centred in the maze. If the maze is
smaller than 9x9, the pattern is skipped and a message is printed.

The gaps inside the "2" are two rows tall on purpose: with one-row gaps,
the cell at the back of each gap would have three closed sides (pattern
cells can never be opened), so it would always be a dead end. With two
rows, the cells of each gap can form a small loop.

## Why this algorithm

- **Simple to reason about**: one stack, one visited set, no extra data
  structure.
- **Linear time**: each cell is pushed and popped once, O(width x height).
- **Good-looking mazes**: long winding corridors and relatively few dead
  ends, which also leaves less work for the loop step.
- **Fits the 42 pattern naturally**: pre-marking pattern cells as visited is
  enough to keep them closed, with no special case in the loop.
- **Reproducible**: every random choice goes through a single
  `random.Random(seed)`, so the same seed gives the same maze.

Alternatives such as Prim's or Kruskal's algorithms also build spanning
trees, but produce many short dead ends, which goes against the "few dead
ends" goal of the non-perfect mode.

## Reusable code

The `mazegen` package (the `mazegen/` folder) is the reusable part. It has no
dependencies, is fully typed (ships a `py.typed` marker) and is built as
`mazegen-1.0.0-py3-none-any.whl` at the root of this repository.

### Installation

```bash
pip install mazegen-1.0.0-py3-none-any.whl
```

To rebuild it from the sources:

```bash
pip install build
python3 -m build      # or: make build
```

### Usage

```python
from mazegen import MazeGenerator

maze = MazeGenerator(
    width=30,          # columns
    height=20,         # rows
    entry=(0, 0),      # (x, y), default (0, 0)
    exit=(29, 19),     # (x, y), default: bottom-right cell
    perfect=True,      # default False
    seed=42,           # default: random
)
maze.generate()

maze.grid                   # list of rows, grid[y][x] = wall bits (see above)
maze.solve()                # [(0, 0), (1, 0), ..., (29, 19)], shortest path
maze.solution_directions()  # "EESW...", one letter per step
maze.seed                   # seed actually used (useful when it was random)
maze.entry, maze.exit_      # entry and exit cells
maze.center                 # open cell in the middle (player start)
maze.has_pattern            # False if the maze is too small for the 42
maze.pattern_cells          # frozenset of the 42 cells
```

Checking a wall:

```python
cell = maze.grid[y][x]
north_closed = bool(cell & 1)
east_closed = bool(cell & 2)
```

Errors:

- `ValueError` from the constructor if the size is not positive, or the
  entry/exit is outside the maze or both are the same cell.
- `ValueError` from `generate()` if the entry or exit is on the 42 pattern.
- `RuntimeError` from `solve()` if `generate()` was not called first.

Calling `generate()` again builds a new maze with the same parameters.

## Advanced features

- **Braided board, no dead ends (bonus)**: with `PERFECT=False`, the maze
  has several independent routes, full connectivity, no 3x3 open area and
  no dead end at all, so a chased player is never trapped.
- **Seed**: the optional `SEED` key makes any maze reproducible.
- **Colour themes**: menu option 3 rotates the wall colour; the 42 pattern,
  entry, exit and path have their own colours.
- **Terminal size check**: the display warns instead of printing a maze
  wider than the terminal.

## Resources

- [Maze generation algorithm (Wikipedia)](https://en.wikipedia.org/wiki/Maze_generation_algorithm)
- [Jamis Buck, "Maze Generation: Recursive Backtracking"](https://weblog.jamisbuck.org/2010/12/27/maze-generation-recursive-backtracking)
- [Breadth-first search (Wikipedia)](https://en.wikipedia.org/wiki/Breadth-first_search)
- Python documentation: [`random`](https://docs.python.org/3/library/random.html),
  [`collections.deque`](https://docs.python.org/3/library/collections.html#collections.deque),
  [`dataclasses`](https://docs.python.org/3/library/dataclasses.html)
- [Python Packaging User Guide: writing `pyproject.toml`](https://packaging.python.org/en/latest/guides/writing-pyproject-toml/)
- [PEP 257: Docstring conventions](https://peps.python.org/pep-0257/)
- [ANSI escape codes: 256 colours](https://en.wikipedia.org/wiki/ANSI_escape_code#8-bit)

### How AI was used

We used Claude (Anthropic) as a tutor:

- **Explanations**: DFS and BFS, wall bitmasks, Python packaging, and
  reading the subject requirements.
- **Code review**: we wrote the modules ourselves and asked the AI to review
  them, point out bugs, `flake8`/`mypy` errors and missing docstrings.
- **Documentation and packaging**: the AI drafted this README, the
  `pyproject.toml` and `requirements-dev.txt`, which we reviewed and edited.

Every part of the code was read and understood by both of us before being
merged.

## Team & project management

**Roles**

- **tjulya-c**: `mazegen` package, output writer (`app/writer.py`) and
  terminal display (`app/display.py`).
- **hesantan**: configuration parser (`app/config.py`), `config.txt` and the
  main program (`a_maze_ing.py`).
- **Both**: Makefile, packaging, README and cross-review of pull requests.

**Planning.** One GitHub issue and one branch per module (generator, writer,
display, config, main), each merged through a pull request. The plan was to
start with the config; in practice the generator and writer were ready
first, so they were tested with hard-coded values and the config was plugged
in at the end together with the main program. Packaging and documentation
came last.

**What worked well**

- Keeping `mazegen` independent from `app/` from the start: packaging it
  required no refactoring.
- Small modules with clear inputs and outputs, so each of us could work in
  parallel and test our part alone.
- Running `flake8` and `mypy` on every module instead of at the end.

**What could be improved**

- Agree on shared interfaces earlier: for example the exit is called `exit`
  in `MazeGenerator` and `exit_` in `Config`, which caused confusion when
  connecting the modules.
- Write automated tests (pytest) for the generator and the config parser
  instead of testing by hand.
- Look at the shape of the 42 pattern earlier: the last two dead ends of
  the non-perfect mode came from the pattern itself, not from the
  algorithm, and took a while to spot.

**Tools**: Git and GitHub (issues, branches, pull requests), `flake8`,
`mypy`, `build`/`setuptools`, `pdb`, and Claude (see above).
