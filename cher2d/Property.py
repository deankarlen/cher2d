class Property:
    """
    The base class for DesignProperty, TrueProperty, and EstimatedProperty

    """
    PROPERTY_TYPES = {'int': int, 'float': float, 'bool': bool}

    def __init__(self, name: str, description: str, property_type: str):
        """Constructor
        """
        self.name = name
        self.description = description

        if property_type not in self.PROPERTY_TYPES:
            buff = '/'.join(self.PROPERTY_TYPES)
            raise ValueError('Error in constructing Property (' + self.name +
                             '): variable_type must be one of:', buff)
        self.property_type = property_type
