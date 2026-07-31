import random

import debug

''' 
    demand classes:
    0: food
    1: items
'''
class Industry:
    global_id = 0

    hdi_effect = 0
    demand_class = 0

    cap_rate = 0
    employment = 0
    risk_factor = 1

    wage = 2
    unit_price = 0.1

    tax_rate = 0
    budget = 0

    demand_exceed = 0
    demand_hist_length = 5

    pop_active = True
    desc = ''

    def get_class(self):
        return self.demand_class
    def get_pop_active(self):
        return self.pop_active
    def get_hdi(self):
        return self.hdi_effect
    def get_tax(self):
        return self.tax_rate
    def get_desc(self):
        return self.desc
    def get_budget(self):
        return self.budget
    def debug_log(self, msg):
        if debug.IND_DEBUG:
            print(f'[industry {self.global_id}] {msg}')
    def get_info(self):
            info = (f'DE_TYPE: {self.demand_class}, {self.desc}\n'+
                   f'   BUDGET: {self.budget}\n'+
                   f'   R_factor: {self.risk_factor}, HIST_LEN: {self.demand_hist_length}\n'+
                   f'   EMPLOYED: {self.employment}'+
                   f'   CAP: {self.employment * self.cap_rate}\n'+
                   f'   {self.demand_hist}')
            return info
    
    def add_hist(self,demand):
        self.demand_hist.insert(0, demand)
        if len(self.demand_hist) > self.demand_hist_length:
            self.demand_hist.pop()

    def d_wavg(self):
        demand_adj = []
        for i in range(0,len(self.demand_hist)):
            demand_adj.append(self.demand_hist[i] * (1 / (i+1)**2))
        return sum(demand_adj) / len(demand_adj)

    def adjust(self, population):
        if self.budget < 0:
            return 0

        expansion_requested = int(self.demand_exceed / self.cap_rate)
        demand_trend = self.d_wavg()
        expense_eta = int(self.budget / max((self.wage * self.employment),1))

        self.debug_log(f'expansion_req: {expansion_requested}, demand_trend: {demand_trend}, expense_eta: {expense_eta}, budget: {self.budget}')
        if debug.GREMLINS and random.random() > debug.GREMLIN_RATE:
            gremlin_quota = int((self.employment * random.random() * 0.1))
            self.debug_log(f'GREMLIN {gremlin_quota}')
            self.employment -= gremlin_quota
            population.unemploy(gremlin_quota)
            return

        if demand_trend < -100:  # demand based layoff
            self.debug_log(f'demand based layoff')
            unemp = int(abs(expansion_requested) * self.risk_factor)

            self.employment = self.employment - unemp
            population.unemploy(unemp)
            self.debug_log(f'fire {unemp}')
        elif expense_eta < 2:   # expense based layoff
            self.debug_log(f'expense based layoff')
            unemp = int((1 - self.risk_factor) * self.employment)
            self.debug_log(f'fire {unemp}')
            self.employment = self.employment - unemp
            population.unemploy(unemp)
        elif demand_trend > 10 and expansion_requested > 0: # demand based hire
            expansion = expansion_requested
            self.debug_log(f'demand based expansion')

            # check avaliable local population
            expansion = min(population.get_unemp(),expansion)
            if expansion == 0:
                self.debug_log('no workforce')
                return

            # check industry budget
            price = min((expansion * self.wage * 3), int(self.budget))
            
            expansion = int(price / self.wage / 3)
            if expansion == 0:
                self.debug_log(f'no budget')
                return

            self.debug_log(f'hire {expansion}')
            # adjust industry stats
            self.employment += expansion

            # adjust population stats
            population.employ(expansion)

    def sale(self, demand):
        self.demand_exceed = int(demand - (self.employment * self.cap_rate))
        self.debug_log(f'demand exceed {self.demand_exceed}, raw demand {demand}')
        self.add_hist(self.demand_exceed)

        # sell goods
        tax = 0

        # raw sale number
        sale_raw = min(demand,(self.employment * self.cap_rate))
        # market adjusted sale
        sale = sale_raw * self.unit_price
        # sale tax
        tax = sale * self.tax_rate
        # profit
        self.budget += sale - tax
        self.debug_log(f'sale {sale} tax {tax}')

        # subtract wage
        self.budget -= (self.wage * self.employment)
        self.debug_log(f'wages: {self.wage * self.employment}, final budget: {self.budget}')

        return demand - sale_raw

    def __init__(self, hdi, cap_rate, taxes, pop_active, demand_class, global_id, desc):
        self.hdi_effect = hdi
        self.cap_rate = cap_rate
        self.risk_rate = 1

        self.tax_rate = taxes
        self.budget = 10 + (5 * random.random())

        self.pop_active = pop_active
        self.demand_class = demand_class
        self.demand_hist = [0]

        self.desc = desc
        self.global_id = global_id
        self.risk_factor = random.random()
        self.demand_hist_length = 5 + int(5 * random.random())