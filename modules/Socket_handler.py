import asyncio
import datetime
import modules.PriorityQueue as PriorityQueue
import socket

JHOMESERVER_ADRESS = "192.168.1.100"
JHOMESERVER_PORT = 40000


class SocketHandler:

    def __init__(self):

        self.is_running = False
        self.queue_link = None
        self.comm_queue = PriorityQueue.PriorityQueue()
        self.comm = None

    def link_queue(self, queue_object: PriorityQueue.PriorityQueue()):
        self.queue_link = queue_object

    def get_comm_queue_link(self):
        return self.comm_queue

    async def socket_loop(self):

        self.is_running = True

        while self.is_running:

            if self.comm_queue.length() > 0:
                comm_task = self.comm_queue.pop()

            # do socket stuff
            await asyncio.sleep(5)
