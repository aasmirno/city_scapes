import random
import statistics
import math
import math_extras

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

    max_sale_hist = 50

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
    
    def add_sales(self, sale):
        self.sales_hist.insert(0, sale)
        if len(self.sales_hist) > self.max_sale_hist:
            self.sales_hist.pop()
            
    def add_hist(self,demand):
        self.demand_hist.insert(0, demand)
        if len(self.demand_hist) > self.demand_hist_length:
            self.demand_hist.pop()

    # basic moving average indicator
    def macd(self, data):
        period_short = int(10 * self.risk_factor)
        period_long = int(20 * self.risk_factor)
        
        m_short = sum(data[0:period_short]) / len(data[0:period_short])
        m_long = sum(data[0:period_long]) / len(data[0:period_long])
        
        self.data['macd_short'].append(m_short)
        self.data['macd_long'].append(m_long)
        
        return m_short - m_long

    # demand weighted average
    def d_wavg(self):
        # calculate recent volatility
        last_n = self.demand_hist[0:10]
        if len(last_n) >= 3:
            std = statistics.stdev(last_n)
            mean_recent = abs(statistics.mean(last_n))
        else:
            std = 0.0
            mean_recent = abs(last_n[0]) if last_n else 0.0
        
        # normalise volatility
        if std > 2.0:
            norm_scale = std / (mean_recent + 1e-6)
            reduction = int(5 * min(norm_scale, 1.0))
        else:
            reduction = 0
            
        # change weighted average length based on recent volatility
        dynamic_length = max(1, min(self.demand_hist_length - reduction, self.demand_hist_length))
        if debug.DATA_MODE:
            self.data['dynamic_length'].append(dynamic_length)
        
        if dynamic_length == 0:
            return 0
        
        # create weighted average list
        demand_adj = []
        weights = [((i + 1)) for i in range(0, min(dynamic_length, len(self.demand_hist)))]
        for i in range(0, min(dynamic_length, len(self.demand_hist))):
            weighted_demand = self.demand_hist[i] / weights[i]
            demand_adj.append(weighted_demand)
        return sum(demand_adj) / sum(weights)

    def sales_trend(self):
        #recent_sales = [self.macd(self.sales_hist[i:i+10]) for i in range(0,10)]
        #print(recent_sales)
        return self.macd(self.sales_hist)
        

    def tune(self, population):
        self.adjust(population)
        if debug.DATA_MODE:
            self.data['wf'].append(self.employment)

    def layoff(self, amount, population):
        # calculate percentage laid off
        self.last_layoff_quant = amount / self.employment
        
        # remove from industry and return to workpool
        self.employment = self.employment - amount
        population.unemploy(amount)
        self.debug_log(f'fire {amount}')
        
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
    #   population: stores city population metadata
    #   expansion: demand units not captured (pop * demand matrix)
    def demand_expand(self, population, expansion):
        '''
            possible sale stores the theoretical perfect profit if production matched demand
            (demand exceeded * price per demand unit) - (theoretical wages)
        '''
        # error check
        if expansion <= 0:
            self.debug_log('no expansion demand')
            return

        possible_sale = (expansion * self.unit_price)
        # avoid division by zero for cap_rate
        cap = max(self.cap_rate, 1e-6)
        possible_cost = (int(expansion / cap) * self.wage)
        if debug.DATA_MODE:
            self.data['p_sale'].append(possible_sale - possible_cost)

        # theoretical maximum to fulfill demand
        max_workers = int(math.ceil(expansion / cap))

        # available resources
        budgeted_workers = int((self.budget * self.risk_factor) / max(self.wage, 1e-6))

        # avaliable workforce
        aval_workers = population.get_unemp()

        # decide hires
        hires = min(max_workers, aval_workers, budgeted_workers)

        # apply risk_factor as a multiplier to hiring appetite
        hires = int(max(0, hires))

        self.debug_log(f'd_pop {hires} theoretical max {max_workers}, workforce avaliable {aval_workers}, afford {budgeted_workers}')
        if hires <= 0:
            if aval_workers == 0:
                self.debug_log('no workforce')
            else:
                self.debug_log('cannot afford to hire')
            return

        # perform hires
        self.hire(hires, population)
    
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
        if self.budget < 1 or (len(self.sales_hist) > debug.DEFUNCT_PERIOD and sum(self.sales_hist[0:debug.DEFUNCT_PERIOD]) == 0):
            self.fail(population)
            return
         
        # set cap rate
        quality = 1
        if self.last_layoff_time != None:
            quality = 1 / (max(self.last_layoff_quant, 1) * max(self.last_layoff_time, 1))
            quality = max(quality, 0.1)
        self.cap_rate = max(self.cap_rate_base * quality, 0.1)
        self.debug_log(f'cap_rate: {self.cap_rate} l_time: {self.last_layoff_time} l_q: {self.last_layoff_quant}')
        
        
        # get demand and sales trends
        demand_trend = self.d_wavg()
        sale_trend = self.sales_trend()
        if debug.DATA_MODE:
            self.data['budget'].append(self.budget)
            self.data['weighted_trend'].append(demand_trend)
            
        # calculate current expenses against budget
        expense_eta = int(self.budget / max((self.wage * self.employment),1))

        # increase time from layoff
        if self.last_layoff_time != None:
            self.last_layoff_time += 1
        self.debug_log(f'expansion_req: {self.demand_hist[0]}, demand_trend: {demand_trend}, expense_eta: {expense_eta}, sale_trend: {sale_trend} budget: {self.budget}, wf: {self.employment}')
        
        if debug.GREMLINS and random.random() > debug.GREMLIN_RATE: # noise for unmodelled events
            if self.employment == 0:
                return
            gremlin_quota = int((self.employment * random.random() * 0.1))
            self.debug_log(f'GREMLIN {gremlin_quota}')
            self.layoff(gremlin_quota, population)
            return
        
        if sale_trend < 0:  # sales based layoff
            self.demand_contract(population)
            
        elif expense_eta < 2:   # expense based layoff
            self.debug_log(f'expense based layoff')
            unemp = int(0.9 * self.employment)
            self.layoff(unemp, population)
            
        elif demand_trend > 4 and self.demand_hist[0] > 0: # demand based hire
            self.demand_expand(population, self.demand_hist[0])
        

    def sale(self, demand):
        self.demand_exceed = int(demand - (self.employment * self.cap_rate))
        self.debug_log(f'demand diff {self.demand_exceed}, raw demand {demand}')

        # sell goods
        tax = 0
        sale_raw = min(demand,(self.employment * self.cap_rate))    # raw sale number
        sale = sale_raw * self.unit_price                           # market adjusted sale
        tax = sale * self.tax_rate                                  # sale tax
        self.budget += sale - tax                                   # profit
        self.debug_log(f'   sale {sale} tax {tax}')

        # subtract wage
        self.budget -= (self.wage * self.employment)
        self.debug_log(f'   wages: {self.wage * self.employment}')
        self.debug_log(f'final budget: {self.budget}')
        
        # store profit figures
        self.add_hist(self.demand_exceed)
        self.add_sales(sale - tax - (self.wage * self.employment))
        if debug.DATA_MODE:
            self.data['demand'].append(demand)
            self.data['demand_exceed'].append(self.demand_exceed)
            self.data['sales'].append(sale - tax - (self.wage * self.employment))
            self.data['p_sale'].append((self.demand_exceed * self.unit_price) - (int(self.demand_exceed / self.cap_rate) * self.wage))
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
        self.last_layoff_time = None
        self.last_layoff_quant = 0

        self.tax_rate = taxes
        self.budget = 10 + (5 * random.random())

        # population parameters
        self.pop_active = pop_active
        self.demand_class = demand_class

        # meta parameters
        self.desc = desc
        self.global_id = global_id
        self.risk_factor = risk_factor
        
        # data history parameters
        self.demand_hist_length = max(debug.MAX_HIST - int(debug.MAX_HIST * self.risk_factor), 10)
        self.demand_hist = [0]
        self.sales_hist = [0]
        
        self.active = True
        
        if debug.DATA_MODE:
            self.data = {
                'demand' : [],
                'demand_exceed' : [],
                'wf': [],
                'budget' : [],
                'weighted_trend' : [],
                'dynamic_length' : [],
                'sales' : [],
                'macd_short' : [],
                'macd_long' : [],
                'p_sale' : []
            }