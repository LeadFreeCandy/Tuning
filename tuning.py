import odrive
from odrive.enums import *
from odrive.utils import *
import time
import numpy as np
import math
import fibre.libfibre
from functools import lru_cache

axis = None
axis_slave = None
odrv = None

def move(dist = 5):
    axis.controller.input_pos = 0
    time.sleep(2)

    axis.controller.input_pos = dist



def rmse_calc(values: np.array, start_pos, target_pos):

    sum = 0
    for val in values:
        if (start_pos < val < target_pos) or (target_pos < val < start_pos):
            sum += abs(val - target_pos)
        else:
            sum += abs(val - target_pos) * 2

    return sum/values.size



       # return np.sqrt(((values - input_pos) ** 2).mean())

def smre_calc(values: np.array):
    return ((np.sqrt(np.absolute(values))).mean()) ** 2


def vibration_calc(values: np.array):
    variances = np.array([])
    for i in range(len(values) - 2):
        variance = (values[i] + values[i + 2]) / 2 - values[i + 1]
        variances = np.append(variances, variance)

    return smre_calc(variances)

def analyze_move(t = 1):
    t0 = time.time()

    values = np.array([])
    values2 = np.array([])
    input_pos = axis.controller.input_pos
    start_pos = axis.encoder.pos_estimate

    while(time.time()-t0 < t):
        values = np.append(values, axis.encoder.pos_estimate)
        values2 = np.append(values2, axis_slave.encoder.pos_estimate)

    rmse = rmse_calc(values, start_pos, input_pos) + \
    rmse_calc(values2, start_pos, input_pos)
    var = vibration_calc(values) + vibration_calc(values2)

    # print(f"Computed with {values.size} values")
    return rmse, var

@lru_cache
def evaluate_values(values, mov_dist = 1, mov_time = 1, rmse_weight = 1, variance_weight = 3, print_vals = False):
    

    try:
        assert -0.25 < axis.encoder.pos_estimate < .25
        assert -0.25 < axis_slave.encoder.pos_estimate < .25
    except AssertionError:
        print("this is bad!!!!")
        return 1

    axis.controller.config.vel_gain = values[0]
    axis.controller.config.pos_gain = values[1]
    axis.controller.config.vel_integrator_gain = values[2]
    
    axis_slave.controller.config.vel_gain = values[0]
    axis_slave.controller.config.pos_gain = values[1]
    axis_slave.controller.config.vel_integrator_gain = values[2]
    
    

    axis.controller.input_pos = mov_dist
    base_rmse, base_variance = analyze_move(mov_time)
    axis.controller.input_pos = 0
    move = analyze_move(mov_time)
    
    
    base_rmse += move[0]
    base_variance += move[1]
    base_rmse /= 2
    base_variance /= 2
    
    # base_variance = 0 if base_variance < .003 else 1

    cost = base_rmse if base_variance < .003 else base_variance + 100
    # cost = base_rmse + base_variance

    if print_vals:
        print(f"rmse = {base_rmse}, variance = {base_variance}")
        print(f"cost = {cost}")
        
    return cost


def start_plotter(data_list):
    start_liveplotter(lambda:data_list)
    


def idle():

    axis_slave.requested_state = AXIS_STATE_IDLE
    axis.requested_state = AXIS_STATE_IDLE

def startup(odrive_serial, axis_num):
    global axis
    global axis_slave
    global odrv


    assert axis_num == 1 or axis_num == 0


    if odrive_serial != "":
        odrv = odrive.find_any(serial_number=odrive_serial)
    else:
        odrv = odrive.find_any()


    if axis_num:
        axis = odrv.axis1
        axis_slave = odrv.axis0
    else:
        axis = odrv.axis0
        axis_slave = odrv.axis1
        
    odrv.clear_errors()

    axis_slave.requested_state = AXIS_STATE_IDLE

    axis.requested_state =  AXIS_STATE_FULL_CALIBRATION_SEQUENCE
    while axis.current_state != AXIS_STATE_IDLE:
        pass
    time.sleep(1)
    
    axis_slave.requested_state =  AXIS_STATE_FULL_CALIBRATION_SEQUENCE
    
    while axis_slave.current_state != AXIS_STATE_IDLE:
        pass
    time.sleep(1)

    axis.controller.config.vel_limit = 40
    axis.controller.config.enable_overspeed_error = False

    axis.requested_state = AXIS_STATE_CLOSED_LOOP_CONTROL
    axis.controller.config.control_mode = CONTROL_MODE_POSITION_CONTROL
    axis.controller.config.input_mode = INPUT_MODE_PASSTHROUGH
    
    axis_slave.controller.config.vel_limit = 40
    axis_slave.controller.config.enable_overspeed_error = False

    axis_slave.requested_state = AXIS_STATE_CLOSED_LOOP_CONTROL
    axis_slave.controller.config.control_mode = CONTROL_MODE_POSITION_CONTROL
    axis_slave.controller.config.input_mode = INPUT_MODE_MIRROR
    axis_slave.controller.config.axis_to_mirror = 0
    axis_slave.controller.config.mirror_ratio = 1
    

    
    
    time.sleep(1)


def main():


    start_plotter()
    startup()
    

    print("Type the key letter, a space, and then a number to set gain value. EX: \"P 50\"")
    print("Type \"d\" to reset all values to their default")
    print("Type \"m\" to move by position, type \"m2\" to move by velocity, can be followed by a space and distance")

    while True:
        print(f"""
        vel_gain (v) = {axis.controller.config.vel_gain}
        pos_gain (p) = {axis.controller.config.pos_gain}
        vel_integrator_gain (i) = {axis.controller.config.vel_integrator_gain}""")
        

        text = input()

        try:

            if text == "d":
                axis.controller.config.vel_gain = .16
                axis.controller.config.pos_gain = 20
                axis.controller.config.vel_integrator_gain = .32


            elif text[0:2] == 'm2':

                val = float(text.split(" ")[1])
                print(f"moving vel {val}")
                move2(float(val))

            elif text[0] == 'm':

                val = float(text.split(" ")[1])
                print(f"moving {val}")
                move(float(val))


                
            else:
                target, val = text.split(" ")
                val = float(val)

                if target == "v":
                    axis.controller.config.vel_gain = val
                elif target == "p":
                    axis.controller.config.pos_gain = val
                elif target == "i":
                    axis.controller.config.vel_integrator_gain = val
                

            
        except Exception as e:
            print(f"ERROR: {e}")

def save_configuration(values):


    axis.controller.config.vel_gain = values[0]
    axis.controller.config.pos_gain = values[1]
    axis.controller.config.vel_integrator_gain = values[2]
    
    axis_slave.controller.config.vel_gain = values[0]
    axis_slave.controller.config.pos_gain = values[1]
    axis_slave.controller.config.vel_integrator_gain = values[2]

    print("saving configuration!!")

    try:
        odrv.save_configuration()
    except fibre.libfibre.ObjectLostError:
        pass  # Saving configuration makes the device reboot

    print("saved!")

# odrv0.axis0.requested_state = AXIS_STATE_FULL_CALIBRATION_SEQUENCE
# odrv0.axis0.motor.config.pre_calibrated = True
# odrv0.axis0.config.startup_encoder_offset_calibration = True
# odrv0.axis0.config.startup_closed_loop_control = True
# odrv0.save_configuration()
# odrv0.reboot()

# print("done!")

if __name__ == "main":
    main()

