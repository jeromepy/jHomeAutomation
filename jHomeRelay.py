import datetime
import modules.Relay_Handler as RelayHandler
import modules.PriorityQueue as PriorityQueue

GPIO_RELAY_PIN = 11
COM_PORT = 40000


class JHomeRelay(object):

    def __init__(self):

        self._relay_time_schedule = dict()
        self._relay_tasks = dict()
        self._task_queue = PriorityQueue.PriorityQueue()

        # temporary fixed time interval of 60 mins
        self._relay_time_schedule["fixed"] = 60

        # start relay_handler
        self._relay_handler = RelayHandler.RelayHandler()
        self._relay_handler.set_gpio_pin(GPIO_RELAY_PIN)

        self.start_event_loop()

    def start_event_loop(self):
        is_running = True
        
        while is_running:

            ### handle task_queue things ###
            while self._task_queue.length() > 0:
                n_task = self._task_queue.pop()
                self.process_task(n_task)

            ### handle relay things ###
            n_time = datetime.datetime.now()
            if len(self._relay_time_schedule) > 0:

                if "fixed" in self._relay_time_schedule:
                    # fixed interval is available -> starting now
                    self._relay_tasks["start"] = n_time
                    self._relay_tasks["stop"] = n_time + \
                                                datetime.timedelta(minutes=self._relay_time_schedule.get("fixed"))

                    # remove entry in time_schedule
                    self._relay_time_schedule.pop("fixed")

                elif "timer" in self._relay_time_schedule:
                    # timed event of relay

                    for event_name, event_info in self._relay_time_schedule["timer"].items():
                        if event_info.get("start") < datetime.datetime.now():
                            # event should be started
                            print("Event " + event_name + " will be started")
                            self._relay_tasks["start"] = event_info.get("start")
                            self._relay_tasks["stop"] = event_info.get("stop")
                            # remove entry from time_schedule
                            self._relay_time_schedule["timer"].pop(event_info)
                            break

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

            ### handle meteo_data
            pass

        # end of script -> do cleanup
        self._relay_handler.do_cleanup()

    def process_task(self, n_task):

        pass

    def init_server_socket(self):

        pass


if __name__ == "__main__":
    jHome = JHomeRelay()
