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

    def get_minuit(self, event, guess):
        def fcn(x, y, angle, length, t0):
            pars = {'x': x, 'y': y, 'angle': angle, 'length': length, 't0': t0}
            neg_log = -1. * self.ln_likelihood(event, pars)
            #print(pars,neg_log)
            return neg_log

        fcn.errordef = Minuit.LIKELIHOOD

        #print(guess)
        m = Minuit(fcn, x=guess['x'], y=guess['y'], angle=guess['angle'], length=guess['length'], t0=guess['t0'])
        m.limits = [(-5000., 0.), (0., 5000.), (None, None) , (0.1, 3000.), (-100., 100.)]
        m.errors = (10., 10., 0.01, 10.,0.5)

        return m

    def ln_likelihood(self, event, parameters: dict):
        """Calculate the ln likelihood of the event, given the parameter values
        for the emitter in the parameters dictionary
        """
        ln_l = 0
        nu_dark = 1.E-9

        # calculate expectations (assuming design_property mean values)
        asimov = self.detector.get_asimov(self.emitter, parameters, False)

        # calculate ln likelihood given those expectations:

        n_module = self.detector.true_properties['n_module'].get_value()
        for i_module in range(n_module):
            module = self.detector.photo_sensor_modules[i_module]
            n_sensor = module.true_properties['n_sensor'].get_value()
            for i_sensor in range(n_sensor):
                # add nu_dark to avoid infinities...
                n_expected = asimov.n_pe[i_module][i_sensor] + nu_dark
                t_expected = asimov.sum_t[i_module][i_sensor]/n_expected

                n_pe = event.n_pe[i_module][i_sensor]
                ln_l += n_pe*np.log(n_expected) - n_expected
                if n_pe > 0:
                    mean_t = event.sum_t[i_module][i_sensor]/n_pe
                    sensor = module.photo_sensors[i_sensor]
                    t_sig = sensor.design_properties['t_sig'].mean
                    ln_l -= (mean_t - t_expected)**2/2./t_sig**2 * n_pe

        return ln_l
