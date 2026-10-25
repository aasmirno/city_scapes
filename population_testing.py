import population
import matplotlib.pyplot as plt
import numpy as np


def graph_population_data(test_pop):
    """Plot every recorded series returned by a population's test data."""
    test_data = test_pop.get_test_data()
    if test_data is None:
        raise ValueError("Population test data is unavailable")

    data_series = {}
    for key, values in test_data.items():
        series = np.asarray(values)
        if series.size == 0:
            continue
        if series.ndim == 0:
            raise ValueError(f"Test data '{key}' must contain a series")
        if series.ndim == 1:
            series = series.reshape(-1, 1)
        else:
            series = series.reshape(series.shape[0], -1)
        data_series[key] = series

    if not data_series:
        raise ValueError("No population test data available to graph")

    figure, axes = plt.subplots(
        len(data_series),
        1,
        squeeze=False,
        figsize=(10, 4 * len(data_series)),
    )

    for axis, (key, series) in zip(axes[:, 0], data_series.items()):
        for column in range(series.shape[1]):
            label = key if series.shape[1] == 1 else f"{key} {column}"
            axis.plot(series[:, column], label=label)
        axis.set_title(key.replace("_", " ").title())
        axis.set_xlabel("Cycle")
        axis.legend()

    figure.tight_layout()
    plt.show()
    return figure

test_pop = population.Population()

for i in range(0,200):
    orders = test_pop.get_orders()
    
    test_pop.fill(orders)
    
    test_pop.pay([(id, 5) for id in range(test_pop.total_pop)])
        
    

graph_population_data(test_pop)

    