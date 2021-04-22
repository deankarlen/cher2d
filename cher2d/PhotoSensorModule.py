from cher2d.Device import Device
from cher2d.DesignProperty import DesignProperty
from cher2d.PhotoSensor import PhotoSensor
import numpy as np


class PhotoSensorModule(Device):
    """
    A PhotoSensorModule object is a group of Photosensors that make up a module

    """

    def __init__(self, module_id: int, design_properties: dict, photo_sensor_design_properties: dict,
                 exact: bool = False):
        """Constructor
        """
        super().__init__(module_id, design_properties, exact)

        # construct the module by adding photosensors
        self.photo_sensors = []
        for i_sensor in range(self.true_properties['n_sensor'].get_value()):
            self.photo_sensors.append(PhotoSensor(i_sensor, photo_sensor_design_properties, exact))

    @classmethod
    def flat_mpmt_properties(cls):
        """ Return a dictionary with the flat mPMT design properties
        """

        def add_prop(name: str, description: str, property_type: str, distribution: str, mean, sigma):
            if name in design_properties:
                raise ValueError('Default properties definition has duplicate names:', name)
            design_properties[name] = DesignProperty(name, description, property_type, distribution, mean, sigma)

        design_properties = {}

        # photosensors
        n_sensor = 5
        add_prop('n_sensor', 'number of photosensors in module', 'int', 'exact', n_sensor, 0)
        pitch = 115.
        add_prop('pitch', 'separation between centres of photosensors (mm)', 'float', 'exact', pitch, 0.)
        add_prop('width', ' width of module in the active surface plane (mm)', 'float', 'norm', n_sensor * pitch, 1.)

        x = -1. * (n_sensor - 1) / 2. * pitch
        for i_sensor in range(n_sensor):
            i_str = str(i_sensor)
            # positions of center of photosensor active surfaces
            add_prop('x_' + i_str, 'x coordinate of center of photosensor active surface wrt module center (mm)',
                     'float', 'norm', x, 1.)
            add_prop('y_' + i_str, 'y coordinate of center of photosensor active surface wrt module center (mm) ',
                     'float', 'norm', 0., 0.5)
            # orientation
            add_prop('angle_' + i_str, 'effective angle wrt vertical wrt module coordinate system (rad)',
                     'float', 'norm', 0., 0.001)
            x += pitch

        return design_properties

    @classmethod
    def dome_mpmt_properties(cls):
        """ Return a dictionary with the dome mpmt design properties
        """

        def add_prop(name: str, description: str, property_type: str, distribution: str, mean, sigma):
            if name in design_properties:
                raise ValueError('Default properties definition has duplicate names:', name)
            design_properties[name] = DesignProperty(name, description, property_type, distribution, mean, sigma)

        design_properties = {}

        # photosensors
        n_sensor = 5
        add_prop('n_sensor', 'number of photosensors in module', 'int', 'exact', n_sensor, 0)
        pitch = 115.
        add_prop('pitch', 'separation between centres of photosensors (mm)', 'float', 'exact', pitch, 0.)
        add_prop('width', 'width of module in the active surface plane (mm)', 'float', 'norm', n_sensor * pitch, 1.)

        x = -1. * (n_sensor - 1) / 2. * pitch
        rot_ang = 0.3
        r = pitch / np.sin(rot_ang)
        y0 = r * (1. - np.sin(np.pi / 2. - 2. * rot_ang))
        mid_sensor = int(n_sensor / 2 + 1)

        for i_sensor in range(n_sensor):
            i_str = str(i_sensor)

            # number of rotations (-2, -1, 0, 1, 2 for a 5 pmt module):
            n_rot = i_sensor - mid_sensor + 1
            dy = r * (1. - np.cos(n_rot * rot_ang))

            # positions of center of photosensor active surfaces
            add_prop('x_' + i_str, 'x coordinate of center of photosensor active surface wrt module center (mm)',
                     'float', 'norm', x, 1.)
            add_prop('y_' + i_str, 'y coordinate of center of photosensor active surface wrt module center (mm) ',
                     'float', 'norm', y0 - dy, 1.)
            # orientation
            add_prop('angle_' + i_str, 'effective angle wrt vertical wrt module coordinate system (rad)',
                     'float', 'norm', -n_rot * rot_ang, 0.002)
            x += pitch

        return design_properties
