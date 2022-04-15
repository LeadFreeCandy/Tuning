# Serial number of the odrive that you would like to tune.
# May be left blank if only one is connected.
odrive_serial = "20673593524B"
odrive_serial = "20793595524B"
# Which axis you would like to tune, must be 0 or 1.
axis_num = 0




#---The rest of these values are most likely fine, so only tinker with these if you need to do so---

# The distance in rotations to travel per move.
mov_dist = 1
# The time given for the motor to complete this move.
# Ensure that this value is large enough to allow the motor to complete the full distance, and
# that it has enough time to become stationary during the tuning cycle
mov_time = 1
# The max speed the motor can travel during this move
vel_limit = 20

# Iteration shift factor represents the factor in which values are mutated during the simulated evolution
iteration_shift_factor = 1.1
# RMSE weight is the weight given to the area under the curve optimization, or essentially the speed at which it
# arrives at the target value. 
rmse_weight = 1
# Variance weight is the weight given to the anti-vibration optimization, increases this value if it is optimizing 
# the tune with a vibration even after a full evolution time
# NOTE: The values themselves are only significant as a ratio to each other. Ex doubling both values does nothing
variance_weight = 2

# The initial values to seed the evolution process with in order of: vel_gain, pos_gain, vel_integrator_gain
# Set to empty array if you would like it to read existing values

# start_values = [.132, 26.6, .1]
# start_values = [.112, 29.3, .121]
# start_values = [.102, 26.6, 0.18]
# start_values = []
# The ranges for each of the values in the same order
ranges = [[0,.2], [0,250], [0,3]]

