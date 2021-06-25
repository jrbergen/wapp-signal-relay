import os
from pathlib import Path
from typing import Union


class DirNames:
    DIRNAME_SRC: str = 'src'
    DIRNAME_SRC_APP: str = 'wapp_signal_relay'
    DIRNAME_APPDATA: str = '.wapp-signal-relay'
    DIRNAME_TOPLEVEL: str = Path(__file__).parent.name


class FileNames:
    CREDENTIALS: str = 'credentials.py'
    GITIGNORE: str = '.gitignore'
    LOGFILE: str = 'wapp-signal-relay-logfile.log'


class Dirs:
    DIR_ROOT = Path(__file__).parent
    DIR_SRC = DIR_ROOT / DirNames.DIRNAME_SRC
    DIR_SRC_APP = DIR_SRC / DirNames.DIRNAME_SRC_APP
    DIR_APPDATA = Path(os.getenv("HOME")) / DirNames.DIRNAME_APPDATA

    MAKE_IF_NOT_EXIST: tuple[Union[Path, str], ...] = (DIR_APPDATA,)

    @classmethod
    def make_nonexisting(cls):
        for dir_ in cls.MAKE_IF_NOT_EXIST:

            if not isinstance(dir_, Path):
                dir_ = Path(dir_)

            dir_.mkdir(exist_ok=True, parents=True)
            logger.debug("Made non-existing directory %r.", str(dir_))


class CredentialsFile:
    CRED_FILENAME: str = FileNames.CREDENTIALS

    LINES: tuple[str, ...] = (
        "# Ignore credentials.py so it doesn't end up on e.g. github\n",
        f"{CRED_FILENAME}\n"
    )


class FilePaths:

    PATH_CREDENTIALS = Dirs.DIR_ROOT / FileNames.CREDENTIALS
    PATH_GITIGNORE = Dirs.DIR_ROOT / FileNames.GITIGNORE
    PATH_LOG = Dirs.DIR_ROOT / FileNames.LOGFILE


class LogSettings:

    LOG_PATH: Path = FilePaths.PATH_LOG
    """Path to log file"""

    LEVEL: str = 'debug'
    """Determines log verbosity (e.g. 'debug','info','warning','critical','error')"""

    WRITEMODE: str = 'a'
    """'w' for overwriting the log each session, 'a' for appending"""

    # LOG_FORMAT: str = '%(name)s - %(levelname)s — %(message)s'
    FORMAT_TTY: str = '%(levelname)s — %(message)s'
    """Format string for log messages (terminal)"""

    FORMAT_FILE: str = '%(asctime)s — %(name)s — %(levelname)s — %(message)s'
    """Format string for log messages (log file)"""

    ENCODING: str = 'utf-8'
    """Encoding to use for log file"""

    ROTATING_MAX_BYTES: int = 10_000_000
    """Maximum size on disk of logsize before rollover occurs."""

    ROTATING_N_BACKUPS: int = 2
    """Number of logfile backups to retain after rollover."""