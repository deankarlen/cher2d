from cher2d.DesignProperty import DesignProperty
from cher2d.Device import Device


class PhotoSensor(Device):
    """
    A PhotoSensor object can detect a Photon object thus producing a Signal object

    """

    def __init__(self, sensor_id: int, design_properties: list):
        """Constructor
        """
        super().__init__(sensor_id, design_properties)



    @classmethod
    def default_properties(cls) -> dict:
        """ Return a dictionary with the default PhotoSensor design properties
        :rtype: dict
        """

        def add_prop(name: str, description: str, property_type: str, distribution: str, mean, sigma):
            if name in design_properties:
                raise ValueError('Default properties definition has duplicate names:', name)
            design_properties[name] = DesignProperty(name, description, property_type, distribution, mean, sigma)

        design_properties = {}

        # size
        add_prop('width',' width of photosensor active surface (mm)', 'float', 'norm', 75.0, 0.1)

        return design_properties
