import unittest
from cher2d.PhotoSensor import PhotoSensor
from cher2d.PhotoSensorModule import PhotoSensorModule
from cher2d.Detector import Detector
from cher2d.Emitter import Emitter
from cher2d.Analyzer import Analyzer
from cher2d.Visualizer import Visualizer


class MyTestCase(unittest.TestCase):
    def test_detector(self):
        default_photosensor_design = PhotoSensor.default_properties()
        default_photosensor_module_design = PhotoSensorModule.default_properties()
        default_detector_design = Detector.default_properties()
        my_detector = Detector(0,default_detector_design,default_photosensor_module_design,default_photosensor_design)

        my_vis = Visualizer(my_detector)
        my_vis.draw_detector()

        default_emitter_design = Emitter.default_properties()
        my_emitter = Emitter(0,default_emitter_design)
        t_0 = 2.
        my_emitter.emit(t_0)
        my_vis.draw_photons(my_emitter)
        my_vis.draw_emitter(my_emitter)

        my_event = my_detector.get_event(my_emitter)
        my_vis.draw_event(my_event)

        my_analyzer = Analyzer(my_detector, my_emitter)

        parameters = {}
        parameters['x'] = my_emitter.true_properties['x'].get_value()
        parameters['y'] = my_emitter.true_properties['y'].get_value()
        parameters['angle'] = my_emitter.true_properties['angle'].get_value()
        parameters['length'] = my_emitter.true_properties['length'].get_value()
        parameters['t0'] = t_0

        my_analyzer.ln_likelihood(my_event,parameters)

        i=1
        assert i == 1

if __name__ == '__main__':
    unittest.main()
