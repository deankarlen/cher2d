from cher2d.Device import Device
from cher2d.PhotoSensorModule import PhotoSensorModule
from cher2d.DesignProperty import DesignProperty
import numpy as np

class Detector(Device):
    """
    A Detector object is a group of PhotoSensorModules

    """

    def __init__(self, detector_id: int, design_properties: list, photo_sensor_model_design_properties: list,
                 photo_sensor_design_properties: list):
        """Constructor
        """
        super().__init__(detector_id, design_properties)

        # construct the detector by adding modules
        self.photo_sensor_modules = []
        for i_module in range(self.true_properties['n_module'].get_value()):
            self.photo_sensor_modules.append(PhotoSensorModule(i_module, photo_sensor_model_design_properties,
                                                               photo_sensor_design_properties))

    @classmethod
    def default_properties(cls):
        """ Return a dictionary with the default PhotoSensor design properties
        """

        def add_prop(name: str, description: str, property_type: str, distribution: str, mean, sigma):
            if name in design_properties:
                raise ValueError('Default properties definition has duplicate names:', name)
            design_properties[name] = DesignProperty(name, description, property_type, distribution, mean, sigma)

        design_properties = {}

        # photosensor_modules
        n_module = 7
        add_prop('n_module', 'number of photosensor modules in detector', 'int', 'exact', n_module, 0)
        pitch = 700.
        add_prop('pitch', 'separation between centres of photosensor modules (mm)', 'float', 'exact', pitch, 0.)

        y = -1. * (n_module - 1) / 2. * pitch
        for i_module in range(n_module):
            i_str = str(i_module)
            # positions of center of photosensor module active surfaces
            add_prop('x_' + i_str, 'x coordinate of center of module front surface wrt detector center (mm)',
                     'float', 'norm', 0., 2.)
            add_prop('y_' + i_str, 'y coordinate of center of module front surface wrt detector center (mm) ',
                     'float', 'norm', y, 2.)
            # orientation
            add_prop('angle_' + i_str, 'effective angle wrt horizontal wrt detector coordinate system (rad)',
                     'float', 'norm', np.pi/2., 0.002)
            y += pitch

        return design_properties
