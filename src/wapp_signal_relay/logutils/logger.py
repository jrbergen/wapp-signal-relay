from __future__ import annotations

import functools
import inspect
import logging
from logging.handlers import RotatingFileHandler
import re
import sys
from enum import Enum
from pathlib import Path
from typing import Any, Iterable, Optional, Union

from settings import LogSettings


class ColoredFormatter(logging.Formatter):
    def __init__(self, msg: str, use_color=True):
        """
        Class to format log messages with colors. (e.g. ``DEBUG`` and ``INFO`` level messages w/ different colors
        in the terminal).
        """
        logging.Formatter.__init__(self, msg)
        self.use_color = use_color

    def format(self, record: logging.LogRecord):
        levelname = record.levelname
        if self.use_color:
            try:
                # noinspection PyTypeChecker
                levelname_color = ''.join([Color.COLOR_SEQ.value % (30 + getattr(Color, levelname).value),
                                           levelname, Color.RESET_SEQ.value])
                record.levelname = levelname_color
            except AttributeError:
                print(f"Error:  color was not found for log level: {levelname!r}", file=sys.stderr)
                record.levelname = levelname
        return logging.Formatter.format(self, record)


class FileHandlerWithoutANSICodes(RotatingFileHandler):

    COLOR_REX: re.Pattern = re.compile(r'\x1b\[[0-9;]+m')

    # noinspection PyPep8Naming
    def __init__(self,
                 filename: str,
                 mode: str = 'a',
                 maxBytes: int = 0,
                 backupCount: int = 0,
                 encoding: str = None,
                 delay: bool = False):
        """
        Extends logging.handlers.RotatingFileHandler; behaves exactly like it apart from filtering
         ANSI color codes from record.levelname, record.message,
          and record.msg before passing them on
        """
        super().__init__(filename=filename, mode=mode, maxBytes=maxBytes, backupCount=backupCount,
                         encoding=encoding, delay=delay)

    def emit(self, record: logging.LogRecord):
        """
        Remove ANSI codes from record, and then emit it.

        If the stream was not opened because 'delay' was specified in the
        constructor, open it before calling the superclass's emit.
        """
        record.levelname = self.COLOR_REX.sub('', record.levelname)
        record.message = self.COLOR_REX.sub('', record.message)
        record.msg = self.COLOR_REX.sub('', record.msg)
        super().emit(record)


def get_console_handler() -> logging.StreamHandler:
    """
    Get console handler for logger
    """
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(ColoredFormatter(LogSettings.FORMAT_TTY))
    return console_handler


def get_rotating_file_handler(log_path: Path = LogSettings.LOG_PATH,
                              write_mode: str = LogSettings.WRITEMODE,
                              max_bytes: int = LogSettings.ROTATING_MAX_BYTES,
                              backupcount: int = LogSettings.ROTATING_N_BACKUPS,
                              encoding: str = LogSettings.ENCODING):
    """
    Get a rotating file handler for logger
    :param log_path: (Optional) path to store application logs. (Default = LogSettings.LOG_PATH)
    :param write_mode: (Optional) 'w' for write, 'a' for append, etc. (Default = LogSettings.WRITE_MODE)
    :param max_bytes: (Optional) size of log file before rollover occurs
        (Default = LogSettings.ROTATING_LOG_MAX_BYTES)
    :param backupcount: (Optional) integer number of backups to retain after log file rollover.
    :param encoding: (Optional) encoding to use (Default = LogSettings.ENCODING)
    """
    try:
        LogSettings.LOG_PATH.parent.mkdir(exist_ok=True, parents=True)
    except PermissionError as err:
        print(f"No permission to create log file directory / save log file: {err}")
        raise SystemExit(1)

    file_handler = FileHandlerWithoutANSICodes(str(log_path),
                                               maxBytes=max_bytes,
                                               backupCount=backupcount,
                                               mode=write_mode,
                                               encoding=encoding)
    file_handler.setFormatter(logging.Formatter(LogSettings.FORMAT_FILE))
    return file_handler


def get_cls_defining_method(meth):
    if isinstance(meth, functools.partial):
        # noinspection PyTypeChecker
        return get_cls_defining_method(meth.func)
    if inspect.ismethod(meth) or (inspect.isbuiltin(meth)
                                  and getattr(meth, '__self__', None) is not None
                                  and getattr(meth.__self__, '__class__', None)):
        for cls in inspect.getmro(meth.__self__.__class__):
            if meth.__name__ in cls.__dict__:
                return cls
        meth = getattr(meth, '__func__', meth)  # fallback to __qualname__ parsing
    if inspect.isfunction(meth):
        cls = getattr(inspect.getmodule(meth),
                      meth.__qualname__.split('.<locals>', 1)[0].rsplit('.', 1)[0],
                      None)
        if isinstance(cls, type):
            return cls
    return getattr(meth, '__objclass__', None)  # handle special descriptor objects


def get_logger(instance_or_name: Union[str, type], log_level: Optional[str] = None):
    """
    Obtain logger instance
    """

    log_level = log_level or LogSettings.LEVEL

    if type(instance_or_name) == str:
        logger_name = instance_or_name
    else:
        logger_name = type(instance_or_name).__name__
        if logger_name == 'type':
            logger_name = instance_or_name.__name__

    logger = logging.getLogger(logger_name)
    logger.addHandler(get_console_handler())
    logger.addHandler(get_rotating_file_handler())
    logger.propagate = False
    possible_levels = dict(debug=logging.DEBUG, info=logging.INFO,
                           warning=logging.WARNING, error=logging.ERROR)

    if log_level not in possible_levels:
        _lvlmsgpart = " or ".join([f"'{key}'" for key in possible_levels])
        raise ValueError(f"Log level should be {_lvlmsgpart}, not {log_level}")
    logger.setLevel(possible_levels[log_level])
    return LoggerWrapper(logger)


class LoggerWrapper(logging.Logger):

    # noinspection PyMissingConstructor
    def __init__(self, base_logger: logging.Logger):
        self.__class__ = type(base_logger.__class__.__name__,
                              (self.__class__, base_logger.__class__),
                              {})
        self.__dict__ = base_logger.__dict__

    def warning(self, msg, *args, **kwargs):
        return super().warning(self.add_caller_info(msg), *args, **kwargs)

    def info(self, msg, *args, **kwargs):
        return super().info(self.add_caller_info(msg), *args, **kwargs)

    def debug(self, msg, *args, **kwargs):
        return super().debug(self.add_caller_info(msg), *args, **kwargs)

    def error(self, msg, *args, **kwargs):
        return super().error(self.add_caller_info(msg), *args, **kwargs)

    @staticmethod
    def add_caller_info(msg):
        parentframe = inspect.stack()[2][0]
        caller_name = parentframe.f_code.co_name
        lineno = parentframe.f_lineno
        filename = Path(parentframe.f_code.co_filename).name
        try:
            cls_str = f"{parentframe.f_locals['self'].__class__.__name__}."
        except KeyError:
            cls_str = ''
        return f'[{filename}: {lineno}] {cls_str}{caller_name}: {msg} '


def errmsg(msg: Union[Iterable[str], str], cls_or_instance: Optional[Any] = None) -> str:
    if type(msg) == str:
        msg = msg.replace('\n', ' ')
        return f"{errprefix(cls_or_instance)} {msg}"
    else:
        return ' '.join(line.replace('\n', ' ') for line in msg)


def errprefix(cls_or_instance: Optional[Any] = None) -> str:
    if cls_or_instance is None:
        return f"{inspect.currentframe().f_back.f_code.co_name}():"
    else:
        return f"{clsname(cls_or_instance)}.{inspect.currentframe().f_back.f_code.co_name}():"


def clsname(cls_or_instance: Any) -> str:
    if inspect.isclass(cls_or_instance):
        return cls_or_instance.__name__
    else:
        return type(cls_or_instance).__name__


def funcname() -> str:
    return inspect.currentframe().f_back.f_code.co_name


class Color(Enum):
    BLACK = 0
    RED = ERROR = 1
    GREEN = PATH = 2
    YELLOW = WARNING = NUMBER = ORANGE = 3
    BLUE = IDENTITY = 4
    MAGENTA = CRITICAL = PURPLE = ACTION = 5
    CYAN = DEBUG = DESCRIPTION = 6
    PINK = INFO = NORMAL = 7

    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    RESET_SEQ = ENDC = "\033[0m"
    COLOR_SEQ = "\033[1;%dm"
