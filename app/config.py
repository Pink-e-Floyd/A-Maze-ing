from dataclasses import dataclass

class ConfigError(Exception):
    pass


@dataclass(frozen=True)
class Config:
    width: int
    height: int
    entry: tuple[int, int]
    exit: tuple[int, int]
    output_file: str
    perfect: bool
    seed: int | None = None


def load_config(path: str) -> Config:
    pass


def _read_pairs(lines: list[str]) -> dict[str, tuple[str, int]]:
    pass


def _parse_int(key: str, rae: str, line: int) -> int:
    pass


def _parse_coord(key: str, raw: str, line: int) -> tuple[int, int]:
    pass


def _parse_bool(key: str, raw:str, line: int) -> bool:
    pass