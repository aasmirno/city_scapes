import random
import statistics

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

    cap_rate_base = 0
    cap_rate = 0
    employment = 0
    last_layoff_time = 0
    last_layoff_quant = 0
    risk_factor = 1

    wage = 0.2
    unit_price = 0.6

    tax_rate = 0
    budget = 0

    demand_exceed = 0
    demand_hist_length = 100

    pop_active = True
    desc = ''

    def get_active(self):
        return self.active
    def get_risk_factor(self):
        return self.risk_factor
    def get_dlength(self):
        return self.demand_hist_length
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
                   f'   L_Q: {self.last_layoff_quant}   L_T: {self.last_layoff_time}'
                   )
            return info
    
    def add_hist(self,demand):
        self.demand_hist.insert(0, demand)
        if len(self.demand_hist) > self.demand_hist_length:
            self.demand_hist.pop()

    # dynamic weighted average
    def d_wavg(self):
        s_norm = 0
        if len(self.demand_hist) > 9:
            last_10 = self.demand_hist[0:10]
            s_norm = abs(statistics.stdev(last_10))
            
        dynamic_length = self.demand_hist_length - int(10 * (s_norm / 100))
        if debug.DATA_MODE:
            self.data['dynamic_length'].append(s_norm / 100)
            
        demand_adj = []
        for i in range(0, min(dynamic_length, len(self.demand_hist))):
            demand_adj.append(self.demand_hist[i] * (1 / (i+1)**2))
        return sum(demand_adj) / max(len(demand_adj),1)

    def tune(self, population):
        self.adjust(population)
        if debug.DATA_MODE:
            self.data['wf'].append(self.employment)

    def layoff(self, amount, population):
        self.employment = self.employment - amount
        population.unemploy(amount)
        self.debug_log(f'fire {amount}')
        
        self.last_layoff_quant = amount / self.employment
        self.last_layoff_time = 0

    def hire(self, amount, population):
        self.employment += amount
        population.employ(amount)
        self.debug_log(f'hire {amount}')

    def fail(self,population):
        # set active false
        self.active = False
        # free workforce
        population.unemploy(self.employment)
        self.employment = 0
    
    # demand based expansion logic
    def demand_expand(self, population, expansion):
        self.debug_log(f'demand based expansion, d_max {expansion}')

        # check avaliable local population
        expansion = min(population.get_unemp(),expansion)
        if expansion == 0:
            self.debug_log('no workforce')
            return
        self.debug_log(f'd_pop {expansion}')
        
        # check recent volatility
        volatility = statistics.stdev(self.demand_hist[0:10])
        expansion = expansion / volatility
        
        # check industry budget
        industry_price = self.budget * self.risk_factor
        ideal_price = expansion * self.wage * 3
        price = min(ideal_price, industry_price)
        expansion = price / self.wage / 3
        
        if expansion == 0:
            self.debug_log(f'no budget')
            return
        
        self.hire(int(expansion), population)
    
    def demand_contract(self, population): 
        if self.employment == 0:
            return
        self.debug_log(f'demand based layoff')
        # set layoff amount based on risk factor
        unemp = self.risk_factor * self.employment
        
        # adjust based on recent volatility
        volatility = statistics.stdev(self.demand_hist[0:10]) / self.risk_factor
        
        # less aggresive industries should contract faster with higher volatility
        
        unemp = max(int(unemp / volatility), 1)
        
        self.layoff(unemp, population)

    def adjust(self, population):
        if self.budget < 1:
            self.fail(population)
            return
        
        # set cap rate
        quality = max(self.last_layoff_quant,0.01) / max(self.last_layoff_time,1)
        quality = max(quality, 0.1)
        quality = min(quality, 1)
        #self.cap_rate = self.cap_rate_base * quality
        self.debug_log(f'cap_rate: {self.cap_rate} l_time: {self.last_layoff_time} l_q: {self.last_layoff_quant}')
        
        # get perfect expansion
        expansion_requested = int(self.demand_exceed / self.cap_rate)
        # get weighted demand trend
        demand_trend = self.d_wavg()
        if debug.DATA_MODE:
            self.data['budget'].append(self.budget)
            self.data['weighted_trend'].append(demand_trend)
            
        # calculate current expenses against budget
        expense_eta = int(self.budget / max((self.wage * self.employment),1))

        # increase time from layoff
        self.last_layoff_time += 1
        self.debug_log(f'expansion_req: {expansion_requested}, demand_trend: {demand_trend}, expense_eta: {expense_eta}, budget: {self.budget}, wf: {self.employment}')
        
        if debug.GREMLINS and random.random() > debug.GREMLIN_RATE: # noise for unmodelled events
            if self.employment == 0:
                return
            gremlin_quota = int((self.employment * random.random() * 0.1))
            self.debug_log(f'GREMLIN {gremlin_quota}')
            self.layoff(gremlin_quota, population)
            return

        if demand_trend < -10:  # demand based layoff
            self.demand_contract(population)
            
        elif expense_eta < 2:   # expense based layoff
            self.debug_log(f'expense based layoff')
            unemp = int(0.9 * self.employment)
            self.layoff(unemp, population)
            
        elif demand_trend > 10 and expansion_requested > 0: # demand based hire
            self.demand_expand(population, expansion_requested)
        

    def sale(self, demand):
        self.demand_exceed = int(demand - (self.employment * self.cap_rate))
        self.debug_log(f'demand diff {self.demand_exceed}, raw demand {demand}')
        self.add_hist(self.demand_exceed)

        # sell goods
        tax = 0
        sale_raw = min(demand,(self.employment * self.cap_rate))    # raw sale number
        sale = sale_raw * self.unit_price                           # market adjusted sale
        tax = sale * self.tax_rate                                  # sale tax
        self.budget += sale - tax                                   # profit
        self.debug_log(f'sale {sale} tax {tax}')

        # subtract wage
        self.budget -= (self.wage * self.employment)
        self.debug_log(f'wages: {self.wage * self.employment}, final budget: {self.budget}')
        if debug.DATA_MODE:
            self.data['demand'].append(demand)
            self.data['demand_exceed'].append(self.demand_exceed)
            self.data['sales'].append(sale_raw)
        return demand - sale_raw

    def get_data(self):
        if not debug.DATA_MODE:
            return None
        return self.data

    def __init__(self, hdi, risk_factor, cap_rate, taxes, pop_active, demand_class, global_id, desc):
        self.hdi_effect = hdi
        self.cap_rate_base = cap_rate
        self.cap_rate = cap_rate
        self.risk_rate = 1
        self.last_layoff_time = 0
        self.last_layoff_quant = 0

        self.tax_rate = taxes
        self.budget = 10 + (5 * random.random())

        self.pop_active = pop_active
        self.demand_class = demand_class
        self.demand_hist = [0]

        self.desc = desc
        self.global_id = global_id
        self.risk_factor = risk_factor
        
        max_hist = 30
        self.demand_hist_length = max(max_hist - int(max_hist * self.risk_factor), 10)
        
        self.active = True
        
        if debug.DATA_MODE:
            self.data = {
                'demand' : [],
                'demand_exceed' : [],
                'wf': [],
                'budget' : [],
                'weighted_trend' : [],
                'dynamic_length' : [],
                'sales' : []
            }