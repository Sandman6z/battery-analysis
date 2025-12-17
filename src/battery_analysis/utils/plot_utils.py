import math
import matplotlib.pyplot as plt
from battery_analysis.utils.exception_type import BatteryAnalysisException

def set_plt_axis(battery_type, max_xaxis):
    if battery_type == "Coin Cell":
        plt.axis([10, 600, 1, 3])
        x_ticks = [10, 100, 200, 300, 400, 500, 600]
    elif battery_type == "Pouch Cell":
        maxTicks = math.ceil(max_xaxis/100)*100
        plt.axis([20, maxTicks, 1, 3])
        x_ticks = [20]
        if maxTicks <= 1000:
            for i in range(1, 11):
                x_ticks.append(i*100)
                if i*100 >= maxTicks:
                    break
        elif maxTicks <= 2000:
            for i in range(1, 11):
                x_ticks.append(i*200)
                if i*200 >= maxTicks:
                    break
        elif maxTicks <= 3000:
            for i in range(1, 11):
                x_ticks.append(i*300)
                if i*300 >= maxTicks:
                    break
        elif maxTicks <= 4000:
            for i in range(1, 11):
                x_ticks.append(i*400)
                if i*400 >= maxTicks:
                    break
        else:
            for i in range(1, 11):
                x_ticks.append(i*500)
                if i*500 >= maxTicks:
                    break
    else:
        raise BatteryAnalysisException("[Plt LoadVoltageOverCharge Error]: Unknown battery type")
    plt.xticks(x_ticks)
