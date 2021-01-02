import asyncio
import datetime
import os
import modules.Relay_Handler as RelayHandler
import modules.PriorityQueue as PriorityQueue
import modules.Meteo_handler as MeteoHandler
import modules.Socket_handler as SocketHandler

GPIO_RELAY_PIN = 17
COM_PORT = 40000

"""
jHomeRelay
@author: Jerome Leibacher, 2020
This code is for the design jHomeRelay Node.
The hardware consists of a Raspberry Pi 0, an Grove Relay 250V - 10A and an BME280 meteo sensor.
"""


class JHomeRelay(object):

    def __init__(self):

        self._relay_time_schedule = dict()
        self._rules = dict()
        self._relay_tasks = dict()
        self.task_queue = PriorityQueue.PriorityQueue()

        # temporary fixed rule-book (for testing)
        self.rules = {"X24B2": {"name": "timer_1", "trigger": {"time": {"start": "18:30", "end": "18:45"}},
                       "action": {"do": "ON", "block": False, "time": 60}}}
        self._relay_time_schedule["fixed"] = {"time": 5}

        # setup relay_handler
        self._relay_handler = RelayHandler.RelayHandler()
        self._relay_handler.set_gpio_pin(GPIO_RELAY_PIN)

        # queue object of socket_handler
        self.socket_queue = None

    def set_comm_queue_link(self, comm_queue):
        self.socket_queue = comm_queue

    async def start_event_loop(self):
        is_running = True

        while is_running:

            ### handle task_queue things ###
            while self.task_queue.length() > 0:
                n_task = self.task_queue.pop()
                self.process_task(n_task)

            ### handle relay things ###
            n_time = datetime.datetime.now()
            if len(self._rules) > 0:

                pos_action = self.check_rules(n_time)
                if pos_action:
                    print(f'Action started -> {pos_action.get("id", "")}')
                    self._relay_tasks["start"] = pos_action.get("start")
                    self._relay_tasks["stop"] = pos_action.get("stop")

            if "start" in self._relay_tasks:
                if self._relay_tasks.get("start") < n_time:
                    self._relay_handler.close_relay()
                    # remove start task
                    self._relay_tasks.pop("start")

            if "stop" in self._relay_tasks:
                if self._relay_tasks.get("stop") < n_time:
                    self._relay_handler.open_relay()
                    # remove stop task
                    self._relay_tasks.pop("stop")

            await asyncio.sleep(1)

        # end of script -> do cleanup
        self._relay_handler.do_cleanup()

    def process_task(self, n_task):

        meteo_path = "home/pi/Documents/jHomeAutomation/meteotest.txt"

        if "type" in n_task:
            print("Received Task type: " + n_task.get("type"))
            if n_task.get("type") == "meteo":
                if not os.path.exists(meteo_path):
                    with open(meteo_path, "w") as init_file:
                        init_file.write("Origin, Temp (C), Pressure (mbar), Rel.hum. (%)\n")
                with open(meteo_path, "a") as meteo_file:
                    meteo_file.write('{origin}, {temperature:.2f}, {humidity:.1f}, {pressure:.2f}'.format(**n_task))

    def check_rules(self, n_time: datetime.datetime):

        n_time_hour = n_time.time()
        time_action = None
        event_action = None

        for ident, rule in enumerate(self._rules):
            if "time" in rule.get("trigger", ""):
                start_time = datetime.datetime.strptime(rule["time"]["start"], "%H:%M")
                end_time = datetime.datetime.strptime(rule["time"]["end"], "%H:%M")
                if n_time_hour > start_time.time():
                    time_action = dict()
                    print(f'Timer-Event {ident} triggered at {n_time}')
                    time_action["id"] = ident
                    if rule["action"]["do"] == "ON":
                        time_action["start"] = n_time
                        time_action["stop"] = n_time + (end_time - start_time)
                        if start_time > end_time:
                            time_action["stop"] += datetime.timedelta(days=1)
                    elif rule["action"]["do"] == "OFF":
                        time_action["stop"] = n_time
                        if rule["action"]["block"]:
                            time_action["stop_block"] = rule["action"]["time"]
            elif "event" in rule.get("trigger", ""):
                if "rel" in rule["trigger"]["event"].get("type", ""):
                    pass
                if "abs" in rule["trigger"]["event"].get("type", ""):
                    pass

        # check different actions according to priority
        # highest to lowest: OFF-blockings, time-based, event-based
        if time_action:
            return time_action
        if event_action:
            return event_action
        return None


async def main():

    main_loop = JHomeRelay()
    meteo_loop = MeteoHandler.MeteoHandler()
    meteo_loop.link_queue(main_loop.task_queue)
    socket_loop = SocketHandler.SocketHandler()
    socket_loop.link_queue(main_loop.task_queue)
    main_loop.set_comm_queue_link(socket_loop.get_comm_queue_link())

    main_task = loop.create_task(main_loop.start_event_loop())
    meteo_task = loop.create_task(meteo_loop.record_loop())
    socket_task = loop.create_task(socket_loop.socket_loop())

    await asyncio.wait([main_task, meteo_task, socket_task])
    return True


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(main())
    except KeyboardInterrupt:
        print("Keyboard interrupted happened -> loop will be closed...")
    finally:
        loop.close()
