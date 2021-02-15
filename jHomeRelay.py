import asyncio
import datetime
import os
import sys

sys.path.append('/')
import modules.utils as utils
import modules.Relay_Handler as RelayHandler
import modules.PriorityQueue as PriorityQueue
import config
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

        self.recv_mess = PriorityQueue.PriorityQueue()

        # initialize global variables
        config.init()
        config.NOTIFIER.subscribe(self)  # add itself to subscribers

        self._rules = dict()
        self.meteo_state = dict()
        self._relay_tasks = dict()

        # temporary fixed rule-book (for testing)
        self._rules = {"block_hours": {"1": "06:00-08:00", "2": "17:00-19:00"},
                       "des_hum": 37.0, "min_runtime": 60, "min_pause": 180}

        # setup relay_handler
        self._relay_handler = RelayHandler.RelayHandler()
        self._relay_handler.set_gpio_pin(GPIO_RELAY_PIN)

    async def start_event_loop(self):
        is_running = True

        while is_running:

            ### handle received messages ###
            while self.recv_mess.length() > 0:
                n_task = self.recv_mess.pop()
                self.process_mess(n_task)

            ### handle relay things ###
            n_time = datetime.datetime.now()

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
                    if "start" in self._relay_tasks:
                        # remove start action if existing
                        self._relay_tasks.pop("start")

            await asyncio.sleep(1)

        # end of script -> do cleanup
        self._relay_handler.do_cleanup()

    def process_mess(self, n_task):

        meteo_path = "/home/pi/Documents/meteotest.txt"
        event_path = "/home/pi/Documents/eventtest.txt"
        timestamp = utils.get_current_timestamp()
        if "type" in n_task:
            # print("Received Task type: " + n_task.get("type"))
            if n_task.get("type") == "meteo":
                if not os.path.exists(meteo_path):
                    with open(meteo_path, "w") as init_file:
                        init_file.write("Time, Temp (C), Rel.hum. (%), Pressure (mbar)\n")
                with open(meteo_path, "a") as meteo_file:
                    meteo_file.write(
                        timestamp + ', {temperature:.2f}, {humidity:.1f}, {pressure:.2f}\n'.format(**n_task))
            elif n_task.get("type") == "meteo_analysis":
                self.check_meteo_state(n_task.get("mess", None))
            elif n_task.get("type") == "event":
                if not os.path.exists(event_path):
                    with open(event_path, "w") as init_file:
                        init_file.write("Event file of jHomeRelay\n")
                with open(event_path, "a") as event_file:
                    event_file.write(timestamp + ", " +
                                     n_task.get("mess", "Error: Message of given event is not defined") + "\n")

    def check_meteo_state(self, meteo_state: dict):

        """
        This function checks, if the relay should be switched
        :param meteo_state: (dict) containing the meteo analysis
        :return:
        """

        #  print("Given meteo analysis data:")
        #  for key, value in meteo_state.items():
            #  print(f'{key}: {value:.2f}')
        r_state, r_last_close, r_last_open = self._relay_handler.get_relay_state()

        t_now = utils.get_current_time()
        start_humi = False

        # check blocking hour criteria
        for _, blck_hour in self._rules.get("block_hours", []).items():
            td = utils.get_current_day()
            start_time = datetime.datetime.combine(td, datetime.time(hour=int(blck_hour[0:2]),
                                                                     minute=int(blck_hour[3:5])))
            end_time = datetime.datetime.combine(td, datetime.time(hour=int(blck_hour[6:8]),
                                                                   minute=int(blck_hour[9:11])))
            if start_time < t_now < end_time:
                # current time is within blocking hours -> stop if necessary
                if r_state == 1:
                    self._relay_tasks["stop"] = t_now
                    config.NOTIFIER.publish({"type": "event", "mess": f'Reached blocking hours {blck_hour}.'})
                    return
                return

        if r_state == 1:
            # relay is currently closed -> humifier is running
            # check after 30minutes, if humidity is increasing -> if not -> publish empty tank message
            if r_last_close is not None and (t_now - r_last_close) > datetime.timedelta(minutes=30):
                if "dH_20" in meteo_state:
                    if meteo_state.get("dH_20") < 0.005:
                        print("--> Event: Tank is probably empty. Humidity is not increasing during runtime")
                        config.NOTIFIER.publish({"type": "event",
                                                 "mess": f'Tank looks to be emtpy. '
                                                         f'(dH_20 = {meteo_state.get("dH_20"):.3f})'})
            if "dT_10" in meteo_state:
                if meteo_state.get("dT_10") < -0.1:  # Temperature falling more than 1°C/10mins
                    config.NOTIFIER.publish({"type": "event",
                                             "mess": f'Open windows detected (dT_10 = {meteo_state.get("dT_10"):.3f}'})
                    self._relay_tasks["stop"] = t_now
                    return

        elif r_state == 0:
            # relay is currently open
            if r_last_open is not None and \
                    (t_now - r_last_open) < datetime.timedelta(minutes=self._rules.get("min_pause")):
                # still in pause situation -> do nothing
                return
            if "dH_20" in meteo_state:
                if meteo_state.get("dH_20") > 0:
                    # humidity is rising without humifier -> do nothing
                    return
            if "dH_1440" in meteo_state:
                if meteo_state.get("dH_1440") < -0.5 / 1440:  # -0.5% rel.Hum within 24hours
                    print(f'Relay will be closed (dH_1440 < 0.5%) -> {meteo_state.get("dH_1440"):.3f}')
                    start_humi = True
            if "dH_60" in meteo_state:
                if meteo_state.get("dH_60") < -0.3 / 60:  # -0.3% within 60min
                    print(f'Relay will be closed (dH_60< 0.3%) -> {meteo_state.get("dH_60"):.3f}')
                    start_humi = True

        if start_humi:
            self._relay_tasks["start"] = utils.get_current_time()
            self._relay_tasks["stop"] = utils.get_current_time() + \
                                        datetime.timedelta(minutes=self._rules.get("min_runtime"))
            config.NOTIFIER.publish({"type": "event",
                                     "mess": f'Relay closed, running for {self._rules.get("min_runtime")} minutes'})


async def main():
    main_loop = JHomeRelay()
    meteo_loop = MeteoHandler.MeteoHandler()
    socket_loop = SocketHandler.SocketHandler()

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
