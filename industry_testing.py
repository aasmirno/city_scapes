import random

import matplotlib.pyplot as plt

from industry import Industry
from math_extras import DemandGenerator
import debug


def graph_industries(industries: list):
    """Plot each industry's recorded data series in a separate column."""
    industry_data = [(industry, industry.get_data()) for industry in industries]
    if not industry_data:
        raise ValueError("No industries available to graph")

    data_keys = list(
        dict.fromkeys(
            key
            for _, data in industry_data
            for key, values in data.items()
            if values
        )
    )
    if not data_keys:
        raise ValueError("No industry data available to graph")

    figure, axes = plt.subplots(
        len(data_keys),
        len(industry_data),
        squeeze=False,
        figsize=(4 * len(industry_data) + 2, 3 * len(data_keys)),
    )
    industry_labels = []
    used_labels = set()
    for index, (industry, _) in enumerate(industry_data):
        label = f"Industry {getattr(industry, 'id', index)}"
        if label in used_labels:
            label = f"{label} ({index + 1})"
        used_labels.add(label)
        industry_labels.append(label)

    for row, key in enumerate(data_keys):
        for index, (industry, data) in enumerate(industry_data):
            axis = axes[row, index]
            values = data.get(key, [])
            if not values:
                axis.set_visible(False)
                continue

            label = industry_labels[index]
            is_nested = any(isinstance(value, (list, tuple)) for value in values)
            component_count = (
                max(
                    len(value) if isinstance(value, (list, tuple)) else 1
                    for value in values
                )
                if is_nested
                else 1
            )

            for component in range(component_count):
                series = []
                for value in values:
                    if isinstance(value, (list, tuple)):
                        series.append(
                            value[component] if component < len(value) else None
                        )
                    else:
                        series.append(value if component == 0 else None)
                series_label = (
                    f"{label} ({key} {component})" if is_nested else label
                )
                line, = axis.plot(series, label=series_label)

            if row == 0:
                axis.set_title(label)
            if index == 0:
                axis.set_ylabel(key.replace("_", " ").title())
            if row == len(data_keys) - 1:
                axis.set_xlabel("Cycle")
            axis.legend()

    figure.tight_layout()
    plt.show()
    return figure


def graph_demand(demand_history: list, income_history: list):
    """Plot generated demand and income over time in a separate figure."""
    if not demand_history:
        raise ValueError("No generated demand available to graph")
    if len(income_history) != len(demand_history):
        raise ValueError("Demand and income histories must have matching lengths")

    category_count = len(demand_history[0])
    if any(len(demand) != category_count for demand in demand_history):
        raise ValueError("Generated demand must have a consistent category count")

    figure, (demand_axis, income_axis) = plt.subplots(
        2,
        1,
        sharex=True,
        figsize=(10, 7),
    )
    for category in range(category_count):
        demand_axis.plot(
            [demand[category] for demand in demand_history],
            label=f"Demand category {category}",
        )

    demand_axis.set_title("Generated Demand")
    demand_axis.set_ylabel("Demand")
    demand_axis.legend()

    income_axis.plot(income_history, label="Generated income", color="tab:green")
    income_axis.set_title("Generated Income")
    income_axis.set_xlabel("Cycle")
    income_axis.set_ylabel("Income")
    income_axis.legend()

    figure.tight_layout()
    return figure


def assign_demand(demands: list, industry_supply: list) -> list:
    """Allocate each category's demand to the cheapest available industries."""
    # init results array
    sales = [[0 for _ in demands] for _ in industry_supply]

    # check for improper supply values
    for industry_index, (supply, unit_prices) in enumerate(industry_supply):
        if len(supply) != len(demands) or len(unit_prices) != len(demands):
            raise ValueError(
                "Demand, supply, and unit prices must have matching category counts"
            )
        if any(amount < 0 for amount in supply):
            raise ValueError("Industry supply cannot be negative")
        if any(price < 0 for price in unit_prices):
            raise ValueError("Unit prices cannot be negative")

    # check for improper demand values
    if any(demand < 0 for demand in demands):
        raise ValueError("Demand cannot be negative")

    for category, demand in enumerate(demands):
        remaining_demand = demand
        # sort by cheapest unit price and assign maximum demand
        cheapest_first = sorted(
            range(len(industry_supply)),
            key=lambda index: industry_supply[index][1][category],
        )
        for industry_index in cheapest_first:
            available = industry_supply[industry_index][0][category]
            allocated = min(remaining_demand, available)
            sales[industry_index][category] = allocated
            remaining_demand -= allocated
            if remaining_demand == 0:
                break

    return sales


'''
    Start testing section
'''
# testing parameters
industries = 2
spec_params = [1,5]
tax_rates = [0.9 for i in range(0, debug.DEMAND_CLASSES_N)]


ind_list = []

# create demand generator
demand_generator = DemandGenerator(types=debug.DEMAND_CLASSES_N,
                      starting_means=[0.5 for i in range(0,debug.DEMAND_CLASSES_N)],
                      starting_variances=[0.05 for i in range(0,debug.DEMAND_CLASSES_N)],
                      distrib='gauss')

# create income generator
income_generator = DemandGenerator(types=1,
                      starting_means=[10000],
                      starting_variances=[1000])

# population size
pop_size = 500

# create industries
for i in range(0, industries):
    ind_list.append(Industry(id=i, risk_factor=0.5, specialisation_param=spec_params[i]))
    
iterations = 500
demand_history = []
income_history = []
for i in range(0,iterations):
    demand = [100 * cat for cat in demand_generator.get_next()]
    
    
    demand_history.append(demand)
    supply = [(ind.produce(), ind.unit_price) for ind in ind_list]
    sales = assign_demand(demand, supply)

    income = income_generator.get_next()
    income_history.append(income[0])
    avg_industry_wage = sum([ind.wage for ind in ind_list]) / len(ind_list)
    for industry, units_sold in zip(ind_list, sales):
        industry.sell(units_sold, tax_rates)
        industry.adjust(economic_data = {'income':income[0]})
    
    
graph_demand(demand_history, income_history)
graph_industries(ind_list)



    
