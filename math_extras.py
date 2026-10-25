import random

class DemandGenerator:
    '''
        Generate random walks for N categories
    '''
    
    def get_next(self):
        """
            Get the next set of random walk values
        """
        if self.distribution == 'gauss':
            self.values = [max(random.gauss(mu = value, sigma = var),0) for value,var in zip(self.values, self.variances)]
        if self.distribution == 'gamma':
            gamma = [random.gammavariate(alpha=0.5,beta=1.0) for val in self.values]
            # negative values
            if random.uniform(-2,1) < 0:
                gamma = [val * -1 for val in gamma]
            self.values = [max(val + gam, 0) for val,gam in zip(self.values,gamma)]
        return self.values
    
    def __init__(self, types: int, starting_means: list, starting_variances:  list, distrib: str = 'gauss'):
        if len(starting_means) != types or len(starting_variances) != types:
            raise ValueError("mismatched means or variances")
        self.n = types
        self.values = starting_means
        self.variances = starting_variances
        self.distribution = distrib