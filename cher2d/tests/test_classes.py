import unittest
from cher2d.PhotoSensor import PhotoSensor
from cher2d.PhotoSensorModule import PhotoSensorModule
from cher2d.Detector import Detector
from cher2d.Emitter import Emitter
from cher2d.Analyzer import Analyzer
from cher2d.Visualizer import Visualizer
import numpy as np


class MyTestCase(unittest.TestCase):
    def test_detector(self):
        np.random.seed(seed=2334231)

        photosensor_design = PhotoSensor.default_properties()
        #photosensor_module_design = PhotoSensorModule.flat_mpmt_properties()
        photosensor_module_design = PhotoSensorModule.dome_mpmt_properties()
        detector_design = Detector.default_properties()

        # Make an EXACT detector and emitter
        exact = False
        my_detector = Detector(0, detector_design, photosensor_module_design, photosensor_design, exact=exact)

        my_vis = Visualizer(my_detector)
        my_vis.draw_detector()

        emitter_design = Emitter.default_properties()
        emitter_design['x'].mean = -3000.
        emitter_design['y'].mean = 2900.
        emitter_design['length'].mean = 1500.
        # change the brightness below (at 3, draw every 100 photons)
        mod_n = 10
        emitter_design['ch_density'].mean = 0.03 * mod_n
        my_emitter = Emitter(0, emitter_design, exact=exact)
        t_0 = 2.

        my_emitter.set_offset('x',15.)

        mpmt = my_detector.photo_sensor_modules[0]
        pmt = mpmt.photo_sensors[0]
        for device in [my_detector, mpmt, pmt, my_emitter]:
            print('')
            print(device.__class__.__name__,device.device_id,'properties')
            print('+++++++++++++++++++++++++++++++++++')
            print(device.get_table())

        event_type = 'asimov'

        if event_type == 'normal':
            my_emitter.emit(t_0)
            my_vis.draw_photons(my_emitter, mod_n=mod_n)
            my_event = my_detector.get_event(my_emitter)
        else:
            # Asimov event
            true_parameters = {}
            for par_name in ['x', 'y', 'angle', 'length']:
                true_parameters[par_name] = my_emitter.get_value(par_name, True)
            true_parameters['t0'] = t_0
            my_event = my_detector.get_asimov(my_emitter, true_parameters, True)

        my_vis.draw_emitter(my_emitter)
        my_vis.draw_event(my_event)
        my_vis.show()

        if 1 == 2:
            my_analyzer = Analyzer(my_detector, my_emitter)

            parameters = {}
            parameters['x'] = my_emitter.design_properties['x'].mean
            parameters['y'] = my_emitter.design_properties['y'].mean
            parameters['angle'] = my_emitter.design_properties['angle'].mean
            parameters['length'] = my_emitter.design_properties['length'].mean
            parameters['t0'] = t_0

            # my_analyzer.ln_likelihood(my_event,parameters)

            m = my_analyzer.get_minuit(my_event, parameters)

            print(m.migrad())  # run optimiser
            # print(m.values)

            print(m.hesse())  # run covariance estimator
            # print(m.errors)

            truth = []
            truth.append(my_emitter.true_properties['x'].get_value())
            truth.append(my_emitter.true_properties['y'].get_value())
            truth.append(my_emitter.true_properties['angle'].get_value())
            truth.append(my_emitter.true_properties['length'].get_value())
            truth.append(t_0)

            print('Minimum valid:', m.valid, '  Covariance is accurate:', m.accurate)

            for p, v, e, t in zip(m.parameters, m.values, m.errors, truth):
                print(f"{p} = {v:.3f} +/- {e:.3f} | {t:.3f}")

            print(m.covariance.correlation())

        i = 1
        assert i == 1


if __name__ == '__main__':
    unittest.main()
