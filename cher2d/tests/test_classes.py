import unittest
from cher2d.PhotoSensor import PhotoSensor
from cher2d.PhotoSensorModule import PhotoSensorModule
from cher2d.Detector import Detector
from cher2d.Emitter import Emitter
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

        my_event = my_emitter.get_event(my_detector)
        my_vis.draw_event(my_event)

        i=1
        assert i == 1

if __name__ == '__main__':
    unittest.main()
