from cher2d.Device import Device
from cher2d.PhotoSensorModule import PhotoSensorModule
from cher2d.DesignProperty import DesignProperty
from cher2d.Event import Event
from cher2d.Photon import Photon
import numpy as np
from scipy import stats


class Detector(Device):
    """
    A Detector object is a group of PhotoSensorModules

    A position and angular PMT response is included as follows:
     - r is distance from centre of PMT
     - theta is angle of photon wrt normal of PMT surface (constant across surface)
     - h is half-width of PMT
     - qe_0 is the nominal quantum efficiency as specified by design property 'qe'
     - td_0 is the nominal time delay as specified by design property 'td'
     - boolean design properties turn on/off angular or radial effects
     - c_a is the quantum efficiency angular coefficient (c_a > 0)
     - c_q is quantum efficiency radial coefficient (-1 < c_q < 1)
     - c_t is time delay radial coefficient (-1 < c_r < 1

    Quantum efficiency:
    -------------------
    Two effects: thickness of photocathode traversed and probability that pe gets into PMT vacuum
    - the latter is qe_0
    - the former: prob for photon not to interact with pathlength d through a photocathode: exp(-d/d_0).
    the pathlength: d = k/cos(theta) where k is the photocathode thickness. The ratio d_0/k = c_a,
    specifies the strength of the angular effect (c_a->0 -> no effect)

    The following form ensures qe is between 0 and 1:

    qe = qe_0 * (1 - exp[-1 / c_a / cos(theta)]) * (1 + c_q * abs(r/h))/(1 + abs(c_q))

    Expectation calculation (for likelihood and Azimov events)
    E[QE] = qe_0 * (1 - exp[-1 / c_a / cos(theta)])  * 2 \int_0^h (1 + c_q *r/h) dr / 2 \int_0^h dr / (1 + abs(c_q))
          = qe_0 * (1 - exp[-1 / c_a / cos(theta)]) * (h + 1/2 c_q h^2/h)/h / (1 + abs(c_q))
          = qe_0 * (1 - exp[-1 / c_a / cos(theta)]) * (1 + 1/2 c_q) / (1 + abs(c_q))

    Time delay
    ----------

    delay = td_0 * (1 + c_t * abs(r/h))

    If both radial affects activated:

    E[TD] = td_0 * 2 \int_0^h (1 + c_t * r/h) (1 + c_q * r/h) dr  / 2 \int_0^h (1 + c_q * r/h) dr
          = td_0 * (h + 1/2 c_t h^2/h + 1/2 c_q h^2/h + 1/3 c_t c_q h^3/h^2) / (h + 1/2 c_q h^2/h)
          = td_0 * (1 +  1/2 c_t + 1/2 c_q + 1/3 c_t c_q) / (1 + 1/2 c_q)

    If only one not activated, set its coefficient to zero


    """

    def __init__(self, detector_id: int, design_properties: dict, photo_sensor_model_design_properties: dict,
                 photo_sensor_design_properties: dict, exact: bool = False):
        """Constructor
        """
        super().__init__(detector_id, design_properties, exact)

        # construct the detector by adding modules
        self.photo_sensor_modules = []
        for i_module in range(self.true_properties['n_module'].get_value()):
            self.photo_sensor_modules.append(PhotoSensorModule(i_module, photo_sensor_model_design_properties,
                                                               photo_sensor_design_properties, exact))

    def get_asimov(self, emitter, parameters: dict, truth: bool):
        """Produce an Asimov event: expectation values for n_pe and times
            - parameters: the emitter parameters that are being estimated
            - truth - True: for generating an Asimov event or False: use design_mean (for calculating likelihood)
        """
        asimov = Event(self)

        x_e = parameters['x']
        y_e = parameters['y']
        angle_e = parameters['angle']
        length_e = parameters['length']
        t0_e = parameters['t0']

        ch_density = emitter.get_value('ch_density', truth)
        velocity_e = emitter.get_value('velocity', truth)

        n_module = self.get_value('n_module', True)
        for i_module in range(n_module):
            i_str = str(i_module)
            x_m = self.get_value('x_' + i_str, truth)
            y_m = self.get_value('y_' + i_str, truth)
            angle_m = self.get_value('angle_' + i_str, truth)

            module = self.photo_sensor_modules[i_module]
            n_sensor = module.get_value('n_sensor', True)
            for i_sensor in range(n_sensor):
                i_str = str(i_sensor)
                x_s = module.get_value('x_' + i_str, truth)
                y_s = module.get_value('y_' + i_str, truth)
                angle_s = module.get_value('angle_' + i_str, truth)

                sensor = module.photo_sensors[i_sensor]
                width_s = sensor.get_value('width', truth)

                # The expected number of pe is calculated by finding the start and end point of the emitter path
                # that produces photons that hit the sensor

                x_s_0 = x_s - width_s / 2. * np.cos(angle_s)
                y_s_0 = y_s - width_s / 2. * np.sin(angle_s)
                x_d_0, y_d_0, angle_d = sensor.get_global_orientation([x_s_0, y_s_0, angle_s], [x_m, y_m, angle_m])

                x_s_1 = x_s + width_s / 2. * np.cos(angle_s)
                y_s_1 = y_s + width_s / 2. * np.sin(angle_s)
                x_d_1, y_d_1, angle_d = sensor.get_global_orientation([x_s_1, y_s_1, angle_s], [x_m, y_m, angle_m])

                for sign in [-1., 1.]:
                    # make a virtual photon that starts at one edge of sensor, and points back towards emitter
                    angle = angle_e + sign * emitter.get_value('ch_angle', truth) + np.pi
                    photon_0 = Photon(0., x_d_0, y_d_0, angle)
                    x_0, y_0 = module.find_intersection(photon_0, [x_e, y_e, angle_e])
                    t_0 = np.sqrt((x_0 - x_d_0) ** 2 + (y_0 - y_d_0) ** 2) / photon_0.VELOCITY
                    dist_0 = (x_0 - x_e) * np.cos(angle_e) + (y_0 - y_e) * np.sin(angle_e)
                    dist_0 = min(length_e, max(0., dist_0))

                    photon_1 = Photon(0., x_d_1, y_d_1, angle)
                    x_1, y_1 = module.find_intersection(photon_1, [x_e, y_e, angle_e])
                    t_1 = np.sqrt((x_1 - x_d_1) ** 2 + (y_1 - y_d_1) ** 2) / photon_1.VELOCITY
                    dist_1 = (x_1 - x_e) * np.cos(angle_e) + (y_1 - y_e) * np.sin(angle_e)
                    dist_1 = min(length_e, max(0., dist_1))

                    # path length contributing photons
                    path_length = np.abs(dist_1 - dist_0)
                    if path_length > 0.:
                        # expected number of photons: half of them on other side of emitter
                        n_photons_expected = path_length * ch_density / 2.
                        qe = sensor.get_value('qe', truth)
                        theta = angle - angle_d - np.pi/2.
                        if sensor.get_value('qe_angle', truth):
                            c_a = sensor.get_value('qe_angle_coeff', truth)
                            if c_a > 0.:
                                factor = np.exp(-1. / c_a / np.cos(theta))
                                qe *= (1. - factor)
                        n_expected = n_photons_expected * qe
                        c_qe = 0.
                        if sensor.get_value('qe_radial', truth):
                            c_qe = sensor.get_value('qe_radial_coeff', truth)
                            n_expected *= (1. * c_qe/2.)/(1. + abs(c_qe))

                        t_expected = 0.5 * (t_0 + t_1 + (dist_0 + dist_1) / velocity_e) + t0_e
                        # transit time delay (within PMT)
                        c_td = 0.
                        if sensor.get_value('td_radial', truth):
                            c_td = sensor.get_value('td_radial_coeff', truth)
                        delay = sensor.get_value('td', truth) * (1. + c_td/2. + c_qe/2. + c_td*c_qe/3.)/(1. + c_qe/2.)

                        asimov.add_pe(i_module, i_sensor, t_expected + delay, n_pe=n_expected)

        return asimov

    def get_event(self, emitter) -> Event:
        """Produce an event from the emitter photons
        """
        event = Event(self)

        n_pe = 0
        sum_times = 0.

        n_module = self.true_properties['n_module'].get_value()
        for photon in emitter.photons:
            x0 = photon.x
            y0 = photon.y

            # see if photon crosses a module:
            for i_module in range(n_module):
                i_str = str(i_module)
                x_m = self.true_properties['x_' + i_str].get_value()
                y_m = self.true_properties['y_' + i_str].get_value()
                angle_m = self.true_properties['angle_' + i_str].get_value()
                module = self.photo_sensor_modules[i_module]
                width = module.true_properties['width'].get_value()

                x, y = module.find_intersection(photon, [x_m, y_m, angle_m])
                dist_m = np.sqrt((x - x_m) ** 2 + (y - y_m) ** 2)
                if dist_m < width / 2.:
                    # see if photon crosses a sensor
                    n_sensor = module.true_properties['n_sensor'].get_value()
                    for i_sensor in range(n_sensor):
                        i_str = str(i_sensor)
                        x_s = module.true_properties['x_' + i_str].get_value()
                        y_s = module.true_properties['y_' + i_str].get_value()
                        angle_s = module.true_properties['angle_' + i_str].get_value()
                        sensor = module.photo_sensors[i_sensor]
                        width_s = sensor.true_properties['width'].get_value()

                        x_d, y_d, angle_d = sensor.get_global_orientation([x_s, y_s, angle_s], [x_m, y_m, angle_m])
                        x, y = sensor.find_intersection(photon, [x_d, y_d, angle_d])
                        dist_s = np.sqrt((x - x_d) ** 2 + (y - y_d) ** 2)
                        if dist_s < width_s / 2.:
                            # photon hit photocathode - was a photo-electron produced?
                            theta = photon.angle - angle_d + np.pi / 2.
                            qe = sensor.true_properties['qe'].get_value()
                            if sensor.true_properties['qe_angle'].get_value():
                                c_a = sensor.true_properties['qe_angle_coeff'].get_value()
                                if c_a > 0.:
                                    factor = np.exp(-1./c_a/np.cos(theta))
                                    qe *= (1. - factor)
                            if sensor.true_properties['qe_radial'].get_value():
                                c_qe = sensor.true_properties['qe_radial_coeff'].get_value()
                                qe *= (1. + c_qe * dist_s/(width_s/2.))/(1. + abs(c_qe))

                            if qe > photon.random_numbers_uniform[0]:
                                distance = np.sqrt((x0 - x) ** 2 + (y0 - y) ** 2)
                                t = photon.t + distance / photon.VELOCITY
                                # internal PMT delay
                                delay = sensor.true_properties['td'].get_value()
                                if sensor.true_properties['td_radial'].get_value():
                                    c_td = sensor.true_properties['td_radial_coeff'].get_value()
                                    delay *= (1. + c_td * dist_s/(width_s/2.))
                                t += delay
                                # incorporate timing resolution
                                t_obs = t + sensor.true_properties['t_sig'].get_value() * photon.random_numbers_norm[0]
                                event.add_pe(i_module, i_sensor, t_obs)
                                n_pe += 1
                                sum_times += t_obs
                            break
                    break

        # add dark noise (not yet in likelihood!)
        mean_time = sum_times / n_pe
        window = self.true_properties['readout_window'].get_value()
        for i_module in range(n_module):
            module = self.photo_sensor_modules[i_module]
            n_sensor = module.true_properties['n_sensor'].get_value()
            for i_sensor in range(n_sensor):
                sensor = module.photo_sensors[i_sensor]
                rate = sensor.true_properties['dark_noise_rate'].get_value()
                if rate > 0.:
                    n_expected = rate * window / 1.E9
                    n_dark = stats.poisson.rvs(n_expected)
                    if n_dark > 0:
                        for i_dark in range(n_dark):
                            t_obs = mean_time + (stats.uniform.rvs() - 0.5) * window
                            event.add_pe(i_module, i_sensor, t_obs)

        return event

    @classmethod
    def default_properties(cls):
        """ Return a dictionary with the default PhotoSensor design properties
        """

        def add_prop(name: str, description: str, property_type: str, distribution: str, mean, sigma):
            if name in design_properties:
                raise ValueError('Default properties definition has duplicate names:', name)
            design_properties[name] = DesignProperty(name, description, property_type, distribution, mean, sigma)

        design_properties = {}

        # readout properties:
        add_prop('readout_window', 'time window for event readout (about the mean time of signals) (ns)',
                 'float', 'exact', 50., 0.)

        # photosensor_modules: wall and floor
        n_set = 2
        n_module = 7
        add_prop('n_module', 'number of photosensor modules in detector', 'int', 'exact', n_module * n_set, 0)
        pitch = 700.
        add_prop('pitch', 'separation between centres of photosensor modules (mm)', 'float', 'exact', pitch, 0.)

        # first set makes up the floor
        x = -1. * (n_module - 1) / 2. * pitch - n_module * pitch / 2.
        for i_module in range(n_module):
            i_str = str(i_module)
            # positions of center of photosensor module active surfaces
            add_prop('x_' + i_str, 'x coordinate of center of module front surface (mm)',
                     'float', 'norm', x, 2.)
            add_prop('y_' + i_str, 'y coordinate of center of module front surface (mm) ',
                     'float', 'norm', 0., 2.)
            # orientation
            add_prop('angle_' + i_str, 'effective angle wrt horizontal wrt detector coordinate system (rad)',
                     'float', 'norm', 0., 0.002)
            x += pitch

        # second set makes up the wall
        y = -1. * (n_module - 1) / 2. * pitch + n_module * pitch / 2.
        for i_module in range(n_module):
            i_str = str(i_module + n_module)
            # positions of center of photosensor module active surfaces
            add_prop('x_' + i_str, 'x coordinate of center of module front surface (mm)',
                     'float', 'norm', 0., 2.)
            add_prop('y_' + i_str, 'y coordinate of center of module front surface (mm) ',
                     'float', 'norm', y, 2.)
            # orientation
            add_prop('angle_' + i_str, 'effective angle wrt horizontal wrt detector coordinate system (rad)',
                     'float', 'norm', np.pi / 2., 0.002)
            y += pitch

        return design_properties
