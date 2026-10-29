"""Entry point of A-Maze-ing: read the config, build the maze and show it."""

import sys
from mazegen import MazeGenerator
from app import (
    ConfigError, format_maze, load_config,
    run_interactive, write_maze
)


def main(argv: list[str]) -> int:
    """Run the A-Maze-ing program.

    Load the config, generate the maze, write it to the output file
    and start the interactive menu.

    Args:
        argv: Command line arguments. argv[1] is the config file path.

    Returns:
        0 on success, 1 on error.
    """
    if len(argv) != 2:
        print("Usage: python3 a_maze_ing.py config.txt", file=sys.stderr)
        return 1
    try:
        config = load_config(argv[1])
        generator = MazeGenerator(width=config.width, height=config.height,
                                  entry=config.entry, exit=config.exit_,
                                  perfect=config.perfect, seed=config.seed)
        generator.generate()
        if not generator.has_pattern:
            print(
                "Maze too small for the 42 pattern (needs at least "
                f"9x9, got {config.width}x{config.height}): pattern skipped.",
                file=sys.stderr
            )
        content = format_maze(generator.grid, generator.entry,
                              generator.exit_,
                              generator.solution_directions())
        write_maze(config.output_file, content)
    except ConfigError as e:
        print(f"Config error: {e}", file=sys.stderr)
        return 1
    except ValueError as e:
        print(f"Maze error: {e}", file=sys.stderr)
        return 1
    except OSError as e:
        print(f"Could not write file: {e}", file=sys.stderr)
        return 1
    run_interactive(generator)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
