import numpy as np
from texttable import Texttable


class Device:
    """
    Base class for physical devices (PhotoSensor, PhotoSensorModule, etc)
    - exact: False, draw true value from distribution, True: use distribution mean
    """

    def __init__(self, device_id: int, design_properties: dict, exact: bool = False):
        """Constructor
        """
        self.device_id = device_id
        self.design_properties = design_properties
        self.true_properties = {}
        self.estimated_properties = {}
        self.exact = exact

        # build a device by setting true values for its properties
        for design_property_name in self.design_properties:
            design_property = self.design_properties[design_property_name]
            true_property = design_property.get_TrueProperty(exact)
            self.true_properties[design_property.name] = true_property

    def get_value(self, property_name: str, truth: bool):
        value = self.design_properties[property_name].mean
        if truth:
            value = self.true_properties[property_name].get_value()
        return value

    def set_offset(self, property_name: str, offset):
        # for sensitivity studies: offset original value
        value = self.true_properties[property_name].get_value()
        diff = offset - self.design_properties[property_name].get_offset()
        self.true_properties[property_name].set_value(value + diff)
        self.design_properties[property_name].set_offset(offset)

    def get_table(self, width: int = 120):
        table = Texttable()
        table.set_deco(Texttable.HEADER | Texttable.HLINES)
        table.set_max_width(width)

        header = ['Property', 'Description', 'Type', 'Dist.', 'Mean', 'Sigma', 'Offset', 'Truth']
        table.set_cols_dtype(['t', 't', 't', 't', 'a', 'a', 'a', 'a'])
        table.set_header_align(['l', 'l', 'l', 'l', 'l', 'l', 'l', 'l'])

        rows = [header]
        for name in self.design_properties:
            design_property = self.design_properties[name]
            row = [design_property.name, design_property.description, design_property.property_type,
                   design_property.distribution, design_property.mean, design_property.sigma,
                   design_property.get_offset(), self.true_properties[design_property.name].get_value()]
            rows.append(row)

        table.add_rows(rows)
        return table.draw()

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
