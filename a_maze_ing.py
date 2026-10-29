import sys
from mazegen import MazeGenerator
from app.config import load_config, ConfigError
from app.writer import format_maze, write_maze
from app.display import run_interactive


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("Usage: python3 a_maze_ing.py config.txt")
        return 1
    try:
        config = load_config(argv[1])
        generator = MazeGenerator(width=config.width, height=config.height,
                                  entry=config.entry, exit=config.exit_, 
                                  seed=config.seed)
        generator.generate()
        content = format_maze(generator.grid, generator.entry,
                              generator.exit_,
                              generator.solution_directions())
        write_maze(config.output_file, content)
        run_interactive(generator)
    except ConfigError as e:
        print(f"Config error: {e}", file=sys.stderr)
        return 1
    except ValueError as e:
        print(f"Maze error: {e}", file=sys.stderr)
        return 1
    except OSError as e:
        print(f"Could not write file: {e}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
