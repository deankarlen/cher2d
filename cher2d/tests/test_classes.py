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
        #np.random.seed(seed=2334233)

        default_photosensor_design = PhotoSensor.default_properties()
        #default_photosensor_module_design = PhotoSensorModule.flat_mpmt_properties()
        default_photosensor_module_design = PhotoSensorModule.dome_mpmt_properties()
        default_detector_design = Detector.default_properties()
        my_detector = Detector(0,default_detector_design,default_photosensor_module_design,default_photosensor_design)

        my_vis = Visualizer(my_detector)
        my_vis.draw_detector()

        default_emitter_design = Emitter.default_properties()
        my_emitter = Emitter(0,default_emitter_design)
        t_0 = 2.
        my_emitter.emit(t_0)
        my_vis.draw_photons(my_emitter, mod_n=100)
        my_vis.draw_emitter(my_emitter)

        my_event = my_detector.get_event(my_emitter)
        my_vis.draw_event(my_event)

        if 1==1:
            my_analyzer = Analyzer(my_detector, my_emitter)

            parameters = {}
            parameters['x'] = my_emitter.design_properties['x'].mean
            parameters['y'] = my_emitter.design_properties['y'].mean
            parameters['angle'] = my_emitter.design_properties['angle'].mean
            parameters['length'] = my_emitter.design_properties['length'].mean
            parameters['t0'] = t_0

            #my_analyzer.ln_likelihood(my_event,parameters)

            m = my_analyzer.estimate_parameters(my_event, parameters)
            for p, v, e in zip(m.parameters, m.values, m.errors):
                print(f"{p} = {v:.3f} +/- {e:.3f}")

            print(m.covariance.correlation())

        i=1
        assert i == 1

if __name__ == '__main__':
    unittest.main()
