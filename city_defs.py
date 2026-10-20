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
        # get total civilian demand
        civ_demand = self.population.get_demand()
        tax_income = 0
        total_income = 0

        # apply demand to existing industries
        for i_class in civ_demand:
            # gather all civilian accesible industries
            civil_facing_ind = []
            for industry in self.industries[i_class]:
                if industry.get_pop_active():
                    civil_facing_ind.append(industry)

            # apply avaliable demand to all industries equally
            unmet = 0
            for industry in civil_facing_ind:
                if industry.get_active():
                    industry_income = industry.sale(
                        civ_demand[i_class]
                        * self.population.get_units()
                        / len(civil_facing_ind)
                    )

                    unmet += industry_income[0]
                    tax_income += industry_income[1]
                    total_income += industry_income[2]

        self.city_budget += tax_income
        self.city_data['tax_income'].append(tax_income)
        self.city_data['gdp'].append(total_income)

        for i_class in self.industries:
            for ind in self.industries[i_class]:
                if ind.get_active():
                    ind.tune(population=self.population)

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
        fig, ax = plt.subplots(3)

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
        
        ax[2].set_title('industry income')
        ax[2].plot(self.city_data['gdp'])

        plt.show()

    def __init__(self, id):
        # meta
        self.id = id
        self.seed = random.random()

        # budget and pop
        self.city_budget = int(self.seed * random.random() * 10000)
        self.population = Population(self.seed)

        # city industries
        self.industries = {0: [], 1: []}
        self.city_data = {'tax_income': [], 'gdp': []}

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
            city.update()

        if cities[0].num_industries() < 3:
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
            industries += 1

    for city in cities:
        city.info_industry()
        city.info()
        print()

    if debug.DATA_MODE:
        for city in cities:
            city.show_data()


start_sim(1)