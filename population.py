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
        order = [(demand, self.net_worth / 10, self.id) for demand in self.demand_matrix]
        self.order = order
        return order


    def order_return(self, order_filled: list):
        fullfilment = [np.divide(filled,order) for order,filled in zip(self.order, order_filled)]
        for i in range(debug.DEMAND_CLASSES_N):
            fill_ratio = fullfilment[i][0]
            
            # filled orders decrease demand
            if fill_ratio > 0.5:
                self.demand_matrix[i] = max(1e-6, self.demand_matrix[i] - fill_ratio * 0.01)
             
            # subtract price
            self.net_worth = max(0, self.net_worth - order_filled[i][1])   
        
        #print(fullfilment)

    def __init__(self, id: int):
        self.demand = DemandGenerator(types=debug.DEMAND_CLASSES_N,
                      starting_means=[0.5 for i in range(0,debug.DEMAND_CLASSES_N)],
                      starting_variances=[0.05 for i in range(0,debug.DEMAND_CLASSES_N)],
                      distrib='gauss')
        self.demand_matrix = [0.5 for i in range(debug.DEMAND_CLASSES_N)]
        
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
        
        order_sum = np.sum(orders,axis=0)
        if debug.DATA_MODE:
            self.data.setdefault('avg_order',[]).append([order[0] / self.total_pop for order in order_sum])
            self.data.setdefault('avg_price',[]).append([order[1] / self.total_pop for order in order_sum])
            self.data.setdefault('income',[]).append(self.income)
        
        return orders

    def fill(self, orders_filled: list):
        for order in orders_filled:
            id = order[0][2]
            
            if id < 0 or id >= self.total_pop:
                raise ValueError(f"Invalid id {id}")
            
            self.units[id].order_return(order)

    def pay(self, amount: list):
        '''
            Pay pop units using list (id, payment)
        '''
        
        for value in amount:
            self.units[value[0]].net_worth += value[1]


    def __init__(self):
        # Initialize the population.
        self.num_units = int(random.random() * 1000)
        self.units = []
        for i in range(self.num_units):
            self.units.append(PopUnit(i))
        
        self.data = {}
