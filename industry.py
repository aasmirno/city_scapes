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
        return [capacity * self.labor for capacity in self.capacity] 
        
    def sell(self, units_sold: list, tax_rate: list):
        '''
            Calculate income based on units sold
        '''
        # calculate profit
        total_income = sum([ units * tax * price for units,tax,price in zip(units_sold, tax_rate, self.unit_price)])
        total_expenses = self.wage * self.labor
        
        profit = total_income - total_expenses
        self.budget += profit
        
        # add sales to sale history
        self.add_sales_figures(sales=units_sold)
        
        if debug.DATA_MODE:
            self.data['income'].append(total_income)
            self.data['expense'].append(total_expenses)
            self.data['units_sold'].append(units_sold)
    
    
    def adjust(self, tax_rate: list, estimated_price: list):
        '''
            Make adjustments to company
        '''
        expected_sale_diff = 0.1
        expected_sales = [expected_sale_diff + sale for sale in self.sales_history[0]]
        
        # partial derivatives for profit formula
        unit_price_profit = sum([sale * tax for sale,tax in zip(expected_sales, tax_rate)])
        
        labor_profit = sum([cap * price * tax for cap,price,tax in zip(self.capacity, self.unit_price, tax_rate)]) - self.wage
        wage_profit = -self.labor
        
        options = [unit_price_profit, labor_profit, wage_profit]
        optimal_index = options.index(max(options))
        
        if optimal_index == 0: # unit price change
            self.unit_price = [up + 0.1 for up in self.unit_price]
        elif optimal_index == 1: # labor change
            self.layoff(amount=1)
        elif optimal_index == 2: # wage change
            self.wage += 1
        else:
            raise ValueError(f'Optimal index out of bounds {optimal_index}')
            
        if debug.DATA_MODE:
            self.data['labor'].append(self.labor)
            self.data['wage'].append(self.wage)
            self.data['unit_price'].append(self.unit_price)
            self.data['gradients'].append(options)
        
    
    def __init__(self, id: int, risk_factor: float):
        # get meta
        self.id = id
        self.risk_factor = risk_factor
        
        # internal estimation 
        self.sales_history = []
        
        # internal variables
        self.unit_price = [5 for i in range(0, debug.DEMAND_CLASSES_N)]
        self.wage = 4
        self.labor = 10
        
        self.capacity = [1 for i in range(0, debug.DEMAND_CLASSES_N)]
        
        self.constraints = [1,1,1]
        
        self.budget = 0
        
        if debug.DATA_MODE:
            self.data = {
                'income' : [],
                'expense' : [],
                'units_sold' : [],
                'labor' : [],
                'wage' : [],
                'unit_price' : [],
                'gradients' : []
            }
        