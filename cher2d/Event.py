#from cher2d.Detector import Detector
import numpy as np
from scipy import stats

class Event():
    """
    An event is a collection of signals for the photosensors

    """

    def __init__(self, detector):
        """Constructor
        """

        self.detector = detector
        self.n_module = self.detector.true_properties['n_module'].get_value()

        self.module_data = {}
        for i_module in range(self.n_module):
            self.module_data[i_module] = {}

    def add_pe(self, i_module, i_sensor, t):
        if i_sensor not in self.module_data[i_module]:
            self.module_data[i_module][i_sensor] = []
        self.module_data[i_module][i_sensor].append(t)