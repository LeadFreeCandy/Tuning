from bayes_opt import BayesianOptimization
import time
# Bounded region of parameter space
pbounds = {'x': (0, 10)}

def black_box_function(x):
    time.sleep(.25)
    return 1/x ** 2

optimizer = BayesianOptimization(
    f=black_box_function,
    pbounds=pbounds,
    random_state=1
)

optimizer.maximize(
    init_points=1,
    n_iter=6,
)

print(optimizer.max)