import asyncio
import datetime
import modules.PriorityQueue as PriorityQueue
import socket


class SocketHandler:

    def __init__(self):

        self.is_running = False
        self.queue_link = None
        self.comm = None

    def link_queue(self, queue_object: PriorityQueue.PriorityQueue()):
        self.queue_link = queue_object

    async def socket_loop(self):

        self.is_running = True

        while self.is_running:

            # do socket stuff
            print(f"Doing socket stuff...")
            await asyncio.sleep(5)
