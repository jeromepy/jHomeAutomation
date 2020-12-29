import asyncio
import datetime
import modules.PriorityQueue as PriorityQueue
import modules.Meteo_BME280 as Meteo_BME280


class MeteoHandler:

    def __init__(self):

        self.is_running = False
        self.queue_link = None

        self.bme280 = Meteo_BME280.BME280()

    def link_queue(self, queue_object: PriorityQueue.PriorityQueue()) -> None:
        self.queue_link = queue_object

    async def record_loop(self):

        self.is_running = True

        while self.is_running:

            # read data and push
            temp, press, hum = self.bme280.readBME280All()
            print(f"Meteo data: {temp:.2f} °C, {press:.3f} mbar, {hum:.1f} % rel. hum.")
            task = dict()
            task["type"] = "meteodata"
            task["origin"] = "jHomeRelay"
            task["temperature"] = temp
            task["pressure"] = press
            task["humidity"] = hum

            if self.queue_link is not None:
                self.queue_link.push(task, 1)

            await asyncio.sleep(60)
