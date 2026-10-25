import random
import math
import statistics

import math_extras

import debug

class Industry:
    """
        Simple industry agent
    """
    @property
    def unit_price(self):
        return self._unit_price

    @unit_price.setter
    def unit_price(self, value):
        self._unit_price = value

    @property
    def labor(self):
        return self._labor

    @labor.setter
    def labor(self, value):
        self._labor = value

    @property
    def wage(self):
        return self.wages

    @wage.setter
    def wage(self, value):
        self.wages = value

    def debug_log(self, msg: str) -> None:
        '''
            Print msg to console
        '''
        if debug.IND_DEBUG:
            print(f'Industry {self.id}: {msg}')
            

    def get_data(self):
        '''
            Get internal testing data
        '''
        if not debug.DATA_MODE:
            raise ValueError("data mode not enabled")
        return self.data
     
    def layoff(self, amount: int):
        '''
            Decrease labor pool
        '''
        if amount <= 0:
            raise ValueError(f"Cannot fire negative employees: {amount}")
        if self.labor == 0:
            raise ValueError(f"No employees to fire")
        self.labor = max(self.labor - amount, 0)
        
    def hire(self, amount: int):
        '''
            Increase labor pool
        '''        
        if amount <= 0:
            raise ValueError(f"Cannot hire negative employees: {amount}")
        self.labor += amount
    
    def add_sales_figures(self, sales: list):
        '''
            Add sales to internal memory
        '''
        self.sales_history.insert(0, sales)
        
        # limit sales history to 100 cycles
        if len(self.sales_history) > 100:
            self.sales_history.pop()
    
    def produce(self) -> list:
        """
            Return supply unit created by this firm
        """
        return [self.labor * l_coeff * capacity for capacity,l_coeff in zip(self.capacity, self.labor_coeff)] 
        
    def sell(self, units_sold: list, tax_rate: list):
        '''
            Calculate income based on units sold
        '''
        # store current tax rate
        self.tax_rate = tax_rate
        
        # calculate profit
        total_income = sum([ units * tax * price for units,tax,price in zip(units_sold, tax_rate, self.unit_price)])
        total_expenses = self.wage * self.labor
        
        profit = total_income - total_expenses
        self.budget += profit
        
        # add sales to sale history
        self.add_sales_figures(sales=units_sold)
        
        # calculate demand ratio
        production = self.produce()
        self.demand_ratio = [demand / max(supply, 1e-6) for supply, demand in zip(production, units_sold)]
        
        if debug.DATA_MODE:
            self.data['fundamentals'].append([total_income, total_expenses])
            self.data['budget'].append(self.budget)
            self.data['profit'].append(profit)
            self.data['units_sold'].append(units_sold)
            self.data['demand_ratio'].append(self.demand_ratio)
    
    def update_labor_coeff(self):
        # calculate optimal coefficents
        gradient = [max(self.labor * cap, sales) * price for cap,price,sales in zip(self.capacity,self.unit_price, self.sales_history[0])]
        gradient = [g / max(sum(gradient),1e-6) for g in gradient]
        
        # apply step adjustment
        diff = [(g - cur) / self.spec_param for cur,g in zip(self.labor_coeff, gradient)]
        self.labor_coeff = [coeff + adj for coeff,adj in zip(self.labor_coeff,diff)]
    
        '''
        if debug.DATA_MODE:
            self.data.setdefault('labor_coeff', []).append(self.labor_coeff)
        '''
    
    
    def estimate_demand(self) -> float:
        # current demand = units sold
        current_demand = self.sales_history[0]
        
        # future demand
        possible_sales = [(self.economic_data['income'] / unit) - sold for unit,sold in zip(self.unit_price,current_demand)]
        
        return possible_sales
        
    
    def adjust(self, economic_data: dict):
        '''
            Make adjustments to company
        '''
        # store market data
        self.economic_data = economic_data
        
        # adjust price
        self.unit_price = self.unit_price
        
        future_demand = self.estimate_demand()
        
        # adjust labor coefficents
        self.update_labor_coeff() 
        
        
        # utility of hiring
        income_possible = [i for i in range(0,debug.DEMAND_CLASSES_N)]
        for i in range(0,debug.DEMAND_CLASSES_N):
            maximum_supply = self.labor * self.labor_coeff[i] * self.capacity[i]
            # demand larger than supply
            if future_demand[i] > maximum_supply:
                income = self.labor * self.labor_coeff[i] * self.capacity[i] * self.unit_price[i] * self.tax_rate[i]
            # supply larger than demand
            else:
                income = -self.wage
            
            income_possible[i] = income
            
        hiring_utility = sum(income_possible) - self.wage
        
        if hiring_utility > 0:
            self.debug_log('hire event')
            self.hire(1)
            
        if hiring_utility < 0 and self.labor != 0:
            self.debug_log('layoff event')
            self.layoff(1)
            
        if debug.DATA_MODE:
            self.data['labor'].append(self.labor)
            self.data['wage'].append(future_demand)
            self.data['unit_price'].append(self.unit_price)
            self.data.setdefault('hire_util', []).append(hiring_utility)
        
    
    def __init__(self, id: int, risk_factor: float, specialisation_param: int):
        # get meta
        self.id = id
        self.risk_factor = risk_factor
        
        # internal estimation 
        self.sales_history = []
        self.economic_data = []
        
        # internal variables
        self.unit_price = [5 for i in range(0, debug.DEMAND_CLASSES_N)]
        self.labor_coeff = [1 / debug.DEMAND_CLASSES_N for i in debug.DEMAND_CLASSES]
        self.capacity = [1 for i in range(0, debug.DEMAND_CLASSES_N)]
        
        self.wage = 4
        self.labor = 10
        
        self.budget = 0
        
        # independent parameters
        self.spec_param = specialisation_param
        
        if debug.DATA_MODE:
            self.data = {
                'fundamentals' : [],
                'profit' : [],
                'budget' : [],
                'labor' : [],
                'wage' : [],
                'units_sold' : [],
                'unit_price' : [],
                'indicators' : [],
                'demand_ratio' : [],
            }
        