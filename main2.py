import tuning
from config import *
import time
import odrive

def main():
    # input("Ensure that motor can freely rotate in either direction for calibration and tuning")
    
    tuning.startup(odrive_serial, axis_num)
    
    tuning.start_liveplotter(lambda: [tuning.axis.controller.pos_setpoint, tuning.axis.controller.vel_setpoint, tuning.axis.controller.torque_setpoint, tuning.axis.encoder.pos_estimate])

    
    tuning.set_freq(.5)
    
    time.sleep(10)
    
    
    
if __name__ == "__main__":
    try:
        main()
    finally:
        tuning.idle()
        # pass
