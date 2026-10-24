import random

class DemandGenerator:
    '''
        Generate random walks for N categories
    '''
    
    def get_next(self):
        """
            Get the next set of random walk values
        """
        self.values = [max(random.gauss(mu = value, sigma = var),0) for value,var in zip(self.values, self.variances)]
        return self.values
    
    def __init__(self, types: int, starting_means: list, starting_variances:  list):
        if len(starting_means) != types or len(starting_variances) != types:
            raise ValueError("mismatched means or variances")
        self.n = types
        self.values = starting_means
        self.variances = starting_variances