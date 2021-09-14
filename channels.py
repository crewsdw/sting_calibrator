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
        if mode == 'read_and_log':
            self.mode = ni.constants.LoggingMode.LOG_AND_READ
        if mode == 'read':
            self.mode = ni.constants.LoggingMode.OFF

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
        # self.determine_channel_names()
        device1 = 'cDAQ1Mod7'
        device2 = 'cDAQ1Mod8'
        ais1, ais2 = ['ai1', 'ai0', 'ai3', 'ai2'], ['ai0', 'ai1']
        self.load_channels = [device1 + '/' + ai for ai in ais1] + [device2 + '/' + ai for ai in ais2]
        self.load_names = ['Neg N Load', 'Pos S Load',
                           'Pos N', 'Neg S',
                           'Roll Moment', 'AF Load']
        # Load scales (same order)
        self.load_scale_names = ['neg_n_scale', 'pos_s_scale', 'pos_n_scale',
                                 'neg_s_scale', 'rm_scale', 'af_scale']
        self.load_scales = np.array([
            [[-1.9631, -300], [-0.9799, -150], [-0.005, 0],
             [0.9803, 150], [1.9631, 300]],
            [[-1.8417, -300], [-0.92, -150], [-0.0036, 0],
             [0.9196, 150], [1.8417, 300]],
            [[-1.898, -300], [-0.9483, -150], [-0.0033, 0],
             [0.9483, 150], [1.8985, 300]],
            [[-1.819, -300], [-0.914, -150], [0.0071, 0],
             [0.9139, 150], [1.8189, 300]],
            [[-2.0586, -100], [-1.0266, -50], [-0.0054, 0],
             [1.0266, 50], [2.0586, 100]],
            [[-2.0931, -100], [-1.0395, -50], [-0.0105, 0],
             [1.0395, 50], [2.0931, 100]]
        ])
        # self.load_scales = np.array([
        #     [[-1.9631, -300], [-0.9799, -150], [-0.005, 0],
        #      [-0.0049, 0], [0.09799, 150], [0.9803, 150], [1.9631, 300]],
        #     [[-1.8417, -300], [-0.92, -150], [-0.0036, 0],
        #      [-0.0034, 0], [0.9196, 150], [1.9202, 150], [1.8417, 300]],
        #     [[-1.898, -300], [-0.9483, -150], [-0.0033, 0],
        #      [-0.0033, 0], [0.9483, 150], [0.9491, 150], [1.8985, 300]],
        #     [[-1.819, -300], [-0.914, -150], [0.0071, 0], [0.0072, 0],
        #      [0.9139, 150], [0.9145, 150], [1.8189, 300]],
        #     [[-2.0586, -100], [-1.0266, -50], [-0.0054, 0], [-0.0051, 0],
        #      [1.0266, 50], [1.0272, 50], [2.0586, 100]],
        #     [[-2.0931, -100], [-1.0395, -50], [-0.0105, 0], [-0.0103, 0],
        #      [1.0395, 50], [1.0396, 50], [2.0931, 100]]
        # ])
        self.set_load_scales()

        # bridge channels and info
        self.bridge_channels = ["PXI1Slot2/ai0", "PXI1Slot2/ai1", "PXI1Slot2/ai2",
                                "PXI1Slot2/ai3", "PXI1Slot2/ai4", "PXI1Slot2/ai5"]
        self.bridge_names = ['N1 Bridge', 'N2 Bridge',
                             'S1 Bridge', 'S2 Bridge',
                             'L1 Bridge', 'L2 Bridge']

    def determine_channel_names(self):
        sim = ni.system.System.local()
        # devices = [device for device in sim.devices]
        for device in sim.devices:
            print(device.name)
            print(device.ai_physical_chans.channel_names)
        # Seems to detect physical channels too...
        quit()

    def configure_loads(self):
        """
        Configures ni.Task for load cell measurements
        """
        self.loads = ni.Task(new_task_name=self.group_name + '_loads')
        for idx, channel in enumerate(self.load_channels):
            self.loads.ai_channels.add_ai_bridge_chan(
                channel, name_to_assign_to_channel=self.load_names[idx],
                units=ni.constants.VoltageUnits.FROM_CUSTOM_SCALE,
                custom_scale_name=self.load_scale_names[idx]
            )

        # sampling and logging config
        self.loads.timing.cfg_samp_clk_timing(self.sampling_rate,
                                              samps_per_chan=1000)
        self.loads.in_stream.configure_logging(self.filename + '.tdms',
                                               self.mode)

    def set_load_scales(self):
        mv_v = ni.constants.UnitsPreScaled.VOLTS_PER_VOLT  # M_VOLTS_PER_VOLT
        # print(mv_v.value)
        # quit()
        lbs = 'lbs'  # ni.constants.UnitsPreScaled.POUNDS
        for i in range(6):
            # print(self.load_scales[i, :, 0])
            # print(self.load_scales[i, :, 1])
            # quit(
            # self.load_scales[i, :, 0] = [-1, -0.5, -0.005, 0.5, 1]
            # self.load_scales[i, :, 1] = 10.0 * np.array([-1, -0.5, 0, 0.5, 1])
            scale = ni.scale.Scale(name=self.load_scale_names[i])
            scale.create_table_scale(scale_name=self.load_scale_names[i],
                                     prescaled_vals=np.ascontiguousarray(self.load_scales[i, :, 0] / 1000.0),
                                     scaled_vals=np.ascontiguousarray(self.load_scales[i, :, 1]),
                                     pre_scaled_units=mv_v,
                                     scaled_units=lbs)  # ni.constants.UnitsPreScaled.POUNDS)

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
