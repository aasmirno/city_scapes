
import random 
'''
    DEBUG / TESTING flags
'''
IND_DEBUG = False            # control logging
MARKET_COLLAPSE_RATE = 5    # control likelihood of market collapse
RISK_FACTORS = [random.random() for i in range(0,50)]   # risk factors to test
WARMUP_PERIOD = 10           # simulation data begin index
ITERATIONS = 10000             # simulation length
DATA_MODE = True            # control data storage

'''
    parameters
'''
# defunct status
DEFUNCT_PERIOD = 20

HDI_MIN = 0.1

''' 
    demand classes:
    0: food
    1: items
'''
DEMAND_CLASSES = [0,1]
DEMAND_STOCH = 0.1      # demand stochasticity

GREMLINS = False
GREMLIN_RATE = 0.9

MAX_HIST = 15