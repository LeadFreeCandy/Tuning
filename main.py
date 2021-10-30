#X axis: [.132, 26.6, .29]

import numpy as np
import tuning
import time
import random as rd
from config import *
from odrive.enums import *

def in_range(val, range):
    return range[0] <= val <= range[1]

class tune:



    def __init__(self,values, cost):
        self.values = values
        self.cost = cost

        max_equal_factor = iteration_shift_factor
        min_equal_factor = 1/max_equal_factor


    def equals(self, other_tune):

        return all(self.min_equal_factor < t/t2 < self.max_equal_factor for t,t2 in zip(self.values, other_tune.values))





def main(start_values):

    costs = []

    tuning.startup(vel_limit, odrive_serial, axis_num)
    absolute_min = float("inf")
    best_values = []
    # tuning.start_liveplotter(lambda:[tuning.axis.controller.config.vel_gain])


    if start_values == []:
        start_values = [tuning.axis.controller.config.vel_gain, tuning.axis.controller.config.pos_gain, tuning.axis.controller.config.vel_integrator_gain]

    tuning.axis.controller.config.vel_gain = start_values[0]
    tuning.axis.controller.config.pos_gain = start_values[1]
    tuning.axis.controller.config.vel_integrator_gain = start_values[2]

    tuning.start_liveplotter(lambda: [tuning.axis.controller.input_pos, tuning.axis.encoder.pos_estimate])

    tuning.axis.controller.input_pos = 0
    time.sleep(3)


    current_values = start_values[:]

    print("press ctrl + c to exit")

    try:
        while True:

            shift = rd.choice([1/iteration_shift_factor, iteration_shift_factor])
            index = rd.randrange(0,3)


            test_values = [i for i in current_values]

            # print(f"test vals b4 = {test_values}")
            test_values[index] *= shift

            # print(f"index = {index}")
            # print(f"test vals after shift = {test_values}")
            # print(f"val = {test_values[index]}, max = {ranges[index][1]}")

            if test_values[index] < ranges[index][0]:
                test_values[index] = ranges[index][0]
            elif test_values[index] > ranges[index][1]:
                test_values[index] = ranges[index][1]

            # print(f"test vals after cieling= {test_values}")

            # print(f"current_values = {current_values}")

            if any(t.equals(test_values) for t in costs):
                print(f"already tested {test_values}")
                continue

            baseline = tuning.evaluate_values(current_values, mov_dist, mov_time, rmse_weight, variance_weight)
            cost = tuning.evaluate_values(test_values, mov_dist, mov_time, rmse_weight, variance_weight)

            # cost = tuning.evaluate_values(values, mov_dist, mov_time, rmse, variance, print)


            cost_delta = cost - baseline
            # print(cost_delta)

            # print(baseline)
            # print(cost)

            # print(f"--shifting with cost delta: {cost_delta}")
            # print(f"--previous values: {current_values}")
            # print(f"--new values: {test_values}")

            # current_values[index] *= shift  # TODO: multipy shift by the magnitude of delta

            if cost_delta < 0:

                current_values[index] *= shift

            else:
                current_values[index] /= shift

            if current_values[index] < ranges[index][0]:
                current_values[index] = ranges[index][0]
            elif current_values[index] > ranges[index][1]:
                current_values[index] = ranges[index][1]

            print(current_values)

            costs.append(tune(current_values, cost))

            if cost < absolute_min:  # TODO: retry to unsure it truly is abs minimum
                # print(f"old absolute_min: {absolute_min}")
                absolute_min = cost
                print(f"new absolute_min: {absolute_min}")
                best_values = current_values[:]






    except KeyboardInterrupt:

        tuning.axis.requested_state = 1

        # tuning.axis.controller.config.vel_gain = 0
        # tuning.axis.controller.config.pos_gain = 0
        # tuning.axis.controller.config.vel_integrator_gain = 0

            
        print("calibraiton finished")
        #grapher.show_graph()

        print(f"Lowest cost: {absolute_min} \n At Values {best_values}")

        if input("Would you like to preview these values? y/N: ") == "y":
            tuning.axis.requested_state = AXIS_STATE_CLOSED_LOOP_CONTROL
            tuning.axis.controller.config.control_mode = CONTROL_MODE_POSITION_CONTROL
            tuning.axis.controller.config.input_mode = INPUT_MODE_PASSTHROUGH

            tuning.axis.controller.input_pos = 0

            time.sleep(1)

            print(f" Cost: {tuning.evaluate_values(best_values, mov_dist, mov_time, rmse_weight, variance_weight)}")

            tuning.axis.requested_state = 1

        if input("Would you like to keep these values? y/N: ") == "y":
            tuning.save_configuration(best_values)







if __name__ == "__main__":
    main(start_values)
