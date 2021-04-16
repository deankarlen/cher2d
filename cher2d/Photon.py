
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