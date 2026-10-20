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
        print(f'-------------------\nCity {self.id} - {self.seed}\npop {self.population.get_units()} - HDI {self.hdi}\nbudget {self.city_budget}\n{self.industries}\n{self.ext_connections}\n------------------')
        print(self.population.get_info())

    def info_industry(self):
        print(f'CITY {self.id} INDUSTRY DATA')
        for i_class in self.industries:
            for industry in self.industries[i_class]:
                if industry.get_active():
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
        #print('SALE CYCLE')
        tax_income = 0
        for i_class in civ_demand:
            civ_acc = []
            for industry in self.industries[i_class]:
                if industry.get_pop_active():
                    civ_acc.append(industry)
            unmet = 0
            for industry in civ_acc:
                if industry.get_active():
                    industry_income = industry.sale(civ_demand[i_class] * self.population.get_units() / len(civ_acc))
                    unmet += industry_income[0]
                    tax_income += industry_income[1]
        self.city_budget += tax_income
        self.city_data['tax_income'].append(tax_income)
                    
        #print('UPDATE CYCLE')
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
        
        warmup_ignore = debug.WARMUP_PERIOD
        fig, ax = plt.subplots(8)
        ax[0].set_title('demand')
        
        ax[1].set_title('hiring indicator')
        ax[1].axhline(0, color='black')
        
        ax[2].set_title('sale trend')
        ax[2].axhline(0, color='black')
        
        ax[3].set_title('demand trend')
        
        ax[4].set_title('demand volatility')
        
        ax[5].set_title('workforce')
        ax[5].axhline(0, color='black')
        
        ax[6].set_title('budget')
        ax[7].set_title('city tax income')
        
        # overall demand data
        demand_history = self.population.demand_history()
        classes = [c for c in demand_history[0]]
        for cat in classes:
            cat_data = [matrix[cat] for matrix in demand_history]
            ax[0].plot(cat_data, label=f'demand class {cat}')

        for i_class in self.industries:
            for industry in self.industries[i_class]:
                data = industry.get_data()
                
                ax[1].plot(data['hiring_indicator'][warmup_ignore:],label=f'{industry.get_risk_factor()},{industry.get_dlength()}')
                
                #ax[2].plot(data['weighted_trend'][warmup_ignore:], color='blue')
                ax[2].plot(data['sale_trend'][warmup_ignore:])
                
                ax[3].plot(data['weighted_trend'][warmup_ignore:])
                
                ax[4].plot(data['demand_volatility'][warmup_ignore:])
                
                ax[5].plot(data['wf'][warmup_ignore:])
                
                ax[6].plot(data['budget'][warmup_ignore:])
                ax[7].plot(self.city_data['tax_income'][warmup_ignore:])

        ax[1].legend()
        plt.show()

    def __init__(self, id):
        self.id = id
        self.seed = random.random()
        
        self.city_budget = int(self.seed * random.random() * 10000)
        self.population = Population(self.seed)

        self.city_data = {
            'tax_income' : [] 
        }
        self.industries = {0:[],1:[]}
        self.ex_conns = []

        self.hdi = max(self.seed * random.random() * (self.city_budget / self.population.get_units()),0.01)
        for i in range(0,len(debug.RISK_FACTORS)):
            self.add_industry(
                Industry(
                    hdi=0,
                    cap_rate=0.8,
                    risk_factor = debug.RISK_FACTORS[i],
                    taxes=0.01,
                    pop_active=True,
                    demand_class=0,
                    global_id=i,
                    desc=f'Grocer {i}'))
        self.info_industry()


def start_sim(num_cities):
    cities = []
    for i in range(0,num_cities):
        cities.append(City(i))

    industries = 2
    for i in range(0, debug.ITERATIONS):
        for city in cities:
            #print(i)
            city.update()
            
        if cities[0].num_industries() < 3:
            cities[0].add_industry(Industry(
                                hdi=0,
                                cap_rate=0.8,
                                risk_factor = 0.5,
                                taxes=0.1,
                                pop_active=True,
                                demand_class=0,
                                global_id=i,
                                desc=f'Grocer {industries}'))
            industries += 1

    for city in cities:
        city.info_industry()
        city.info()
        print()
    
    if debug.DATA_MODE:
        for city in cities:
            city.show_data()


start_sim(1)