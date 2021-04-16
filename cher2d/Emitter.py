from cher2d.DesignProperty import DesignProperty
from cher2d.Device import Device
from cher2d.Photon import Photon
from cher2d.Event import Event
import numpy as np
from scipy import stats

class Emitter(Device):
    """
    An Emitter object produces Cherenkov radiation

    """

    def __init__(self, emitter_id: int, design_properties: list):
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

        while len(self.photons)<100000:
            travel = stats.expon.rvs(scale=1./density)
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
        add_prop('y', 'y coordinate of starting point (mm)', 'float', 'norm', 0.0, 0.1)
        add_prop('angle', 'angle wrt to x axis (rad)', 'float', 'norm', 0.0, 0.1)
        add_prop('length', 'path length of emission (mm)', 'float', 'norm', 1000.0, 0.1)

        # cherenkov angle
        add_prop('ch_angle', 'cherenkov emission angle (rad)', 'float', 'norm', 0.733, 0.001)

        # photon emission probability per unit length
        add_prop('ch_density', 'cherenkov emission probability (per mm)', 'float', 'norm', 0.01, 0.00001)

        # emitter velocity
        add_prop('velocity','velocity of the emitter particle (mm/ns)', 'float', 'exact', 299.79, 0.)


        return design_properties

    def get_event(self, detector) -> Event:
        """Produce an event from the photons
        """
        event = Event(detector)

        n_module = detector.true_properties['n_module'].get_value()
        for photon in self.photons:
            x0 = photon.x
            y0 = photon.y

            # see if photon crosses a module:
            for i_module in range(n_module):
                istr = str(i_module)
                x_m = detector.true_properties['x_' + istr].get_value()
                y_m = detector.true_properties['y_' + istr].get_value()
                angle_m = detector.true_properties['angle_' + istr].get_value()
                module = detector.photo_sensor_modules[i_module]
                width = module.true_properties['width'].get_value()

                x, y = module.find_intersection(photon, [x_m, y_m, angle_m])
                dist_m = np.sqrt((x - x_m) ** 2 + (y - y_m) ** 2)
                if dist_m < width / 2.:
                    # see if photon crosses a sensor
                    n_sensor = module.true_properties['n_sensor'].get_value()
                    for i_sensor in range(n_sensor):
                        istr = str(i_sensor)
                        x_s = module.true_properties['x_' + istr].get_value()
                        y_s = module.true_properties['y_' + istr].get_value()
                        angle_s = module.true_properties['angle_' + istr].get_value()
                        sensor = module.photo_sensors[i_sensor]
                        width_s = sensor.true_properties['width'].get_value()

                        x_d, y_d, angle_d = sensor.get_global_orientation([x_s, y_s, angle_s], [x_m, y_m, angle_m])
                        x, y = sensor.find_intersection(photon, [x_d, y_d, angle_d])
                        dist_s = np.sqrt((x - x_d) ** 2 + (y - y_d) ** 2)
                        if dist_s < width_s/2.:
                            distance = np.sqrt((x0-x)**2 + (y0-y)**2)
                            t = photon.t + distance/photon.VELOCITY
                            event.add_pe(i_module, i_sensor,t)
                            break

                    break
        return event
