import shutil
from pathlib import Path
import asyncio
from typing import Optional, Union

import time


from webwhatsapi import WhatsAPIDriver, UserChat
from webwhatsapi.objects.message import Message
from config import LogCfg, WSRCfg
from loggermodule import get_logger
from src.wapp_signal_relay.io_handling import get_nonexisting_target_path
from dbus_next.aio import MessageBus
from dbus_next import MessageType, BusType, Message, Variant


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


class SignalClient:

    def __init__(self, eventloop: asyncio.AbstractEventLoop):
        self.bus = None
        self.loop = eventloop

    async def start(self):
        self.bus = await MessageBus(bus_type=BusType.SYSTEM,
                                    bus_address='org.asamk.signal').connect()
        #self.signal = self.bus.get('org.asamk.Signal')

    def register(self):
        pass#regmsg = Message(destination='org.asamk.signal',
                        # )

    async def send(self):
        ...#self.signal


async def main(driver: WhatsAPIDriver, signalclient: SignalClient, event_loop: asyncio.AbstractEventLoop):
    #chat = get_chat(contains='RelayTestWapp', driver=driver)
    await signalclient.start()

    while True:
        #get_unread = event_loop.create_task(handle_unread(chat))

        await asyncio.sleep(2)
        #await asyncio.gather(get_unread)


if __name__ == '__main__':

    eventloop = asyncio.get_event_loop()

    logger.info("Starting Signal client")
    scli = SignalClient(eventloop=eventloop)

    #driver = connect_and_get_driver_wapp()
    driver = None
    try:
        eventloop.run_until_complete(main(driver=driver, signalclient=scli, event_loop=eventloop))
    except Exception:
        raise
    finally:
        if eventloop:
            eventloop.close()
