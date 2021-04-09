from cher2d.Detector import Detector
import matplotlib.pyplot as plt
import numpy as np

class Visualizer():
    """
    A Device object is a group of PhotoSensorModules

    """

    def __init__(self, detector: Detector):
        """Constructor
        """
        self.detector = detector

    def draw_line(self, x, y, angle, width, **kwargs):
        vector = [width/2.*np.cos(angle),width/2.*np.sin(angle)]
        ends = np.array([np.add([x,y],vector),np.subtract([x,y],vector)]).T
        plt.plot(ends[0],ends[1], **kwargs)

    def draw_detector(self,xlim=(-5000,1000),ylim=(-3000,3000)):
        """Show the layout of the photosensor and modules
        """
        plt.figure(figsize=(8, 8))
        plt.xlim(xlim)
        plt.ylim(ylim)

        # draw each module
        n_module = self.detector.true_properties['n_module'].get_value()
        for i_module in range(n_module):
            istr = str(i_module)
            x = self.detector.true_properties['x_'+istr].get_value()
            y = self.detector.true_properties['y_' + istr].get_value()
            angle = self.detector.true_properties['angle_' + istr].get_value()
            module = self.detector.photo_sensor_modules[i_module]
            width = module.true_properties['width'].get_value()
            self.draw_line(x, y, angle, width, lw=4, alpha=0.3, zorder=1)

            n_sensor = module.true_properties['n_sensor'].get_value()
            for i_sensor in range(n_sensor):
                istr = str(i_sensor)
                x_s = module.true_properties['x_' + istr].get_value()
                y_s = module.true_properties['y_' + istr].get_value()
                angle_s = module.true_properties['angle_' + istr].get_value()
                sensor = module.photo_sensors[i_sensor]
                width_s = sensor.true_properties['width'].get_value()
                x_d, y_d, angle_d = sensor.get_global_orientation([x_s,y_s,angle_s],[x,y,angle])
                self.draw_line(x_d, y_d, angle_d, width_s, lw=1, color='black', zorder=2)

        plt.show()