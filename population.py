import random
from industry import Industry
import debug

class Population:
    units = 0
    unemployed = 0

    demand_matrix = {}
    demand_stability = 0


    def get_unemp(self):
            return self.unemployed
    def get_emp(self):
        return self.units - self.unemployed
    def get_units(self):
        return self.units

    def employ(self, amount):
        self.unemployed = self.unemployed - amount
    def unemploy(self, amount):
        self.unemployed += amount

    def get_info(self):
        info = (
            f'Population Statistics\n' +
            f'  Total: {self.units}\n'+
            f'  Unemployed: {self.unemployed}\n'
        )
        return info

    def get_demand(self):
        # artifical demand stability
        if self.demand_stability == 0 and abs(random.gauss(mu = 0, sigma = 1)) > 4:
            self.demand_stability = 20
        
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
                
                
        if self.demand_stability > 0:
                self.demand_stability -= 1
        return self.demand_matrix

    def __init__(self, seed):
        self.units = int(seed * random.random() * 1000) + 1000
        self.unemployed = self.units
        self.demand_stability = 0       # artifical periods of stability
        self.demand_matrix = {
                0 : 0.5,
                1 : 0.2
            }
