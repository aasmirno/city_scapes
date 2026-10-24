
"""Debug and simulation configuration."""

import random


IND_DEBUG = False  # Control logging.
MARKET_COLLAPSE_RATE = 5  # Control the likelihood of market collapse.
RISK_FACTORS = [random.random() for _ in range(5)]  # Risk factors to test.
WARMUP_PERIOD = 0  # Simulation data start index.
ITERATIONS = 1000  # Simulation length.
DATA_MODE = True  # Control data storage.

# Defunct industry status.
DEFUNCT_PERIOD = 20

# Demand classes: 0 = food, 1 = items.
DEMAND_CLASSES = [0, 1]
DEMAND_CLASSES_N = len(DEMAND_CLASSES)
DEMAND_STOCH = 0.1  # Demand stochasticity.

GREMLINS = False
GREMLIN_RATE = 0.9

MAX_HIST = 15