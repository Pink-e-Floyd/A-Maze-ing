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
    """Validated maze configuration."""
    width: int
    height: int
    entry: tuple[int, int]
    exit_: tuple[int, int]
    output_file: str
    perfect: bool
    seed: int | None = None


def load_config(path: str) -> Config:
    """Read the config in the path file, calls the parser functions,
    and validate the coordinates."""
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
    """..."""
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
    """Convert raw to int or raise ConfigError."""
    try:
        return int(raw)
    except ValueError:
        raise ConfigError(f"line {line}: {key} must be an integer,"
                          f" got {raw!r}") from None


def _parse_coord(key: str, raw: str, line: int) -> tuple[int, int]:
    """Convert raw to x,y or raise ConfigError."""
    value = raw.split(",")
    if len(value) == 2:
        x = _parse_int(key, value[0], line)
        y = _parse_int(key, value[1], line)
        return (x, y)
    raise ConfigError(f"line {line}: {key} must be 'x,y',"
                      f" got {raw!r}")


def _parse_bool(key: str, raw: str, line: int) -> bool:
    """Convert raw to bool or raise ConfigError."""
    value = raw.lower()
    if value == "true":
        return True
    if value == "false":
        return False
    raise ConfigError(f"line {line}: {key} must be True or False,"
                      f" got {raw!r}")
