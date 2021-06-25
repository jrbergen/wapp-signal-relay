import getpass
import re
import sys

from ruamel.yaml import YAML

from settings import FilePaths
from checks import check_file_access
from src.wapp_signal_relay.logutils.logger import errmsg, get_logger

logger = get_logger(__name__)


# !TODO update phone number regex
CRED_REX: re.Pattern = re.compile(r''.join(r'[00|+]\d{2}\d{8,12}'))
CRED_KEY: str = 'SIGNAL_ID'


def get_signal_id() -> str:
    ensure_credentials_exist()
    return get_signal_id_or_prompt_new_if_invalid()


def get_signal_id_or_prompt_new_if_invalid() -> str:
    yaml = YAML(typ='safe')

    rewrite_creds = False
    with open(credpath := FilePaths.PATH_CREDENTIALS, 'r') as credentialsfile:
        yamldict = yaml.load(credentialsfile)

        if CRED_KEY not in yamldict or not CRED_REX.match(yamldict[CRED_KEY]) in yamldict:
            logger.debug("Invalid or corrupted Signal ID or missing Signal ID key in %r", credpath.name)
            yamldict |= {CRED_KEY: prompt_signal_id()}
            rewrite_creds = True

    if rewrite_creds:
        with open(credpath, 'w') as credentialsfile:
            yaml.dump(yamldict, credentialsfile)

    return yamldict[CRED_KEY]


def ensure_credentials_exist():

    if not (credpath := FilePaths.PATH_CREDENTIALS).exists():
        yamldict = {CRED_KEY: prompt_signal_id()}

        yaml = YAML(typ='safe')
        with open(credpath, 'w') as credentialsfile:
            yaml.dump(yamldict, credentialsfile)
        logger.debug("Wrote signal user id to credentials file.")


def prompt_signal_id() -> str:

    signal_id_match = False
    while not signal_id_match:
        signal_id: str = getpass.getpass(
            prompt="Input Signal ID (=phone number WITH country prefix)")
        if CRED_REX.match(signal_id):
            break
        if signal_id == 'exit':
            logger.debug("User prompted exit")
            sys.exit(1)
        print("Invalid phone number format. Try again, or type 'exit' to exit program.")
    return signal_id




