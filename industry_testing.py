import random

import matplotlib.pyplot as plt

from industry import Industry
from math_extras import DemandGenerator
import debug


def graph_industries(industries: list):
    """Plot each recorded data series for all supplied industries."""
    industry_data = [(industry, industry.get_data()) for industry in industries]
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
        1,
        squeeze=False,
        figsize=(10, 4 * len(data_keys)),
    )

    for axis, key in zip(axes[:, 0], data_keys):
        for index, (industry, data) in enumerate(industry_data):
            values = data.get(key, [])
            if not values:
                continue

            label = f"Industry {getattr(industry, 'id', index)}"
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
                axis.plot(series, label=series_label)

        axis.set_title(key.replace("_", " ").title())
        axis.set_xlabel("Cycle")
        axis.legend()

    figure.tight_layout()
    plt.show()
    return figure

'''
    Start testing section
'''
# testing parameters
industries = 2
tax_rates = [0.9 for i in range(0, debug.DEMAND_CLASSES_N)]


ind_list = []

# create demand generator
demand_generator = DemandGenerator(types=debug.DEMAND_CLASSES_N,
                      starting_means=[0.5 for i in range(0,debug.DEMAND_CLASSES_N)],
                      starting_variances=[0.05 for i in range(0,debug.DEMAND_CLASSES_N)])

# create income generator
income_generator = DemandGenerator(types=debug.DEMAND_CLASSES_N,
                      starting_means=[10 for i in range(0,debug.DEMAND_CLASSES_N)],
                      starting_variances=[0.05 for i in range(0,debug.DEMAND_CLASSES_N)])

# create industries
for i in range(0, industries):
    ind_list.append(Industry(id=i, risk_factor=0.5))
    
iterations = 50
for i in range(0,iterations):
    demand = [1000 * cat for cat in demand_generator.get_next()]
    supply = [(ind.produce(), ind.unit_price) for ind in ind_list]
    
    ind_list[0].sell(demand, tax_rates)
    ind_list[0].adjust(tax_rates, income_generator.get_next())
    
    
graph_industries(ind_list)



    
