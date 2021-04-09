from cher2d.Property import Property


class TrueProperty(Property):
    """
    A TrueProperty object holds the description and the true numerical value for the property

    """

    def __init__(self, name: str, description: str, property_type: str, value):
        """Constructor
        """
        super().__init__(name, description, property_type)

        self.__value = None
        self.set_value(value)

    def get_value(self):
        """
        Return the true value of the property

        """
        return self.__value

    def set_value(self, new_value):
        """
        Change the true value of the property

        """
        value_type = type(new_value).__name__
        # avoid issues with float64 vs float
        if value_type[:len(self.property_type)] != self.property_type:
            raise TypeError('Property (' + self.name +
                            ') value type (' + type(new_value).__name__ +
                            ') does not match property_type (' +
                            self.property_type + ')')
        self.__value = new_value
