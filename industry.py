import random
import math
import statistics

import math_extras

import debug

"""Industry simulation model; demand classes are food (0) and items (1)."""


class Industry:
    global_id = 0

    demand_class = 0

    cap_rate_base = 0
    cap_rate = 0
    last_layoff_time = 0
    last_layoff_quant = 0
    risk_factor = 1

    wage = 10
    unit_price = 0.6

    tax_rate = 0
    budget = 0

    pop_active = True
    desc = ''

    @property
    def employment(self):
        return len(self.employees)

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
        info = (
            f'DE_TYPE: {self.demand_class}, {self.desc}\n'
            f'   BUDGET: {self.budget}\n'
            f'   R_factor: {self.risk_factor}, HIST_LEN: {self.demand_hist_length}\n'
            f'   EMPLOYED: {self.employment}'
            f'   CAP: {self.employment * self.cap_rate}\n'
            f'   L_Q: {self.last_layoff_quant}   L_T: {self.last_layoff_time}'
        )
        return info

    def add_sales(self, sale):
        """Add a sale figure to historical data tracking."""
        self.sales_hist.insert(0, sale)
        if len(self.sales_hist) > self.sale_hist_length:
            self.sales_hist.pop()

    def add_demand(self, demand):
        """Add demand figures to historical data."""
        self.demand_hist.insert(0, demand)
        if len(self.demand_hist) > self.demand_hist_length:
            self.demand_hist.pop()

    # Calculate the basic moving-average indicator.
    def macd(self, data):
        """Calculate MACD with periods adjusted by the industry risk factor."""
        period_adjustment = int(5 * self.risk_factor)
        period_short = 10 - period_adjustment
        period_long = 20 - period_adjustment

        data_short = data[:period_short]
        data_long = data[:period_long]
        if len(data_short) == 0 or len(data_long) == 0:
            return 0

        m_short = sum(data_short) / len(data_short)
        m_long = sum(data_long) / len(data_long)

        if debug.DATA_MODE:
            self.data['macd_short'].append(m_short)
            self.data['macd_long'].append(m_long)

        return m_short - m_long

    # Calculate the demand-weighted average.
    def d_wavg(self):
        # Calculate recent volatility.
        last_n = self.demand_hist[0:10]
        if len(last_n) >= 3:
            std = statistics.stdev(last_n)
            mean_recent = abs(statistics.mean(last_n))
        else:
            std = 0.0
            mean_recent = abs(last_n[0]) if last_n else 0.0

        # Normalize volatility.
        if std > 2.0:
            norm_scale = std / (mean_recent + 1e-6)
            reduction = int(5 * min(norm_scale, 1.0))
        else:
            reduction = 0

        # Adjust the weighted-average length based on recent volatility.
        dynamic_length = max(1, min(self.demand_hist_length - reduction, self.demand_hist_length))
        if debug.DATA_MODE:
            self.data['dynamic_length'].append(dynamic_length)

        if dynamic_length == 0:
            return 0

        # Weight recent observations more heavily and normalize by total weight.
        sample_count = min(dynamic_length, len(self.demand_hist))
        weights = range(sample_count, 0, -1)
        weighted_demand = sum(
            self.demand_hist[i] * weight
            for i, weight in enumerate(weights)
        )
        return weighted_demand / sum(weights)

    def sales_trend(self):
        """Return a one-number realized-profit trend based on the MACD difference."""
        return self.macd(self.sales_hist)

    def tune(self, population):
        self.adjust(population)
        if debug.DATA_MODE:
            self.data['wf'].append(self.employment)

    def layoff(self, amount, population):
        if type(amount) != int:
            raise ValueError('non integer layoff!')
        if amount < 0 or amount > self.employment or self.employment == 0:
            raise ValueError('layoff amount must be within the current workforce')

        # Calculate the percentage laid off.
        self.last_layoff_quant = amount / self.employment

        # Remove workers from the industry and return them to the workforce.
        laid_off = self.employees[-amount:] if amount else []
        population.unemploy(laid_off)
        if amount:
            del self.employees[-amount:]
        self.debug_log(f'fire {amount}')

        self.last_layoff_time = 0

    def expenses(self):
        wages = self.employment * self.wage
        for pop in self.employees:
            pop.net_worth += self.wage

        self.debug_log('    Expenses')
        self.debug_log(f'        Wages: {wages}')

        return wages

    def hire(self, amount, population):
        if type(amount) != int:
            raise ValueError('non integer employment!')
        employees = population.employ(amount)
        self.employees.extend(employees)
        self.debug_log(f'hire {amount}')

    def fail(self, population):
        # Return its workers to the workforce.
        population.unemploy(self.employees)
        self.employees.clear()
        # Mark the industry inactive.
        self.active = False

    # Expand based on demand that is not currently met.
    def demand_expand(self, population, expansion):
        """Hire workers to meet additional demand when resources allow."""
        # Ignore non-positive unmet demand.
        if expansion <= 0:
            self.debug_log('no expansion demand')
            return

        possible_sale = (expansion * self.unit_price)
        # Avoid division by zero for the production rate.
        cap = max(self.cap_rate, 1e-6)
        possible_cost = (int(expansion / cap) * self.wage)

        # Calculate the theoretical workforce required to fulfill demand.
        max_workers = int(math.ceil(expansion / cap))

        # Calculate the number of workers the industry can afford.
        budgeted_workers = int((self.budget * self.risk_factor) / max(self.wage, 1e-6))

        # Check the available workforce.
        aval_workers = population.unemployed

        # Limit each update to 10% of the current workforce, or one new worker.
        hire_limit = max(1, math.ceil(self.employment * 0.1))
        hires = min(max_workers, aval_workers, budgeted_workers, hire_limit)

        hires = int(max(0, hires))

        self.debug_log(f'd_pop {hires} theoretical max {max_workers}, workforce available {aval_workers}, afford {budgeted_workers}')
        if hires <= 0:
            if aval_workers == 0:
                self.debug_log('no workforce')
            else:
                self.debug_log('cannot afford to hire')
            return

        # Hire the available workers.
        self.hire(hires, population)

    def recent_demand_volatility(self):
        volatility_hist = 10
        volatility = 0

        # Ignore volatility estimates with fewer than 11 samples.
        if len(self.demand_hist) > volatility_hist:
            mean = abs(statistics.mean(self.demand_hist[0:volatility_hist]))
            if mean != 0:
                volatility = (
                    statistics.stdev(self.demand_hist[0:volatility_hist]) / mean
                )

        # Clamp volatility to the configured scale.
        max_vol = 6
        volatility = min(volatility, max_vol)

        return volatility / max_vol

    def demand_contract(self, population):
        """Lay off workers based on recent demand volatility and industry risk."""
        # Skip the contraction when there are no workers to lay off.
        if self.employment == 0:
            return
        self.debug_log(f'demand based layoff')

        # Higher volatility and lower risk tolerance increase the layoff proportion.
        volatility = self.recent_demand_volatility()
        self.debug_log(f'recent demand volatility {volatility}')
        unemp = int(self.employment * (volatility * (1 - self.risk_factor)))

        # Keep layoffs within the workforce and lay off at least one worker.
        unemp = min(unemp, self.employment)
        unemp = max(unemp, 1)
        self.layoff(unemp, population)

    def adjust(self, population):
        if self.budget < 1 or (len(self.sales_hist) > debug.DEFUNCT_PERIOD and self.employment == 0):
            self.fail(population)
            return

        # Get demand and sales trends.
        demand_trend = self.d_wavg()
        sale_trend = self.sales_trend()
        demand_vol = self.recent_demand_volatility()

        # Estimate how many iterations the budget can cover current wages.
        expense_eta = int(self.budget / max((self.wage * self.employment), 1))

        # Increase the time since the last layoff.
        if self.last_layoff_time is not None:
            self.last_layoff_time += 1
        self.debug_log(f'expansion_req: {self.demand_hist[0]}, demand_trend: {demand_trend}, expense_eta: {expense_eta}, sale_trend: {sale_trend} budget: {self.budget}, wf: {self.employment}')

        # sale_trend is currency; demand_vol is unitless; expense_eta is iterations.
        hiring_indicator = (sale_trend + demand_trend) / max(demand_vol, 1e-6)

        # Clamp and scale the hiring indicator.
        indicator_clamp = 100
        if hiring_indicator > 0:
            hiring_indicator = min(hiring_indicator, indicator_clamp)
        if hiring_indicator < 0:
            hiring_indicator = max(hiring_indicator, -indicator_clamp)
        hiring_indicator = hiring_indicator / indicator_clamp

        if debug.DATA_MODE:
            self.data['budget'].append(self.budget)
            self.data['weighted_trend'].append(demand_trend)
            self.data['demand_volatility'].append(demand_vol)
            self.data['sale_trend'].append(sale_trend)
            self.data['hiring_indicator'].append(hiring_indicator)

        if debug.GREMLINS and random.random() > debug.GREMLIN_RATE:
            if self.employment == 0:
                return
            gremlin_quota = int((self.employment * random.random() * 0.1))
            self.debug_log(f'GREMLIN {gremlin_quota}')
            self.layoff(gremlin_quota, population)
            return

        if self.employment != 0 and (
            sale_trend < 0 or hiring_indicator < -0.5
        ):
            self.demand_contract(population)

        elif expense_eta < 2 and self.employment != 0:
            self.debug_log(f'expense based layoff')
            unemp = int(0.9 * self.employment)
            self.layoff(unemp, population)

        elif hiring_indicator > 0.5:
            self.demand_expand(population, self.demand_hist[0])

    def sale(self, demand, consumers=None):
        self.debug_log(f'---------- SALE ----------')
        self.demand_exceed = int(demand - (self.employment * self.cap_rate))
        self.debug_log(f'market demand {demand}, industry available {self.employment * self.cap_rate}, unmet demand {self.demand_exceed}')

        # Sell goods
        tax = 0
        capacity = max(0, self.employment * self.cap_rate)
        if consumers is None:
            sale_raw = min(demand, capacity)
        else:
            sale_raw = 0
            remaining_capacity = capacity
            for consumer, requested in consumers:
                if remaining_capacity <= 0:
                    break
                purchased = consumer.purchase(
                    min(requested, remaining_capacity),
                    self.unit_price,
                )
                sale_raw += purchased
                remaining_capacity -= purchased

        sale = sale_raw * self.unit_price
        tax = sale * self.tax_rate
        income = sale - tax
        self.budget += income
        self.debug_log(f'raw sale units {sale_raw}, sale (currency) {sale}, tax {tax}')
        self.debug_log(f'   Income')
        self.debug_log(f'       Sales {income}')

        # Subtract expenses.
        expenses = self.expenses()
        self.budget -= expenses
        self.debug_log(f'profit         {income - expenses}')
        self.debug_log(f'Final budget:  {self.budget}')

        theoretical_sale = (self.demand_exceed * self.unit_price) - (
            self.wage * (self.demand_exceed / self.cap_rate)
        )
        self.debug_log(f'Perfect sale: {theoretical_sale}')

        # Store demand and realized profit for trend analysis.
        self.add_demand(demand)
        self.add_sales(income - expenses)
        if debug.DATA_MODE:
            self.data['demand'].append(demand)
            self.data['demand_exceed'].append(self.demand_exceed)
            self.data['expenses'].append(expenses)
            self.data['profit'].append(income - expenses)
            self.data['p_sale'].append(theoretical_sale)

        return demand - sale_raw, tax, sale_raw

    def get_data(self):
        if not debug.DATA_MODE:
            return None
        return self.data

    def __init__(self, risk_factor, cap_rate, taxes, pop_active, demand_class, global_id, desc):
        self.cap_rate_base = cap_rate
        self.cap_rate = cap_rate
        self.risk_rate = 1
        self.last_layoff_time = None
        self.last_layoff_quant = 0
        self.employees = []

        self.tax_rate = taxes
        self.budget = 1000 + (500 * random.random())

        # Set population parameters.
        self.pop_active = pop_active
        self.demand_class = demand_class

        # Set industry metadata.
        self.desc = desc
        self.global_id = global_id

        if risk_factor < 0:
            risk_factor = 0
        if risk_factor > 1:
            risk_factor = 1
        self.risk_factor = risk_factor

        # Configure data history.
        self.demand_hist_length = max(debug.MAX_HIST - int(debug.MAX_HIST * self.risk_factor), 15)
        self.sale_hist_length = 50
        self.demand_hist = [0]
        self.sales_hist = [0]

        self.active = True

        if debug.DATA_MODE:
            self.data = {
                'demand': [],
                'demand_volatility': [],
                'demand_exceed': [],
                'hiring_indicator': [],
                'wf': [],
                'budget': [],
                'weighted_trend': [],
                'dynamic_length': [],
                'expenses': [],
                'profit': [],
                'macd_short': [],
                'macd_long': [],
                'p_sale': [],
                'sale_trend': [],
            }