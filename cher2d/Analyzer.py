#from cher2d.Detector import Detector
from cher2d.Event import Event
from cher2d.Emitter import Emitter
from cher2d.Photon import Photon
import numpy as np
from scipy import stats


class Analyzer:
    """
    An Analyzer object applies maximum likelihood to estimate emitter parameters

    """

    def __init__(self, detector, emitter: Emitter):
        """Constructor
        """
        self.detector = detector
        self.emitter = emitter

    def ln_likelihood(self, event: Event, parameters: dict):
        """Calculate the ln likelihood of the event, given the parameter values
        for the emitter in the parameters dictionary
        """
        sum = 0

        x_e = parameters['x']
        y_e = parameters['y']
        angle_e = parameters['angle']
        length_e = parameters['length']
        t0_e = parameters['t0']

        ch_density = self.emitter.design_properties['ch_density'].mean
        velocity_e = self.emitter.design_properties['velocity'].mean

        n_module = self.detector.true_properties['n_module'].get_value()
        for i_module in range(n_module):
            istr = str(i_module)
            x = self.detector.true_properties['x_' + istr].get_value()
            y = self.detector.true_properties['y_' + istr].get_value()
            angle = self.detector.true_properties['angle_' + istr].get_value()
            module = self.detector.photo_sensor_modules[i_module]

            n_sensor = module.true_properties['n_sensor'].get_value()
            for i_sensor in range(n_sensor):
                istr = str(i_sensor)
                x_s = module.true_properties['x_' + istr].get_value()
                y_s = module.true_properties['y_' + istr].get_value()
                angle_s = module.true_properties['angle_' + istr].get_value()
                sensor = module.photo_sensors[i_sensor]
                width_s = sensor.true_properties['width'].get_value()

                # The expected number of pe is calculated by finding the start and end point of the emitter path
                # that produces photons that hit the sensor

                x_s_0 = x_s - width_s/2. * np.cos(angle_s)
                y_s_0 = y_s - width_s / 2. * np.sin(angle_s)
                x_d_0, y_d_0, angle_d = sensor.get_global_orientation([x_s_0, y_s_0, angle_s], [x, y, angle])

                x_s_1 = x_s + width_s/2. * np.cos(angle_s)
                y_s_1 = y_s + width_s / 2. * np.sin(angle_s)
                x_d_1, y_d_1, angle_d = sensor.get_global_orientation([x_s_1, y_s_1, angle_s], [x, y, angle])

                for sign in [-1.,1.]:
                    # make a virtual photon that starts at one edge of sensor, and points back towards emitter
                    angle = angle_e + sign * self.emitter.design_properties['ch_angle'].mean + np.pi
                    photon_0 = Photon(0., x_d_0, y_d_0, angle)
                    x, y = module.find_intersection(photon_0, [x_e, y_e, angle_e])
                    t_0 = np.abs((x-x_d_0)**2 + (y-y_d_0)**2)/photon_0.VELOCITY
                    dist_0 = (x-x_e)*np.cos(angle_e) + (y-y_e)*np.sin(angle_e)
                    dist_0 = min(length_e,max(0.,dist_0))

                    photon_1 = Photon(0., x_d_1, y_d_1, angle)
                    x, y = module.find_intersection(photon_1, [x_e, y_e, angle_e])
                    dist_1 = (x-x_e)*np.cos(angle_e) + (y-y_e)*np.sin(angle_e)
                    dist_1 = min(length_e, max(0., dist_1))
                    t_1 = np.abs((x-x_d_1)**2 + (y-y_d_1)**2)/photon_1.VELOCITY

                    # path length contributing photons
                    path_length = np.abs(dist_1 - dist_0)
                    if path_length > 0.:
                        # for now - assuming constant qe across the surface - half of photons on either side
                        n_expected = (path_length * ch_density * sensor.design_properties['qe'].mean)/2.
                        t_expected = 0.25*(t_0 + t_1 + (dist_0 + dist_1)/velocity_e) + t0_e

                        # work out the probability density to see the photons and time given these expectations
                        n_pe = 0
                        data = []
                        if i_sensor in event.module_data[i_module]:
                            data = event.module_data[i_module][i_sensor]
                            n_pe = len(data)
                        sum += np.log(stats.poisson.pmf(n_pe,n_expected))
                        t_sig = sensor.design_properties['t_sig'].mean
                        for t in data:
                            sum += np.log(stats.norm.pdf(t,t_expected,t_sig))

        return sum




