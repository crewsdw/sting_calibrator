import nidaqmx as ni
import numpy as np
import time


class ChannelLogger:
    def __init__(self, filename='test', mode='log', group_name='00'):
        # Determine logging mode
        if mode != 'log' and mode != 'read':
            print('\nError: mode must be "log" or "read". Exiting.')
            quit()
        if mode == 'log':
            self.mode = ni.constants.LoggingMode.LOG
        if mode == 'read':
            self.mode = ni.constants.LoggingMode.LOG_AND_READ

        # tdms log file info
        self.filename = 'data\\' + filename

        # hardware info
        self.sampling_rate = 2.5e3  # kS/s, devices: [pxie, 9237]
        self.samples = ni.constants.READ_ALL_AVAILABLE

        # Configure channels
        self.group_name = group_name
        self.loads, self.bridge = None, None

        # names and other info
        # load cell channels: order N-, S+, N+, S-, RM, AF
        self.load_channels = ["cDAQ1Mod7/ai1", "cDAQ1Mod7/ai0", "cDAQ1Mod7/ai3",
                                     "cDAQ1Mod7/ai2", "cDAQ1Mod8/ai0", "cDAQ1Mod8/ai1"]
        self.load_names = ['Neg N Load', 'Pos S Load',
                           'Pos N', 'Neg S',
                           'Roll Moment', 'AF Load']
        # bridge channels and info
        self.bridge_channels = ["PXI1Slot2/ai0", "PXI1Slot2/ai1", "PXI1Slot2/ai2",
                                "PXI1Slot2/ai3", "PXI1Slot2/ai4", "PXI1Slot2/ai5"]
        self.bridge_names = ['N1 Bridge', 'N2 Bridge',
                             'S1 Bridge', 'S2 Bridge',
                             'L1 Bridge', 'L2 Bridge']

    def configure_loads(self):
        """
        Configures ni.Task for load cell measurements
        """
        self.loads = ni.Task(new_task_name=self.group_name + '_loads')
        for idx, channel in enumerate(self.load_channels):
            self.loads.ai_channels.add_ai_bridge_chan(channel, name_to_assign_to_channel=self.load_names[idx])

        # sampling and logging config
        self.loads.timing.cfg_samp_clk_timing(self.sampling_rate,
                                              samps_per_chan=1000)
        self.loads.in_stream.configure_logging(self.filename + '.tdms',
                                               self.mode)

    def configure_bridge(self):
        """
        Configures ni.Task for bridge voltage readings
        """
        self.bridge = ni.Task(new_task_name=self.group_name + '_bridge')
        for idx, channel in enumerate(self.bridge_channels):
            self.bridge.ai_channels.add_ai_bridge_chan(channel, name_to_assign_to_channel=self.bridge_names[idx])

        # sampling and logging config
        self.loads.timing.cfg_samp_clk_timing(self.sampling_rate,
                                              samps_per_chan=1000)
        self.loads.in_stream.configure_logging(self.filename + '.tdms',
                                               self.mode)

    def close_loads(self):
        self.loads.close()

    def close_bridge(self):
        self.bridge.close()

    def read_loads(self):
        if self.mode == ni.constants.LoggingMode.LOG:
            print('\nError: reading channels not possible in Logging Mode. Exiting...')
            self.close_all()
            quit()
        return np.array([self.loads.read(self.samples)])

    def read_bridge(self):
        if self.mode == ni.constants.LoggingMode.LOG:
            print('\nError: reading channels not possible in Logging Mode. Exiting...')
            self.close_all()
            quit()
        return np.array([self.bridge.read(self.samples)])

    def log_data(self):
        self.loads.start(), self.bridge.start()
        while not self.loads.is_task_done() and self.bridge.is_task_done():
            time.sleep(0.5)

    def close_all(self):
        """
        closes all initialized channels
        """
        self.loads.close(), self.bridge.close()
