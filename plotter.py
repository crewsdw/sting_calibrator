import matplotlib.pyplot as plt
import numpy as np
from inputimeout import inputimeout, TimeoutOccurred


class Plotter:
    def __init__(self):
        self.data, self.samples = None, None
        self.fig, self.ax = None, None
        # self.fig_bridge, self.ax_bridge = None, None

    def set_data(self, data):
        self.data = data
        self.samples = np.array(range(data.shape[2]))

    def plot_channel_data(self):
        plt.figure()
        for i in range(6):
            plt.plot(self.samples, self.data[0, i, :], 'o')
        plt.ylabel('load voltages')
        plt.grid(True)
        plt.tight_layout()

    def initialize_subplots(self):
        plt.ion()
        self.fig, self.ax = plt.subplots(1, 2, figsize=(15, 6))
        self.ax[0].set_xlabel('Samples'), self.ax[1].set_xlabel('Samples')
        self.ax[0].set_ylabel('Load [lbs]'), self.ax[1].set_ylabel('Bridge Voltage [V]')
        self.ax[0].grid(True), self.ax[1].grid(True)
        # plt.tight_layout()
        plt.show()

    def update_channel(self, daq_channels, idx):
        # Read load cells
        data_loads = daq_channels.read_loads()[0, :, :]
        # Read bridge
        data_bridge = daq_channels.read_bridge()[0, :, :]

        # average samples
        # avg_loads = np.mean(data_loads, axis=1)
        # avg_bridge = np.mean(data_bridge, axis=1)
        samples = np.arange(idx * data_loads.shape[1], (idx + 1) * data_loads.shape[1])

        colors = ['r', 'g', 'b', 'k', 'c', 'm']
        for i in range(1):  # data_loads.shape[0]):
            self.ax[0].plot(samples, data_loads[i, :], 'o' + colors[i] + '--')
            self.ax[1].plot(samples, data_bridge[i, :], 'o' + colors[i] + '--')
        plt.draw()
        plt.pause(0.1)

    def continuous_plotting(self, daq_channels):
        # Configure channels
        daq_channels.configure_loads(), daq_channels.configure_bridge()
        # Initial read and plot
        self.initialize_subplots()
        self.update_channel(daq_channels=daq_channels, idx=0)
        # plt.show(block=False)
        plt.pause(1)
        # Visualization loop
        idx = 0
        valid_input = None
        print('\nConfigure experiment, then press any key to read data.')
        while not valid_input:
            try:
                inputimeout(prompt='',
                            timeout=0.5)
                valid_input = 1
            except TimeoutOccurred:
                # print('updating plots')
                idx += 1
                self.update_channel(daq_channels=daq_channels, idx=idx)
                continue
        plt.close(self.fig)
        daq_channels.close_loads(), daq_channels.close_bridge()
        return

    def show_all(self):
        plt.show()
