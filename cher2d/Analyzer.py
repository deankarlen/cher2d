from cher2d.Photon import Photon
import numpy as np
from scipy import stats
from iminuit import Minuit


class Analyzer:
    """
    An Analyzer object applies maximum likelihood to estimate emitter parameters

    """

    def __init__(self, detector, emitter):
        """Constructor
        """
        self.detector = detector
        self.emitter = emitter

    def estimate_parameters(self, event, guess):
        def fcn(x, y, angle, length, t0):
            pars = {'x': x, 'y': y, 'angle': angle, 'length': length, 't0': t0}
            neg_log = -1. * self.ln_likelihood(event, pars)
            #print(pars,neg_log)
            return neg_log

        fcn.errordef = Minuit.LIKELIHOOD

        #print(guess)
        m = Minuit(fcn, x=guess['x'], y=guess['y'], angle=guess['angle'], length=guess['length'], t0=guess['t0'])
        m.limits = [(-5000., 0.), (-3000., 3000.), (None, None) , (0.1, 3000.), (-100., 100.)]
        m.errors = (10., 10., 0.01, 10.,0.5)

        m.migrad()  # run optimiser
        #print(m.values)

        m.hesse()  # run covariance estimator
        #print(m.errors)
        return m

    def ln_likelihood(self, event, parameters: dict):
        """Calculate the ln likelihood of the event, given the parameter values
        for the emitter in the parameters dictionary
        """
        ln_l = 0

        x_e = parameters['x']
        y_e = parameters['y']
        angle_e = parameters['angle']
        length_e = parameters['length']
        t0_e = parameters['t0']

        ch_density = self.emitter.design_properties['ch_density'].mean
        velocity_e = self.emitter.design_properties['velocity'].mean

        n_module = self.detector.design_properties['n_module'].mean
        for i_module in range(n_module):
            i_str = str(i_module)
            x_m = self.detector.design_properties['x_' + i_str].mean
            y_m = self.detector.design_properties['y_' + i_str].mean
            angle_m = self.detector.design_properties['angle_' + i_str].mean
            module = self.detector.photo_sensor_modules[i_module]

            n_sensor = module.design_properties['n_sensor'].mean
            for i_sensor in range(n_sensor):
                i_str = str(i_sensor)
                x_s = module.design_properties['x_' + i_str].mean
                y_s = module.design_properties['y_' + i_str].mean
                angle_s = module.design_properties['angle_' + i_str].mean
                sensor = module.photo_sensors[i_sensor]
                width_s = sensor.design_properties['width'].mean

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
                    angle = angle_e + sign * self.emitter.design_properties['ch_angle'].mean + np.pi
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
                    n_pe = event.n_pe[i_module][i_sensor]
                    if path_length > 0.:
                        # for now - assuming constant qe across the surface - half of photons on either side
                        n_expected = (path_length * ch_density * sensor.design_properties['qe'].mean) / 2.
                        t_expected = 0.5 * (t_0 + t_1 + (dist_0 + dist_1) / velocity_e) + t0_e

                        # work out the probability density to see the photons and time given these expectations
                        # Note: not understood, but convergence is better with logpmf than calculation without factorial
                        ln_l += stats.poisson.logpmf(n_pe, n_expected)
                        #ln_l += n_pe*np.log(n_expected) - n_expected # performs less well!
                        if n_pe > 0:
                            mean_t = event.sum_t[i_module][i_sensor]/n_pe
                            t_sig = sensor.design_properties['t_sig'].mean
                            #ln_l += stats.norm.logpdf(mean_t, loc=t_expected, scale=t_sig/np.sqrt(n_pe))
                            ln_l -= (mean_t - t_expected)**2/2./t_sig**2 * n_pe

                    # very small probability to see a signal if path length is zero!
                    else:
                        if n_pe > 0:
                            ln_l += stats.poisson.logpmf(n_pe, 0.00001)
                            #ln_l -= n_pe*10.

        return ln_l
