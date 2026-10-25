import random
import copy

from math_extras import DemandGenerator
from industry import Industry
import debug
import numpy as np


class PopUnit:      
    def getID(self):
        if self.initialised:
            return self.id

    def getEmployment(self):
        if self.initialised:
            return self.hired

    def setHired(self, status: bool):
        if self.initialised:
            self.hired = status

    def get_order(self) -> list:
        '''
            Generate order to purchase supply
        '''
        demand_matrix = self.demand.get_next()
        
        order = []
        return demand_matrix


    def __init__(self, id: int):
        self.demand = DemandGenerator(types=debug.DEMAND_CLASSES_N,
                      starting_means=[0.5 for i in range(0,debug.DEMAND_CLASSES_N)],
                      starting_variances=[0.05 for i in range(0,debug.DEMAND_CLASSES_N)],
                      distrib='gauss')
        
        self.net_worth = random.random() * 100
        self.initialised = True
        self.hired = False
        self.id = id


class Population:
    @property
    def income(self):
        return sum(unit.net_worth for unit in self.units)

    @property
    def total_pop(self):
        return len(self.units)

    def get_test_data(self):
        if debug.DATA_MODE:
            return self.data
        return None

    def get_info(self):
        info = (
            f'Population Statistics\n'
            f'  Total: {self.num_units}\n'
            f'  Unemployed: {self.unemployed}\n'
        )
        return info

    def get_orders(self) -> list:
        orders = [unit.get_order() for unit in self.units]
        
        if debug.DATA_MODE:
            self.data.setdefault('avg_order',[]).append(np.sum(orders,axis=0) / self.total_pop)
            self.data.setdefault('income',[]).append(self.income)
        
        return orders

    def __init__(self):
        # Initialize the population.
        self.num_units = int(random.random() * 1000)
        self.units = []
        for i in range(self.num_units):
            self.units.append(PopUnit(i))
        
        self.data = {}
