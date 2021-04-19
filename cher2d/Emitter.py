from cher2d.DesignProperty import DesignProperty
from cher2d.Device import Device
from cher2d.Photon import Photon
import numpy as np
from scipy import stats


class Emitter(Device):
    """
    An Emitter object produces Cherenkov radiation

    """

    def __init__(self, emitter_id: int, design_properties: dict):
        """Constructor
        """
        super().__init__(emitter_id, design_properties)

        self.photons = None

    def emit(self, t0: float):
        """Produce Cherenkov photons starting at time t0 (ns)
        """
        self.photons = []

        # travel along the emitter direction, producing photons on either side of emitter
        dist = 0.
        density = self.true_properties['ch_density'].get_value()

        emission_time = t0
        emitter_velocity = self.true_properties['velocity'].get_value()
        emitter_x = self.true_properties['x'].get_value()
        emitter_y = self.true_properties['y'].get_value()
        emitter_angle = self.true_properties['angle'].get_value()
        ch_angle = self.true_properties['ch_angle'].get_value()

        while len(self.photons) < 100000:
            travel = stats.expon.rvs(scale=1. / density)
            dist += travel
            if dist < self.true_properties['length'].get_value():
                sign = 1.
                if np.random.rand() < 0.5:
                    sign = -1.
                emission_angle = emitter_angle + sign * ch_angle
                emission_time += travel / emitter_velocity
                emitter_x += travel * np.cos(emitter_angle)
                emitter_y += travel * np.sin(emitter_angle)
                self.photons.append(Photon(emission_time, emitter_x, emitter_y, emission_angle))
            else:
                break

    @classmethod
    def default_properties(cls) -> dict:
        """ Return a dictionary with the default Emitter design properties
        :rtype: dict
        """

        def add_prop(name: str, description: str, property_type: str, distribution: str, mean, sigma):
            if name in design_properties:
                raise ValueError('Default properties definition has duplicate names:', name)
            design_properties[name] = DesignProperty(name, description, property_type, distribution, mean, sigma)

        design_properties = {}

        # starting position, direction, length
        add_prop('x', 'x coordinate of starting point (mm)', 'float', 'norm', -2000.0, 0.1)
        add_prop('y', 'y coordinate of starting point (mm)', 'float', 'norm', 3000.0, 0.1)
        add_prop('angle', 'angle wrt to x axis (rad)', 'float', 'norm', -0.6, 0.1)
        add_prop('length', 'path length of emission (mm)', 'float', 'norm', 1000.0, 0.1)

        # Cherenkov angle
        add_prop('ch_angle', 'Cherenkov emission angle (rad)', 'float', 'norm', 0.733, 0.001)

        # photon emission probability per unit length
        add_prop('ch_density', 'Cherenkov emission probability (per mm)', 'float', 'norm', 0.03*100, 0.00001)

        # emitter velocity
        add_prop('velocity', 'velocity of the emitter particle (mm/ns)', 'float', 'exact', 299.79, 0.)

        return design_properties
