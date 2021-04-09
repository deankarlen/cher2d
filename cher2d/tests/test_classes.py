import unittest
from cher2d.PhotoSensor import PhotoSensor
from cher2d.PhotoSensorModule import PhotoSensorModule
from cher2d.Detector import Detector
from cher2d.Visualizer import Visualizer


class MyTestCase(unittest.TestCase):
    def test_detector(self):
        default_photosensor_design = PhotoSensor.default_properties()
        default_photosensor_module_design = PhotoSensorModule.default_properties()
        default_detector_design = Detector.default_properties()
        my_detector = Detector(0,default_detector_design,default_photosensor_module_design,default_photosensor_design)

        my_vis = Visualizer(my_detector)
        my_vis.draw_detector()

        i=1
        assert i == 1

if __name__ == '__main__':
    unittest.main()
