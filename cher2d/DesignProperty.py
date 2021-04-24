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
        self.devices = []

        self.__offset = None
        if property_type == 'int':
            self.set_offset(0)
        else:
            self.set_offset(0.)

    def add_device(self, device):
        if device not in self.devices:
            self.devices.append(device)

    def get_offset(self):
        """
        Return the offset applied

        """
        return self.__offset

    def set_offset(self, offset):
        """
        Set an offset value of the property to study sensitivity to systematic parameters
        - after changing the offset, these are applied to any devices built with this design property

        """
        offset_type = type(offset).__name__
        # avoid issues with float64 vs float
        if offset_type[:len(self.property_type)] != self.property_type:
            raise TypeError('Property (' + self.name +
                            ') offset type (' + type(offset).__name__ +
                            ') does not match property_type (' +
                            self.property_type + ')')

        if len(self.devices) > 0:
            diff_offset = offset - self.__offset
            for device in self.devices:
                value = device.true_properties[self.name].get_value()
                device.true_properties[self.name].set_value(value + diff_offset)

        self.__offset = offset

    def get_TrueProperty(self, exact):
        """Return a TrueProperty object according to the distribution and offset
        """

        true_value = None

        if exact or self.distribution == 'exact':
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

        # apply the offset
        true_value += self.__offset

        return TrueProperty(self.name, self.description, self.property_type, true_value)
