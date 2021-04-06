import functools
import inspect
import logging
import sys
from pathlib import Path
from typing import Union

from config import LogCfg


class ColoredFormatter(logging.Formatter):
    def __init__(self, logcfg: LogCfg, use_color=True):
        """
        Class to format log messages with colors. (e.g. ``DEBUG`` and ``INFO`` level messages w/ different colors
        in the terminal).
        """
        logging.Formatter.__init__(self, fmt=logcfg.FORMAT)
        self.use_color = use_color
        self.logcfg = logcfg

    def format(self, record):
        levelname: str = record.levelname
        if self.use_color:
            levelname_color = \
                self.logcfg.COLOR_SEQ % (30 + getattr(self.logcfg.LEVEL_COLORS, levelname)) + levelname + LogCfg.RESET_SEQ
            record.levelname = levelname_color
        return logging.Formatter.format(self, record)


def get_console_handler(logcfg: LogCfg):
    """
    Get console handler for logger
    """
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(ColoredFormatter(logcfg))
    return console_handler


def get_file_handler(logcfg: LogCfg):
    """
    Get file handler for logger

    :param log_filename: (Optional) filename to use for log file. (Default = LogCfg.FILENAME)
    """
    log_path = Path(__file__).parent.absolute() / logcfg.FILENAME
    file_handler = logging.FileHandler(filename=log_path, mode=logcfg.WRITEMODE)
    file_handler.setFormatter(logging.Formatter(logcfg.FORMAT))
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


def get_logger(instance_or_name: Union[str, type], logcfg: LogCfg):
    """
    Obtain logger instance
    """

    if type(instance_or_name) == str:
        logger_name = instance_or_name
    else:
        logger_name = type(instance_or_name).__name__
        if logger_name == 'type':
            logger_name = instance_or_name.__name__

    logger = logging.getLogger(logger_name)
    logger.addHandler(get_console_handler(logcfg=logcfg))
    logger.addHandler(get_file_handler(logcfg=logcfg))
    logger.propagate = False
    level = LogCfg.DEFAULT_LEVEL

    possible_levels = dict(debug=logging.DEBUG, info=logging.INFO,
                           warning=logging.WARNING, error=logging.ERROR)

    if level not in possible_levels:
        _lvlmsgpart = " or ".join([f"'{key}'" for key in possible_levels])
        raise ValueError(f"Log level should be {_lvlmsgpart}, not {level}")
    logger.setLevel(possible_levels[level])

    return LoggerWrapper(logger)


class LoggerWrapper(logging.Logger):

    def __init__(self, base_logger):
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


def funcname():
    return inspect.currentframe().f_back.f_code.co_name
