import json
import random
from pathlib import Path

import matplotlib.pyplot as plt

from industry import Industry
import debug
from population import Population


class City:
    id = None
    seed = 0
    population = None
    money = 0
    industries = {}
    infrastructure = []
    ext_connections = []

    def info(self):
        print(
            f'-------------------\nCity {self.id} - {self.seed}\n'
            f'pop {self.population.get_units()}\n'
            f'budget {self.city_budget}\n{self.industries}\n'
            f'{self.ext_connections}\n------------------'
        )
        print(self.population.get_info())

    def info_industry(self):
        print(f'CITY {self.id} INDUSTRY DATA')
        for i_class in self.industries:
            for industry in self.industries[i_class]:
                if industry.get_active():
                    print(industry.get_info())

    def num_industries(self):
        count = 0
        for i_class in self.industries:
            for industry in self.industries[i_class]:
                if industry.get_active():
                    count += 1
        return count

    def update(self):
        if self.terminated:
            return

        # get total civilian demand
        civ_demand = self.population.get_demand()
        tax_income = 0

        # apply demand to existing industries
        for i_class in civ_demand:
            # Gather active industries that serve the population.
            active_industries = [
                industry
                for industry in self.industries[i_class]
                if industry.get_pop_active() and industry.get_active()
            ]

            # Divide demand only among active population-facing industries.
            for industry in active_industries:
                demand_per_unit = 1 / len(active_industries)
                purchases = [
                    (unit, unit.demand_matrix[i_class] * demand_per_unit)
                    for unit in self.population.units
                ]
                industry_income = industry.sale(
                    civ_demand[i_class]
                    * self.population.get_units()
                    * demand_per_unit,
                    consumers=purchases,
                )

                tax_income += industry_income[1]

        self.city_budget += tax_income
        self.city_data['tax_income'].append(tax_income)

        for i_class in self.industries:
            for ind in self.industries[i_class]:
                if ind.get_active():
                    ind.tune(population=self.population)

        industry_wealth = sum(
            industry.budget
            for industries in self.industries.values()
            for industry in industries
        )
        self.city_data['industry_wealth'].append(industry_wealth)

        active_industries = self.num_industries()
        if debug.DATA_MODE:
            self.population.wealth_hist.append(self.population.get_total_wealth())
            self.city_data['active_industries'].append(active_industries)

        if active_industries == 0:
            self.empty_industry_cycles += 1
            if self.empty_industry_cycles >= 10:
                self.terminated = True
        else:
            self.empty_industry_cycles = 0

    def add_industry(self, industry: Industry):
        i_class = industry.get_class()
        if i_class not in self.industries:
            self.industries[i_class] = [industry]
        else:
            self.industries[i_class].append(industry)

    def show_data(self):
        if not debug.DATA_MODE:
            print('ERROR data mode disabled')
            return

        warmup_ignore = debug.WARMUP_PERIOD
        fig, ax = plt.subplots(10)

        # Plot the overall demand data.
        ax[0].set_title('population demand')
        demand_history = self.population.hist_data()[1]
        ax[0].plot(
            [matrix[0] for matrix in demand_history],
            label=f'demand class {0}',
        )
        ax[0].legend()

        # population employment
        ax[1].set_title('employed')
        ax[1].plot(self.population.hist_data()[0])
        
        ax[2].set_title('active industries')
        ax[2].plot(self.city_data['active_industries'])

        ax[3].set_title('city tax revenue')
        ax[3].plot(self.city_data['tax_income'])

        ax[4].set_title('industry budgets')
        for industries in self.industries.values():
            for industry in industries:
                data = industry.get_data()
                ax[4].plot(
                    data['budget'],
                    label=f'{industry.get_desc()} ({industry.global_id})',
                )
        ax[4].legend()

        ax[5].set_title('industry sales trend')
        ax[6].set_title('industry hiring indicator')
        ax[7].set_title('industry demand')
        for industries in self.industries.values():
            for industry in industries:
                data = industry.get_data()
                label = f'{industry.get_desc()} ({industry.global_id})'
                ax[5].plot(data['sale_trend'], label=label)
                ax[6].plot(data['hiring_indicator'], label=label)
                ax[7].plot(data['demand'], label=label)
        ax[5].legend()
        ax[6].legend()
        ax[7].legend()

        first_industry = next(
            (industry for industries in self.industries.values() for industry in industries),
            None,
        )
        ax[8].set_title('expenses per cycle: first industry')
        ax[9].set_title('profit per cycle: first industry')
        if first_industry is not None:
            data = first_industry.get_data()
            label = f'{first_industry.get_desc()} ({first_industry.global_id})'
            ax[8].plot(data['expenses'], label=label)
            ax[9].plot(data['profit'], label=label)
            ax[8].legend()
            ax[9].legend()

        plt.show()

    def __init__(self, id):
        # meta
        self.id = id
        self.seed = random.random()

        # budget and pop
        self.city_budget = int(self.seed * random.random() * 10000)
        self.population = Population(self.seed)
        self.empty_industry_cycles = 0
        self.terminated = False

        # city industries
        self.industries = {0: [], 1: []}
        self.city_data = {
            'tax_income': [],
            'industry_wealth': [],
            'active_industries': [],
        }

        for i in range(len(debug.RISK_FACTORS)):
            self.add_industry(
                Industry(
                    cap_rate=0.8,
                    risk_factor=debug.RISK_FACTORS[i],
                    taxes=0.01,
                    pop_active=True,
                    demand_class=0,
                    global_id=i,
                    desc=f'Grocer {i}',
                )
            )
        self.info_industry()


def start_sim(num_cities):
    cities = []
    for i in range(num_cities):
        cities.append(City(i))

    industries = 2
    for i in range(debug.ITERATIONS):
        for city in cities:
            if not city.terminated:
                city.update()

        if all(city.terminated for city in cities):
            break

        '''if cities[0].num_industries() < 3:
            cities[0].add_industry(
                Industry(
                    cap_rate=0.8,
                    risk_factor=0.5,
                    taxes=0.1,
                    pop_active=True,
                    demand_class=0,
                    global_id=i,
                    desc=f'Grocer {industries}',
                )
            )
            industries += 1'''

    for city in cities:
        city.info_industry()
        city.info()
        print()

    if debug.DATA_MODE:
        for city in cities:
            city.show_data()


start_sim(1)