from cher2d.Property import Property
from cher2d.TrueProperty import TrueProperty
import numpy as np
from scipy import stats


class DesignProperty(Property):
    """
    A DesignProperty object holds description and the distribution for multiple instances

    """

    DISTRIBUTIONS = ['exact', 'norm', 'gamma', 'beta', 'uniform']

    def __init__(self, name: str, description: str, property_type: str,
                 distribution: str, mean, sigma):
        """Constructor
        """
        super().__init__(name, description, property_type)

        if distribution not in self.DISTRIBUTIONS:
            buff = '/'.join(self.DISTRIBUTIONS)
            raise ValueError('Error in constructing DesignProperty (' + self.name +
                             '): distribution must be one of:', buff)
        self.distribution = distribution

        if distribution == 'beta' and (mean <= 0. or mean >= 1.):
            raise ValueError('Error in constructing DesignProperty (' + self.name +
                             '): beta distribution mean outside range (0,1)')
        self.mean = mean
        self.sigma = sigma

    def get_TrueProperty(self):
        """Return a TrueProperty object according to the distribution
        """

        true_value = None

        if self.distribution == 'exact':
            true_value = self.mean

        elif self.distribution == 'norm':
            true_value = stats.norm.rvs(self.mean, self.sigma)

        elif self.distribution == 'gamma':
            loc = 0.
            a = (self.mean / self.sigma) ** 2
            scale = self.sigma ** 2 / self.mean
            true_value = stats.gamma.rvs(a, loc, scale)

        elif self.distribution == 'beta':
            term = (self.mean * (1. - self.mean)) / self.sigma ** 2 - 1.
            a = term * self.mean
            b = term * (1. - self.mean)
            true_value = stats.beta.rvs(a, b)

        elif self.distribution == 'uniform':
            scale = self.sigma * np.sqrt(12.)
            loc = self.mean - scale / 2.
            true_value = stats.uniform.rvs(loc, scale)

        return TrueProperty(self.name, self.description, self.property_type, true_value)
