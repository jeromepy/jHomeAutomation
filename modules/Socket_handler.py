import asyncio
import datetime
import socket


class SocketHandler:

    def __init__(self):

        self.is_running = False

        self.comm = None

    async def socket_loop(self):

        self.is_running = True

        while self.is_running:

            # do socket stuff
            print(f"Doing socket stuff...")
            await asyncio.sleep(5)
