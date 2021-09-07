import matplotlib.pyplot as plt
import numpy as np


class Plotter:
    def __init__(self, data):
        self.data = data
        self.samples = np.array(range(data.shape[2]))

    def plot_channel_data(self):
        plt.figure()
        for i in range(6):
            plt.plot(self.samples, self.data[0, i, :], 'o')
        plt.ylabel('load voltages')
        plt.grid(True)
        plt.tight_layout()

        # plt.figure()
        # for i in range(6):
        #     plt.plot(self.samples, self.data[1, i, :], 'o')
        # plt.ylabel('load voltages')
        # plt.grid(True)
        # plt.tight_layout()

    def show_all(self):
        plt.show()