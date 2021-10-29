import numpy as np
import tuning
import time
import random as rd
from config import *


def in_range(val, range):
    return range[0] <= val <= range[1]





def main(start_values, vel_range, pos_range, int_range):

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
            test_values = current_values[:]
            test_values[index] *= shift

            if test_values[index] < ranges[index][0]:
                test_values[index] = ranges[index][0]
            elif test_values[index] > ranges[index][1]:
                test_values[index] = ranges[index][1]

            print(f"current_values = {current_values}")
            baseline = tuning.evaluate_values(current_values, mov_dist, mov_time, rmse_weight, variance_weight)
            cost = tuning.evaluate_values(test_values, mov_dist, mov_time, rmse_weight, variance_weight)

            # cost = tuning.evaluate_values(values, mov_dist, mov_time, rmse, variance, print)


            cost_delta = cost - baseline

            print(baseline)
            print(cost)

            print(f"--shifting with cost delta: {cost_delta}")
            print(f"--previous values: {current_values}")
            print(f"--new values: {test_values}")

            # current_values[index] *= shift  # TODO: multipy shift by the magnitude of delta

            if cost_delta < 0:
                current_values[index] *= shift

            else:
                current_values[index] /= shift / 2

            if cost < absolute_min:  # TODO: retry to unsure it truly is abs minimum
                print(f"old absolute_min: {absolute_min}")
                absolute_min = cost
                print(f"new absolute_min: {absolute_min}")
                best_values = current_values






    except KeyboardInterrupt:


        tuning.axis.requested_state = 1
        # tuning.axis.controller.config.vel_gain = 0
        # tuning.axis.controller.config.pos_gain = 0
        # tuning.axis.controller.config.vel_integrator_gain = 0

            
        print("calibraiton finished")
        #grapher.show_graph()

        print(f"Lowest cost: {absolute_min} \n At Values {best_values}")
        if input("Would you like to keep these values? y/N: ") == "y":
            tuning.save_configuration(best_values)







if __name__ == "__main__":
    main(start_values, vel_range, pos_range, int_range)