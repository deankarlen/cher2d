import numpy as np


class Device:
    """
    Base class for physical devices (PhotoSensor, PhotoSensorModule, etc)

    """

    def __init__(self, device_id: int, design_properties: dict):
        """Constructor
        """
        self.device_id = device_id
        self.design_properties = design_properties
        self.true_properties = {}
        self.estimated_properties = {}

        # build a device by setting true values for its properties
        for design_property_name in self.design_properties:
            design_property = self.design_properties[design_property_name]
            true_property = design_property.get_TrueProperty()
            self.true_properties[design_property.name] = true_property

    @staticmethod
    def get_global_orientation(local_orientation: list, coordinate_system_orientation: list):
        """ Transform orientation from local coordinate system to a global coordinate system
         orientation is defined by a list of [x,y,theta]
        """
        x_l, y_l, t_l = local_orientation
        x_c, y_c, t_c = coordinate_system_orientation
        x = x_c + x_l * np.cos(t_c) - y_l * np.sin(t_c)
        y = y_c + x_l * np.sin(t_c) + y_l * np.cos(t_c)
        t = t_c + t_l
        return [x, y, t]

    @staticmethod
    def find_intersection(photon, device_orientation: list):
        x_c, y_c, t_c = device_orientation
        m_c = np.tan(t_c)
        x_p, y_p, t_p = [photon.x, photon.y, photon.angle]
        m_p = np.tan(t_p)
        x = (y_p - y_c - m_p * x_p + m_c * x_c) / (m_c - m_p)
        y = y_c + m_c * (x - x_c)
        return [x, y]
