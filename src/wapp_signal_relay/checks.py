import os
from collections import Iterable
from pathlib import Path
from typing import Union

from settings import CredentialsFile, FileNames, FilePaths
from src.wapp_signal_relay.logutils.logger import errmsg, get_logger

logger = get_logger(__name__)

_ACCESS_CHECKS: dict[str, int] = {
    'w': os.W_OK,
    'r': os.R_OK,
    'f': os.F_OK,
    'x': os.X_OK,
}


def pre_launch_checks() -> None:
    check_gitignore()


def check_gitignore() -> None:
    if not FilePaths.PATH_GITIGNORE.exists():

        logger.debug("Did not find .gitignore file: creating one for credentials")
        check_gitignore_write_permission()

        with open(FilePaths.PATH_GITIGNORE, 'a') as gitignore_file:
            gitignore_file.writelines(CredentialsFile.LINES)

    else:
        with open(FilePaths.PATH_GITIGNORE, 'r') as gitignore_file:
            credentials_line_missing = \
                not any(line.startswith(FileNames.CREDENTIALS) for line in gitignore_file)

            if credentials_line_missing:
                logger.debug("No %r entry in %r file. Adding one.",
                             CredentialsFile.CRED_FILENAME,
                             FileNames.GITIGNORE)

        if credentials_line_missing:
            check_gitignore_write_permission()

            with open(FilePaths.PATH_GITIGNORE, 'a') as gitignore_file:
                gitignore_file.writelines(lines=CredentialsFile.LINES)
        else:
            logger.debug("Found %r exclusion in %r: OK",
                         CredentialsFile.CRED_FILENAME, FileNames.GITIGNORE)


def check_gitignore_write_permission() -> None:
    check_file_access(FilePaths.PATH_GITIGNORE, 'w',
                      custom_err=["no permission to write to .gitignore file;",
                                  "cannot guarantee credentials.py not being uploaded."])


def check_file_access(path: Path, checkstr: str,
                      custom_err: Union[None, str, Iterable[str]] = None) -> None:
    for check in checkstr:
        if not os.access(path, _ACCESS_CHECKS[checkstr]):
            custom_err = custom_err or f"No permission for file operation: {check!r}."
            raise PermissionError(errmsg(custom_err))
    logger.debug(f"Access checks {', '.join(f'{x!r}' for x in checkstr)} OK.")
