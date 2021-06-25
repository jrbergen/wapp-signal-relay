from __future__ import annotations

from src.wapp_signal_relay.checks import pre_launch_checks


async def main_async():
    ...


def main():
    pre_launch_checks()


if __name__ == '__main__':

    main()

    raise NotImplementedError("Project in planning phase.")

