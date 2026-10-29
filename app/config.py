"""Read and validate the A-Maze-ing configuration file."""

from dataclasses import dataclass


MANDATORY_KEYS = ["WIDTH", "HEIGHT", "ENTRY", "EXIT", "OUTPUT_FILE",
                  "PERFECT"]
VALID_KEYS = MANDATORY_KEYS + ["SEED"]
MIN_SIZE = 2
MAX_SIZE = 200


class ConfigError(Exception):
    """Raised when the configuration file is missing or invalid."""


@dataclass(frozen=True)
class Config:
    """Validated maze configuration.

    Attributes:
        width: Number of columns of the maze.
        height: Number of rows of the maze.
        entry: (x, y) of the entry cell.
        exit_: (x, y) of the exit cell.
        output_file: Path of the file where the maze is written.
        perfect: True for a perfect maze, False for a maze with loops.
        seed: Random seed, or None for a random maze.
    """

    width: int
    height: int
    entry: tuple[int, int]
    exit_: tuple[int, int]
    output_file: str
    perfect: bool
    seed: int | None = None


def load_config(path: str) -> Config:
    """Read, parse and validate a configuration file.

    Args:
        path: Path of the configuration file.

    Returns:
        The validated configuration.

    Raises:
        ConfigError: If the file cannot be read, a mandatory key is
            missing, a value is invalid, the size is out of range, the
            entry or exit is outside the maze, entry equals exit, or
            the seed is negative.
    """
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = f.read()
    except OSError as e:
        raise ConfigError(f"Error reading {path!r}: {e.strerror}") from None
    except UnicodeDecodeError:
        raise ConfigError(f"The file: {path!r} needs to be"
                          " a text file") from None
    lines = data.split("\n")
    pairs = _read_pairs(lines)
    missing_keys: list[str] = []
    for key in MANDATORY_KEYS:
        if key not in pairs:
            missing_keys.append(key)
    if missing_keys:
        missing = ", ".join(missing_keys)
        raise ConfigError(f"Missing mandatory key(s): {missing}")
    raw, line = pairs["WIDTH"]
    width = _parse_int("WIDTH", raw, line)
    raw, line = pairs["HEIGHT"]
    height = _parse_int("HEIGHT", raw, line)
    raw, line = pairs["ENTRY"]
    entry = _parse_coord("ENTRY", raw, line)
    raw, line = pairs["EXIT"]
    exit_ = _parse_coord("EXIT", raw, line)
    raw, line = pairs["PERFECT"]
    perfect = _parse_bool("PERFECT", raw, line)
    output_file = pairs["OUTPUT_FILE"][0]
    seed: int | None = None
    if "SEED" in pairs:
        raw, line = pairs["SEED"]
        seed = _parse_int("SEED", raw, line)
    if not MIN_SIZE <= width <= MAX_SIZE:
        raise ConfigError(f"Expected 'WIDTH' between {MIN_SIZE} and"
                          f" {MAX_SIZE}, received: {width!r}")
    if not MIN_SIZE <= height <= MAX_SIZE:
        raise ConfigError(f"Expected 'HEIGHT' between {MIN_SIZE} and"
                          f" {MAX_SIZE}, received: {height!r}")
    x, y = entry
    if not 0 <= x < width or not 0 <= y < height:
        raise ConfigError(f"'ENTRY' {entry} is outside a"
                          f" {width}x{height} maze!")
    x, y = exit_
    if not 0 <= x < width or not 0 <= y < height:
        raise ConfigError(f"'EXIT' {exit_} is outside a"
                          f" {width}x{height} maze!")
    if entry == exit_:
        raise ConfigError("'ENTRY' and 'EXIT' need to be different!")
    if seed is not None and seed < 0:
        raise ConfigError("'SEED' need to be positive or 0")
    return Config(width=width, height=height, entry=entry, exit_=exit_,
                  output_file=output_file, perfect=perfect, seed=seed)


def _read_pairs(lines: list[str]) -> dict[str, tuple[str, int]]:
    """Turn the lines of the file into a dict of raw values.

    Empty lines and lines starting with '#' are ignored. Keys are
    converted to upper case and spaces around keys and values are removed.

    Args:
        lines: Lines of the configuration file.

    Returns:
        A dict mapping each key to (raw value, line number).

    Raises:
        ConfigError: If a line has no '=', the key is unknown or
            duplicated, or the value is empty.
    """
    config: dict[str, tuple[str, int]] = {}
    for number, raw in enumerate(lines, start=1):
        line = raw.strip()
        if line == "" or line.startswith("#"):
            continue
        if "=" not in line:
            raise ConfigError(f"line {number}: expected KEY=VALUE, "
                              f"got {line!r}")
        k, v = line.split("=", 1)
        k = k.strip().upper()
        v = v.strip()
        if k not in VALID_KEYS:
            raise ConfigError(f"line {number}: the key {k!r} is invalid!")
        if not v:
            raise ConfigError(f"line {number}: empty value for {k}!")
        if k in config:
            raise ConfigError(f"line {number}: the key {k!r} is duplicated!")
        config[k] = (v, number)
    return config


def _parse_int(key: str, raw: str, line: int) -> int:
    """Convert a raw value to an int.

    Args:
        key: Name of the key, used in the error message.
        raw: Raw value read from the file.
        line: Line number, used in the error message.

    Returns:
        The value as an int.

    Raises:
        ConfigError: If raw is not an integer.
    """
    try:
        return int(raw)
    except ValueError:
        raise ConfigError(f"line {line}: {key} must be an integer,"
                          f" got {raw!r}") from None


def _parse_coord(key: str, raw: str, line: int) -> tuple[int, int]:
    """Convert a raw 'x,y' value to a coordinate.

    Args:
        key: Name of the key, used in the error message.
        raw: Raw value read from the file, like '0,0'.
        line: Line number, used in the error message.

    Returns:
        The coordinate as (x, y).

    Raises:
        ConfigError: If raw does not have exactly two integers
            separated by a comma.
    """
    value = raw.split(",")
    if len(value) == 2:
        x = _parse_int(key, value[0], line)
        y = _parse_int(key, value[1], line)
        return (x, y)
    raise ConfigError(f"line {line}: {key} must be 'x,y',"
                      f" got {raw!r}")


def _parse_bool(key: str, raw: str, line: int) -> bool:
    """Convert a raw 'True'/'False' value to a bool (any case).

    Args:
        key: Name of the key, used in the error message.
        raw: Raw value read from the file.
        line: Line number, used in the error message.

    Returns:
        The value as a bool.

    Raises:
        ConfigError: If raw is not 'true' or 'false'.
    """
    value = raw.lower()
    if value == "true":
        return True
    if value == "false":
        return False
    raise ConfigError(f"line {line}: {key} must be True or False,"
                      f" got {raw!r}")
