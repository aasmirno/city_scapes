import random
from industry import Industry
import debug
import copy

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
    
    def update_demand(self, sigma=debug.DEMAND_STOCH):
        for i_class in self.demand_matrix:
            demand_walk = random.gauss(mu=self.demand_matrix[i_class],sigma=sigma)
            if demand_walk < 0: demand_walk = 0
            if demand_walk > 1: demand_walk = 1

            self.demand_matrix[i_class] = demand_walk
    
    
    def __init__(self, id: int):
        self.demand_matrix = {
            0 : 0.5,
            1 : 0.2
        }
        self.initialised = True
        self.hired = False
        self.id = id
    

class Population:
    unemployed = 0

    demand_matrix = {}
    demand_stability = 0

    def get_unemp(self):
        return self.unemployed
    def get_emp(self):
        return self.units - self.unemployed
    def get_units(self):
        return len(self.units)

    def employ(self, amount):
        self.unemployed = self.unemployed - amount
    def unemploy(self, amount):
        self.unemployed += amount

    def demand_history(self):
        return self.demand_hist

    def get_info(self):
        info = (
            f'Population Statistics\n' +
            f'  Total: {self.units}\n'+
            f'  Unemployed: {self.unemployed}\n'
        )
        return info

    def get_demand_pop(self):
        '''
            population model for demand
        '''
        avg = {     # demand matrix init
            0 : 0,
            1 : 0
        }

        for pop in self.units:
            pop.update_demand()
            for i_class in pop.demand_matrix:
                avg[i_class] += pop.demand_matrix[i_class]

        for i_class in avg:
            avg[i_class] = avg[i_class] / len(self.units)

        return avg

    def get_demand(self):
        # artifical demand stability
        if self.demand_stability == 0 and abs(random.gauss(mu = 0, sigma = 1)) > 3:
            self.demand_stability = 20
        
        # random market crash
        if self.demand_stability == 0 and abs(random.gauss(mu = 0, sigma = 1)) > debug.MARKET_COLLAPSE_RATE:
            self.demand_stability = 30
            for i_class in self.demand_matrix:
                self.demand_matrix[i_class] = 0.1
        
        # base market variance
        sigma = debug.DEMAND_STOCH
        # stable market variance
        if self.demand_stability > 0:
            sigma = 0.01
        demand_walk = random.gauss(mu=self.demand_matrix[0],sigma=sigma)
        
        # cap limits
        if demand_walk > 1.0: demand_walk = 1.0
        if demand_walk < 0.0: demand_walk = 0.0
        
        # apply walk
        for i_class in self.demand_matrix:
            self.demand_matrix[i_class] = abs(demand_walk)
                
        # artifical stability timer
        if self.demand_stability > 0:
            self.demand_stability -= 1

        
        demand = self.get_demand_pop()
        # store demand in data if required
        if debug.DATA_MODE:
            self.demand_hist.append(copy.deepcopy(demand))

        return demand

    def __init__(self, seed):
        # pop init
        self.num_units = int(seed * random.random() * 1000) + 1000
        self.unemployed = self.num_units
        self.units = []
        for i in range(0,self.num_units):
            self.units.append(PopUnit(i))
        
        # demand init
        self.demand_hist = []      # historical demand tracking
        self.demand_stability = 0  # stability timer
        self.demand_matrix = {     # demand matrix init
                    0 : 0,
                    1 : 0
                }
