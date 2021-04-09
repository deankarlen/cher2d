from cher2d.Device import Device
from cher2d.DesignProperty import DesignProperty
from cher2d.PhotoSensor import PhotoSensor

class PhotoSensorModule(Device):
    """
    A PhotoSensorModule object is a group of Photosensors that make up a module

    """

    def __init__(self, module_id: int, design_properties: list, photo_sensor_design_properties:list):
        """Constructor
        """
        super().__init__(module_id, design_properties)

        # construct the module by adding photosensors
        self.photo_sensors = []
        for i_sensor in range(self.true_properties['n_sensor'].get_value()):
            self.photo_sensors.append(PhotoSensor(i_sensor, photo_sensor_design_properties))

    @classmethod
    def default_properties(cls):
        """ Return a dictionary with the default PhotoSensor design properties
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
        add_prop('width',' width of module in the active surface plane (mm)', 'float', 'norm', n_sensor*pitch, 1.)

        x = -1. * (n_sensor-1)/2. * pitch
        for i_sensor in range(n_sensor):
            i_str = str(i_sensor)
            # positions of center of photosensor active surfaces
            add_prop('x_'+i_str, 'x coordinate of center of photosensor active surface wrt module center (mm)',
                     'float', 'norm', x, 0.5)
            add_prop('y_'+i_str, 'y coordinate of center of photosensor active surface wrt module center (mm) ',
                     'float', 'norm', 0., 0.5)
            # orientation
            add_prop('angle_'+i_str, 'effective angle wrt vertical wrt module coordinate system (rad)',
                     'float', 'norm', 0., 0.001)
            x += pitch

        return design_properties
