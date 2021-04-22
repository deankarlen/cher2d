class Event:
    """
    An event is a collection of signals for the photosensors

    """

    def __init__(self, detector):
        """Constructor
        """

        self.detector = detector
        self.n_module = self.detector.design_properties['n_module'].mean

        self.n_pe = []
        self.sum_t = []

        for i_module in range(self.n_module):
            self.n_pe.append([])
            self.sum_t.append([])
            module = self.detector.photo_sensor_modules[i_module]

            n_sensor = module.design_properties['n_sensor'].mean
            for i_sensor in range(n_sensor):
                self.n_pe[i_module].append(0)
                self.sum_t[i_module].append(0.)

    def add_pe(self, i_module: int, i_sensor: int, t: float, n_pe=1):
        self.n_pe[i_module][i_sensor] += n_pe
        self.sum_t[i_module][i_sensor] += t*n_pe
