import asyncio
import datetime
from collections import deque
import numpy as np
import sklearn.linear_model as LinearRegression
import modules.PriorityQueue as PriorityQueue
import modules.Meteo_BME280 as Meteo_BME280

global NOTIFIER


class MeteoHandler:

    def __init__(self):

        self.is_running = False
        self.recv_mess = PriorityQueue.PriorityQueue()

        NOTIFIER.subscribe(self)

        self.bme280 = Meteo_BME280.BME280()

        # holding data of temperature & humidity of the last 48 hours
        self.temp_data = deque(maxlen=48 * 60)
        self.hum_data = deque(maxlen= 48 * 60)

    async def record_loop(self):

        self.is_running = True

        while self.is_running:

            # read data and push
            temp, press, hum = self.bme280.readBME280All()
            print(f"Meteo data: {temp:.2f} °C, {press:.3f} mbar, {hum:.1f} % rel. hum.")
            task = dict()
            task["type"] = "meteo"
            task["origin"] = "jHomeRelay"
            task["temperature"] = temp
            task["pressure"] = press
            task["humidity"] = hum

            self.temp_data.append(temp)
            self.hum_data.append(hum)

            NOTIFIER.publish(task, {"priority": 1})

            await asyncio.sleep(60)

    def analyze_meteodata(self):
        """
        Create analysis results of temperature and humidity to publish
        Created results (linear regression):
        Temperature change over 10mins (dT_10), 3 hours (dT_180)
        Humidity change over 20min (dH_20), 1 hour (dH_60), 24 hours (dH_1440) and 48 hours (dH_2880)
        If results can not be computed, the values are not returned
        :return: (dict) results with keys as mentioned above
        """

        results = dict()

        calc_dT_coeffs = [10, 180]
        calc_dH_coeffs = [20, 60, 1440, 2880]

        temp_data = np.asarray(self.temp_data)
        hum_data = np.asarray(self.hum_data)

        for calc_dT in calc_dT_coeffs:
            if temp_data.size >= calc_dT:
                x = np.linspace(1, calc_dT, calc_dT).reshape(-1, 1)
                model = LinearRegression.LinearRegression()
                model.fit(x, temp_data[calc_dT:])
                results["dT_" + str(calc_dT)] = model.coef_

        for calc_dH in calc_dH_coeffs:
            if hum_data.size >= calc_dH:
                x = np.linspace(1, calc_dH, calc_dH).reshape(-1, 1)
                model = LinearRegression.LinearRegression()
                model.fit(x, hum_data[calc_dH:])
                results["dH_" + str(calc_dH)] = model.coef_

        # add last values
        if temp_data.size > 0:
            results["dT_last"] = float(temp_data[:1])

        if hum_data.size > 0:
            results["dH_last"] = float(hum_data[:1])

        # Publish results
        if len(results):
            NOTIFIER.publish({"info": "meteo_analysis", "mess": results})
