from cher2d.Device import Device
from cher2d.PhotoSensorModule import PhotoSensorModule
from cher2d.DesignProperty import DesignProperty
from cher2d.Event import Event
from cher2d.Emitter import Emitter
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

    def get_event(self, emitter: Emitter) -> Event:
        """Produce an event from the emitter photons
        """
        event = Event(self)

        n_module = self.true_properties['n_module'].get_value()
        for photon in emitter.photons:
            x0 = photon.x
            y0 = photon.y

            # see if photon crosses a module:
            for i_module in range(n_module):
                istr = str(i_module)
                x_m = self.true_properties['x_' + istr].get_value()
                y_m = self.true_properties['y_' + istr].get_value()
                angle_m = self.true_properties['angle_' + istr].get_value()
                module = self.photo_sensor_modules[i_module]
                width = module.true_properties['width'].get_value()

                x, y = module.find_intersection(photon, [x_m, y_m, angle_m])
                dist_m = np.sqrt((x - x_m) ** 2 + (y - y_m) ** 2)
                if dist_m < width / 2.:
                    # see if photon crosses a sensor
                    n_sensor = module.true_properties['n_sensor'].get_value()
                    for i_sensor in range(n_sensor):
                        istr = str(i_sensor)
                        x_s = module.true_properties['x_' + istr].get_value()
                        y_s = module.true_properties['y_' + istr].get_value()
                        angle_s = module.true_properties['angle_' + istr].get_value()
                        sensor = module.photo_sensors[i_sensor]
                        width_s = sensor.true_properties['width'].get_value()

                        x_d, y_d, angle_d = sensor.get_global_orientation([x_s, y_s, angle_s], [x_m, y_m, angle_m])
                        x, y = sensor.find_intersection(photon, [x_d, y_d, angle_d])
                        dist_s = np.sqrt((x - x_d) ** 2 + (y - y_d) ** 2)
                        if dist_s < width_s/2.:
                            # photon hit photocathode - was a photo-electron produced?
                            qe = sensor.true_properties['qe'].get_value()
                            if qe > photon.random_numbers_uniform[0]:
                                distance = np.sqrt((x0-x)**2 + (y0-y)**2)
                                t = photon.t + distance/photon.VELOCITY
                                # incorporate timing resolution
                                t_obs = t + sensor.true_properties['t_sig'].get_value() * photon.random_numbers_norm[0]
                                event.add_pe(i_module, i_sensor,t)
                            break
                    break
        return event


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
