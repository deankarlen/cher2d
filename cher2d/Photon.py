
import numpy as np
from scipy import stats

class Photon:
    """
    An Photon object has a starting point, starting time, and angle

    """

    VELOCITY = 299.79/1.333

    def __init__(self, t, x, y, angle):
        """Constructor
        """
        self.t = t
        self.x = x
        self.y = y
        self.angle = angle
        # the following uniform random numbers (0,1) are used to produce event information for this photon
        # this is done to reduce unnecessary variance when comparing the performance of two detectors
        # analyzing the same event
        self.random_numbers_uniform = stats.uniform.rvs(size=2)
        self.random_numbers_norm = stats.norm.rvs(size=2)