import random
import json
from pathlib import Path

import matplotlib.pyplot as plt

from population import Population
from industry import Industry
import debug

class City:
    id = None
    seed = 0
    population = None
    money = 0
    hdi = 0
    industries = {}
    infrastructure = []
    ext_connections = []

    def info(self):
        print(f'-------------------\nCity {self.id} - {self.seed}\npop {self.population.get_units()} - HDI {self.hdi}\nbudget {self.money}\n{self.industries}\n{self.ext_connections}\n------------------')
        print(self.population.get_info())

    def info_industry(self):
        print(f'CITY {self.id} INDUSTRY DATA')
        for i_class in self.industries:
            for industry in self.industries[i_class]:
                print(f'{industry.get_info()}')    

    def num_industries(self):
        count = 0
        for i_class in self.industries:
            for industry in self.industries[i_class]:
                if industry.get_active():
                    count += 1
        return count

    def update(self):
        civ_demand = self.population.get_demand()
        print('SALE CYCLE')
        for i_class in civ_demand:
            civ_acc = []
            for industry in self.industries[i_class]:
                if industry.get_pop_active():
                    civ_acc.append(industry)
            unmet = 0
            for industry in civ_acc:
                if industry.get_active():
                    unmet += industry.sale(civ_demand[i_class] * self.population.get_units() / len(civ_acc))
        print('UPDATE CYCLE')
        for i_class in self.industries:
            for ind in self.industries[i_class]:
                if ind.get_active():
                    ind.tune(population = self.population)
        
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
        fig, ax = plt.subplots(7)
        ax[0].set_title('demand')
        ax[1].set_title('demand_exceeded')
        ax[1].axhline(0, color='black')
        ax[2].set_title('weighted demand')
        ax[2].axhline(0, color='black')
        ax[3].set_title('s_norm')
        ax[4].set_title('workforce')
        ax[5].set_title('sales')
        ax[6].set_title('cap_rate')
        for i_class in self.industries:
            for industry in self.industries[i_class]:
                print(industry.get_risk_factor())
                
                data = industry.get_data()
                ax[0].plot(data['demand'])
                ax[1].plot(data['demand_exceed'],label=f'{industry.get_risk_factor()},{industry.get_dlength()}')
                ax[2].plot(data['weighted_trend'])
                ax[3].plot(data['dynamic_length'])
                ax[4].plot(data['wf'])
                ax[5].plot(data['sales'])
                ax[6].plot(data['budget'])

        ax[1].legend()
        plt.show()

    def __init__(self, id):
        self.id = id
        self.seed = random.random()
        
        self.money = int(self.seed * random.random() * 10000)
        self.population = Population(self.seed)

        self.industries = {0:[],1:[]}
        self.ex_conns = []

        self.hdi = max(self.seed * random.random() * (self.money / self.population.get_units()),0.01)
        risk_factors = [0.1,0.5,0.9]
        for i in range(0,3):
            self.add_industry(
                Industry(
                    hdi=0,
                    cap_rate=0.8,
                    risk_factor = risk_factors[i],
                    taxes=0.01,
                    pop_active=True,
                    demand_class=0,
                    global_id=i,
                    desc=f'Grocer {i}'))
        #self.info()
        self.info_industry()


def start_sim(num_cities):
    cities = []
    for i in range(0,num_cities):
        cities.append(City(i))

    for i in range(0,500):
        for city in cities:
            print(i)
            city.update()
            
        if cities[0].num_industries() == 0:
            break

    for city in cities:
        city.info()
        city.info_industry()
        print()
    
    if debug.DATA_MODE:
        for city in cities:
            city.show_data()


start_sim(1)