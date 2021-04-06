import os
from collections import namedtuple
from dataclasses import dataclass, field
from enum import IntEnum, unique
from pathlib import Path
from typing import NamedTuple


@dataclass(frozen=True)
class IOConfig:
    WSR_DIRNAME: str = 'wapp-signal-relay'
    WSR_DIR: Path = Path(os.getenv("HOME")).absolute().joinpath(WSR_DIRNAME)
    QR_DIRNAME: str = 'qr_codes'
    QR_DIR: Path = Path(WSR_DIR).absolute() / QR_DIRNAME


@unique
class LogColors(IntEnum):
    """Enum for colors"""
    BLACK = 0
    RED = 1
    GREEN = 2
    YELLOW = 3
    BLUE = 4
    MAGENTA = 5
    CYAN = 6
    WHITE = 7


@dataclass(frozen=True)
class LevelColors:
    DEBUG = LogColors.GREEN
    INFO = LogColors.BLUE
    WARNING = LogColors.YELLOW
    CRITICAL = LogColors.MAGENTA
    ERROR = LogColors.RED


@dataclass(frozen=True, eq=True)
class LogCfg:
    """Configuration class for logging functionality"""
    FILENAME: str = 'wapp_signal_log.log'
    FORMAT: str = '%(levelname)s — %(message)s'
    WRITEMODE: str = 'w'
    DEFAULT_LEVEL = 'debug'
    RESET_SEQ: str = "\033[0m"
    COLOR_SEQ: str = "\033[1;%dm"
    BOLD_SEQ: str = "\033[1m"
    LEVEL_COLORS: LevelColors = field(default_factory=LevelColors)


@dataclass(frozen=True, eq=True)
class WSRCfg:
    """Main Whatsapp Signal Relay config object. Immutable."""

    USERNAME: str = 'WappSignalRelay'
    CLIENT: str = 'firefox'
    LOADSTYLES: bool = False
    IO: IOConfig = field(default_factory=IOConfig)
