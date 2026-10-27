"""Write a generated maze to the output file format."""


def format_maze(grid: list[list[int]], entry: tuple[int, int],
                exit_: tuple[int, int], directions: str) -> str:
    """Build the output file content for a maze.

    Args:
        grid: Rows of cells, each cell a 4-bit wall mask (N, E, S, W).
        entry: (x, y) of the entry cell.
        exit_: (x, y) of the exit cell.
        directions: Shortest path from entry to exit using N, E, S, W.

    Returns:
        One hex digit per cell, one row per line, then an empty line,
        the entry, the exit and the path, each line ending with a newline.
    """
    maze: list[str] = []
    for line in grid:
        for number in line:
            maze.append(f"{number:x}")
        maze.append("\n")
    maze.append("\n")
    maze.append(f"{entry[0]},{entry[1]}\n")
    maze.append(f"{exit_[0]},{exit_[1]}\n")
    maze.append(f"{directions}\n")
    return "".join(maze)


def write_maze(path: str, content: str) -> None:
    """Write the formatted maze text to a file.

    Args:
        path: Path of the output file.
        content: Text returned by format_maze.
    """
    with open(path, "w") as f:
        f.write(content)
