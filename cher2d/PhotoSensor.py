from cher2d.DesignProperty import DesignProperty
from cher2d.Device import Device


class PhotoSensor(Device):
    """
    A PhotoSensor object can detect a Photon object thus producing a Signal object

    """

    def __init__(self, sensor_id: int, design_properties: dict, exact: bool = False):
        """Constructor
        """
        super().__init__(sensor_id, design_properties, exact)

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
        add_prop('width', 'width of photosensor active surface (mm)', 'float', 'norm', 75.0, 0.1)

        # detector performance

        # timing
        add_prop('t_sig', 'timing resolution (ns)', 'float', 'norm', 1.5, 0.05)
        # time delay
        add_prop('td', 'mean time delay (ns)', 'float', 'norm', 1.0, 0.05)
        add_prop('td_radial', 'delay radial dependence included', 'bool', 'exact', False, 0.)
        add_prop('td_radial_coeff', 'delay radial coefficienct', 'float', 'norm', 0.5, 0.01)

        # quantum efficiency
        add_prop('qe', 'quantum efficiency', 'float', 'beta', 0.8, 0.01)
        # quantum efficiency depends on angle
        add_prop('qe_angle', 'qe angle dependence included', 'bool', 'exact', False, 0.)
        add_prop('qe_angle_coeff', 'qe angle coefficient', 'float', 'norm', 0.5, 0.01)
        # quantum efficiency depends on distance from pmt centre
        add_prop('qe_radial', 'qe radial dependence included', 'bool', 'exact', False, 0.)
        add_prop('qe_radial_coeff', 'qe radial coefficient', 'float', 'norm', 0.5, 0.01)

        # dark noise - note that detector defines the time window for events - turn off for now (not in likelihood)
        add_prop('dark_noise_rate', 'rate of random single pe pulses (Hz)', 'float', 'exact', 0., 0.)

        return design_properties
