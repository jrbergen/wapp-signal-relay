from __future__ import annotations

from src.wapp_signal_relay.checks import pre_launch_checks
from src.wapp_signal_relay.credential_handling import get_signal_id


async def main_async():
    ...


def main():
    pre_launch_checks()

    id = get_signal_id()


if __name__ == '__main__':

    main()

    #raise NotImplementedError("Project in planning phase.")

