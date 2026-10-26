from dataclasses import dataclass


VALID_KEYS = ["WIDTH", "HEIGHT", "ENTRY", "EXIT", "OUTPUT_FILE",
              "PERFECT", "SEED"]


class ConfigError(Exception):
    """Raised when the configuration file is missing or invalid."""
    pass


@dataclass(frozen=True)
class Config:
    """Validated maze configuration."""
    width: int
    height: int
    entry: tuple[int, int]
    exit: tuple[int, int]
    output_file: str
    perfect: bool
    seed: int | None = None


def load_config(path: str) -> Config:
    """..."""
    pass


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
    """..."""
    pass


def _parse_coord(key: str, raw: str, line: int) -> tuple[int, int]:
    """..."""
    pass


def _parse_bool(key: str, raw: str, line: int) -> bool:
    """..."""
    pass
