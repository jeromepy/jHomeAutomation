import asyncio
import datetime
import Meteo_BME280


class MeteoHandler:

    def __init__(self):

        self.is_running = False

        self.bme280 = Meteo_BME280.BME280()

    async def record_loop(self):

        self.is_running = True

        while self.is_running:

            # read data and push
            temp, press, hum = self.bme280.readBME280All()
            print(f"Meteo data: {temp:.2f} °C, {press:.3f} mbar, {hum:.1f} % rel. hum.")

            await asyncio.sleep(60)
