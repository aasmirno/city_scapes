import random
from industry import Industry
import debug

class Population:
    units = 0
    unemployed = 0

    demand_matrix = {
        0 : 0.7,
        1 : 0.2
    }

    def get_unemp(self):
            return self.unemployed
    def get_emp(self):
        return amount - self.unemployed
    def get_units(self):
        return self.units

    def employ(self, amount):
        self.unemployed = self.unemployed - amount
    def unemploy(self, amount):
        self.unemployed += amount

    def get_info(self):
        info = (
            f'Populaton Statistics\n' +
            f'  Total: {self.units}\n'+
            f'  Unemployed: {self.unemployed}\n'
        )
        return info

    def get_demand(self):
        demand_adj = self.demand_matrix
        for i_class in demand_adj:
            demand_adj[i_class] = demand_adj[i_class] + (debug.DEMAND_STOCH * (random.random() - 0.5))
        return demand_adj

    def __init__(self, seed):
        self.units = int(seed * random.random() * 1000) + 1000
        self.unemployed = self.units
