#X axis: [.132, 26.6, .29]

import numpy as np
import tuning
import time
import random as rd
from config import *
from odrive.enums import *
from bayes_opt import BayesianOptimization

def max_function(vel_gain, pos_gain, vel_integrator_gain):
    cost = tuning.evaluate_values([vel_gain, pos_gain, vel_integrator_gain], mov_dist, mov_time, rmse_weight, variance_weight)
    return 1/cost


def main(start_values):

    tuning.startup(vel_limit, odrive_serial, axis_num)

    # tuning.start_liveplotter(lambda:[tuning.axis.controller.config.vel_gain])


    if start_values == []:
        start_values = [tuning.axis.controller.config.vel_gain, tuning.axis.controller.config.pos_gain, tuning.axis.controller.config.vel_integrator_gain]

    tuning.axis.controller.config.vel_gain = start_values[0]
    tuning.axis.controller.config.pos_gain = start_values[1]
    tuning.axis.controller.config.vel_integrator_gain = start_values[2]

    tuning.start_liveplotter(lambda: [tuning.axis.controller.input_pos, tuning.axis.encoder.pos_estimate])

    tuning.axis.controller.input_pos = 0
    time.sleep(3)

    optimizer = BayesianOptimization(
        f=max_function,
        pbounds=pbounds,
        random_state=1
    )

    optimizer.maximize(
        init_points=1,
        n_iter=6,
    )

    tuning.axis.requested_state = 1

    # tuning.axis.controller.config.vel_gain = 0
    # tuning.axis.controller.config.pos_gain = 0
    # tuning.axis.controller.config.vel_integrator_gain = 0


    print("calibraiton finished")


    print(optimizer.max)

    # if input("Would you like to preview these values? y/N: ") == "y":
    #     tuning.axis.requested_state = AXIS_STATE_CLOSED_LOOP_CONTROL
    #     tuning.axis.controller.config.control_mode = CONTROL_MODE_POSITION_CONTROL
    #     tuning.axis.controller.config.input_mode = INPUT_MODE_PASSTHROUGH
    #
    #     tuning.axis.controller.input_pos = 0
    #
    #     time.sleep(1)
    #
    #     print(f" Cost: {tuning.evaluate_values(best_values, mov_dist, mov_time, rmse_weight, variance_weight)}")
    #
    #     tuning.axis.requested_state = 1
    #
    # if input("Would you like to keep these values? y/N: ") == "y":
    #     tuning.save_configuration(best_values)







if __name__ == "__main__":
    main(start_values)
