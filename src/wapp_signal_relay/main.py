import shutil
import sys
import time
from pathlib import Path
import asyncio
from typing import Optional, Union
import subprocess
import aiohttp
import uvicorn
import contextlib
import time
import threading

from webwhatsapi import WhatsAPIDriver, UserChat
from webwhatsapi.objects.message import Message
from config import LogCfg, WSRCfg
from loggermodule import get_logger
from src.wapp_signal_relay.io_handling import get_nonexisting_target_path
from pydbus import SystemBus
from gi.repository import GLib

UVICORN_PORT = 34833
UVICORN_ADDR = "127.0.0.1"

logger = get_logger(__name__, logcfg=LogCfg())


def get_init_wsr_cfg(**kwargs):
    return WSRCfg(**kwargs)


def copy_qr_to_local_dir(qr_src_path: Union[Path, str], cfg):

    persistent_qr_path: Path = cfg.IO.QR_DIR / Path(qr_src_path).name
    logger.debug('copying temporary QR path: %r to persistent QR path: %r',
                 qr_src_path, str(persistent_qr_path))

    if qr_src_path.exists():
        shutil.copy(src=qr_src_path,
                    dst=get_nonexisting_target_path(persistent_qr_path))
        logger.debug("QR code copied succesfully.")

    logger.info("Waiting for client to connect using QR code...")


def ensure_directory_existence(cfg: WSRCfg):
    for dirname in ('WSR_DIR', 'QR_DIR'):
        curdir = getattr(cfg.IO, dirname)
        curdir.mkdir(exist_ok=True, parents=True)


def save_qr(driver: WhatsAPIDriver, cfg: WSRCfg):

    qr_path_tmp = Path(driver.get_qr()).absolute()

    if qr_path_tmp.exists():
        copy_qr_to_local_dir(qr_src_path=qr_path_tmp, cfg=cfg)


def init_driver(cfg: WSRCfg, browser_client: str = 'firefox') -> WhatsAPIDriver:
    driver = WhatsAPIDriver(client=browser_client, username=cfg.USERNAME, logger=logger)
    #ensure_directory_existence(cfg=cfg)
    #save_qr(driver=driver, cfg=cfg)

    return driver


def get_chat(driver: WhatsAPIDriver, contains: str = 'RelayTestWapp') -> Union[UserChat, None]:
    chats = driver.get_all_chats()
    ret_chat = None
    for chat in chats:
        if contains in chat.name:
            ret_chat = chat
            logger.info("Found chat %r containing %r.", chat.name, contains)
            break
    else:
        logger.error("No chat found containing %r...", contains)
    return ret_chat


async def handle_unread(chat: UserChat) -> Union[None, list[Message]]:

    msgs = chat.get_unread_messages()
    if msgs:
        return msgs
    else:
        return None





def connect_and_get_driver_wapp(login_timeout_qr=180) -> WhatsAPIDriver:
    wsr_cfg = get_init_wsr_cfg()

    start_time = time.time()
    driver = init_driver(cfg=wsr_cfg)

    driver.wait_for_login(timeout=login_timeout_qr)

    while not driver.is_logged_in():
        wait_time = time.time() - start_time
        logger.info("Waited %d seconds for web Whatsapp login to complete (timeout = %d seconds)...",
                    round(wait_time),
                    login_timeout_qr)

        time.sleep(3)
        if wait_time > login_timeout_qr:
            raise TimeoutError("Web whatsapp login request timed out")

    logger.info("Logged into web Whatsapp!")

    return driver






def register_signal():
    pass

    #selected_chat.send_message("TEST")

#def msgRcv (timestamp, source, groupID, message, attachments):
  # print("Message", message, "received in group", signal.getGroupName (groupID))
#
#
#
#
# bus = SystemBus()
# loop = GLib.MainLoop()
#
# signal = bus.get('org.asamk.Signal')
#
# signal.onMessageReceived = msgRcv
# loop.run()

class UviServer(uvicorn.Server):

    def install_signal_handlers(self):
        pass

    @contextlib.contextmanager
    def run_in_thread(self):
        thread = threading.Thread(target=self.run)
        thread.start()
        try:
            while not self.started:
                time.sleep(1e-3)
            yield
        finally:
            self.should_exit = True
            thread.join()


class SignalUviClient:

    def __init__(self, host: str, port: int, eventloop: asyncio.AbstractEventLoop):
        self.host = host
        self.port = port
        self.eventloop=eventloop


    async def register(self, number: str):
        msg = {"type": "http",
        "method": "POST",
        "scheme": "https",
        "server": (self.host, self.port),
        "path": f"/register/{number}/link",
        "headers": [],
        }


async def main(driver: WhatsAPIDriver, event_loop: asyncio.AbstractEventLoop):
    chat = get_chat(contains='RelayTestWapp', driver=driver)
    uvi_client = SignalUviClient(host=UVICORN_ADDR, port=UVICORN_PORT, eventloop=eventloop)

    while True:
        get_unread = event_loop.create_task(handle_unread(chat))

        await asyncio.sleep(2)
        await asyncio.gather(get_unread)

if __name__ == '__main__':


    logger.info("Starting signal CLI rest API...")

    uvi_config = uvicorn.Config("signal_cli_rest_api.main:app", host=UVICORN_ADDR, port=UVICORN_PORT, log_level='info',
                                loop="asyncio")
    uvi_server = UviServer(config=uvi_config)


    with uvi_server.run_in_thread():

        logger.info("Started signal CLI rest API...")
        driver = connect_and_get_driver_wapp()
        eventloop = None
        try:
            eventloop = asyncio.get_event_loop()

            eventloop.run_until_complete(main(driver=driver, event_loop=eventloop))
        except Exception:
            raise
        finally:
            if eventloop:
                eventloop.close()