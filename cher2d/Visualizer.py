import matplotlib.pyplot as plt
import numpy as np


class Visualizer:
    """
    A Device object is a group of PhotoSensorModules

    """
    NUM_COLORS = 100

    def __init__(self, detector):
        """Constructor
        """
        self.detector = detector
        self.cm = plt.get_cmap('gist_rainbow')

    @staticmethod
    def draw_line(x, y, angle, width, **kwargs):
        vector = [width / 2. * np.cos(angle), width / 2. * np.sin(angle)]
        ends = np.array([np.add([x, y], vector), np.subtract([x, y], vector)]).T
        plt.plot(ends[0], ends[1], **kwargs)

    def draw_detector(self, xlim=(-5000, 1000), ylim=(-3000, 3000)):
        """Show the layout of the photosensor and modules
        """
        plt.figure(figsize=(8, 8))
        plt.xlim(xlim)
        plt.ylim(ylim)

        # draw each module
        n_module = self.detector.true_properties['n_module'].get_value()
        for i_module in range(n_module):
            i_str = str(i_module)
            x = self.detector.true_properties['x_' + i_str].get_value()
            y = self.detector.true_properties['y_' + i_str].get_value()
            angle = self.detector.true_properties['angle_' + i_str].get_value()
            module = self.detector.photo_sensor_modules[i_module]
            width = module.true_properties['width'].get_value()
            self.draw_line(x, y, angle, width, lw=4, alpha=0.3, zorder=1)

            n_sensor = module.true_properties['n_sensor'].get_value()
            for i_sensor in range(n_sensor):
                i_str = str(i_sensor)
                x_s = module.true_properties['x_' + i_str].get_value()
                y_s = module.true_properties['y_' + i_str].get_value()
                angle_s = module.true_properties['angle_' + i_str].get_value()
                sensor = module.photo_sensors[i_sensor]
                width_s = sensor.true_properties['width'].get_value()
                x_d, y_d, angle_d = sensor.get_global_orientation([x_s, y_s, angle_s], [x, y, angle])
                self.draw_line(x_d, y_d, angle_d, width_s, lw=1, color='black', zorder=2)

        # plt.show()

    def draw_event(self, event):
        n_module = self.detector.true_properties['n_module'].get_value()
        for i_module in range(n_module):
            i_str = str(i_module)
            x = self.detector.true_properties['x_' + i_str].get_value()
            y = self.detector.true_properties['y_' + i_str].get_value()
            angle = self.detector.true_properties['angle_' + i_str].get_value()
            module = self.detector.photo_sensor_modules[i_module]

            n_sensor = module.true_properties['n_sensor'].get_value()
            for i_sensor in range(n_sensor):
                n_photons = event.n_pe[i_module][i_sensor]
                if n_photons > 0:
                    i_str = str(i_sensor)
                    x_s = module.true_properties['x_' + i_str].get_value()
                    y_s = module.true_properties['y_' + i_str].get_value()
                    angle_s = module.true_properties['angle_' + i_str].get_value()
                    sensor = module.photo_sensors[i_sensor]
                    width_s = sensor.true_properties['width'].get_value()
                    x_d, y_d, angle_d = sensor.get_global_orientation([x_s, y_s, angle_s], [x, y, angle])
                    color = self.cm(1. * n_photons / self.NUM_COLORS)

                    self.draw_line(x_d, y_d, angle_d, width_s, lw=2, color=color, zorder=3)
        plt.show()

    def draw_photons(self, emitter):
        """Show photons produced by an emitter
        """
        max_distance = 100000
        n_module = self.detector.true_properties['n_module'].get_value()
        for photon in emitter.photons:
            x0 = photon.x
            y0 = photon.y

            # see if photon crosses a module:
            distance = max_distance
            for i_module in range(n_module):
                i_str = str(i_module)
                x_m = self.detector.true_properties['x_' + i_str].get_value()
                y_m = self.detector.true_properties['y_' + i_str].get_value()
                angle_m = self.detector.true_properties['angle_' + i_str].get_value()
                module = self.detector.photo_sensor_modules[i_module]
                width = module.true_properties['width'].get_value()

                x, y = module.find_intersection(photon, [x_m, y_m, angle_m])
                dist_m = np.sqrt((x - x_m) ** 2 + (y - y_m) ** 2)
                if dist_m < width / 2.:
                    distance = np.sqrt((x0 - x) ** 2 + (y0 - y) ** 2)
                    break

            x1 = x0 + distance * np.cos(photon.angle)
            y1 = y0 + distance * np.sin(photon.angle)
            plt.plot([x0, x1], [y0, y1], ls='--', color='grey', zorder=1)

    @staticmethod
    def draw_emitter(emitter):
        """Show photons produced by an emitter
        """
        x0 = emitter.true_properties['x'].get_value()
        y0 = emitter.true_properties['y'].get_value()
        angle = emitter.true_properties['angle'].get_value()
        length = emitter.true_properties['length'].get_value()

        x1 = x0 + length * np.cos(angle)
        y1 = y0 + length * np.sin(angle)
        plt.plot([x0, x1], [y0, y1], lw=3, color='red', zorder=4)
