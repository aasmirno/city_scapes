import random
import copy

from industry import Industry
import debug


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
            demand_walk = random.gauss(
                mu=self.demand_matrix[i_class],
                sigma=sigma,
            )
            if demand_walk < 0:
                demand_walk = 0
            if demand_walk > 1:
                demand_walk = 1

            self.demand_matrix[i_class] = demand_walk

    def __init__(self, id: int):
        self.demand_matrix = {
            0: 0.5,
            1: 0.2,
        }
        self.net_worth = 0
        self.initialised = True
        self.hired = False
        self.id = id


class Population:
    demand_stability = 0

    @property
    def unemployed(self):
        return len(self.unemployed_units)

    def get_emp(self):
        return [unit for unit in self.units if unit.getEmployment()]

    def get_units(self):
        return self.num_units

    def employ(self, amount):
        if type(amount) is not int or amount < 0:
            raise ValueError('employment amount must be a non-negative integer')
        if amount > self.unemployed:
            raise ValueError('employment amount exceeds available population')
        if amount == 0:
            return []

        employees = self.unemployed_units[-amount:]
        del self.unemployed_units[-amount:]
        for unit in employees:
            unit.setHired(True)
        return employees

    def unemploy(self, units):
        if any(not isinstance(unit, PopUnit) for unit in units):
            raise ValueError('only population units can be released')
        if len({unit.id for unit in units}) != len(units):
            raise ValueError('cannot release the same population unit more than once')
        for unit in units:
            if (
                unit.id < 0
                or unit.id >= self.num_units
                or self.units[unit.id] is not unit
                or not unit.getEmployment()
            ):
                raise ValueError('cannot release a population unit not employed here')

        for unit in units:
            unit.setHired(False)
        self.unemployed_units.extend(units)

    def hist_data(self):
        return [self.employ_hist, self.demand_hist]

    def get_info(self):
        info = (
            f'Population Statistics\n'
            f'  Total: {self.num_units}\n'
            f'  Unemployed: {self.unemployed}\n'
        )
        return info

    def get_demand(self):
        # Activate artificial demand stability after a large random fluctuation.
        if self.demand_stability == 0 and abs(random.gauss(mu=0, sigma=1)) > 3:
            self.demand_stability = 20

        avg = {
            0: 0,
            1: 0,
        }

        # Generate market variance.
        sigma = debug.DEMAND_STOCH
        if self.demand_stability > 0:
            sigma = 0.01

        # Sum demand across population units.
        for pop in self.units:
            pop.update_demand(sigma=sigma)
            for i_class in pop.demand_matrix:
                avg[i_class] += pop.demand_matrix[i_class]

        # Calculate average demand.
        for i_class in avg:
            avg[i_class] = avg[i_class] / len(self.units)

        # Store demand when data collection is enabled.
        if debug.DATA_MODE:
            self.demand_hist.append(copy.deepcopy(avg))
            self.employ_hist.append(self.unemployed)
        # Decrease the artificial stability timer.
        if self.demand_stability > 0:
            self.demand_stability -= 1

        return avg

    def __init__(self, seed):
        # Initialize the population.
        self.num_units = int(seed * random.random() * 1000) + 1000
        self.units = []
        for i in range(self.num_units):
            self.units.append(PopUnit(i))
        self.unemployed_units = self.units.copy()

        # Initialize demand metavariables.
        self.demand_stability = 0  # Stability timer.
        self.demand_matrix = {
            0: 0,
            1: 0,
        }
        
        # data mode variables
        self.demand_hist = []  # Historical demand tracking.
        self.employ_hist = []   # Historical employment
