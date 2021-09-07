import channels as ch
import plotter as my_plt
import read_tdms as my_tdms

# Unused libraries
# import nidaqmx as ni
# import numpy as np
# import matplotlib.pyplot as plt

# Parameters and flags
mode = 'read'

# Desired groups
load_groups = ['+NF', '-NF', '+SF', '-SF', '+AF', '-AF']
load_values = ['00', '10', '20', '30', '220', '210', '200']

# Set up channels
for group in load_groups:
    for load in load_values:
        print('\n\nCurrent group: ' + group + ' and load ' + load)
        print('Configure experiment, then press enter to read data.')
        input()
        print('Reading data... wait until next prompt to proceed.')
        # Set up channel logger
        daq_channels = ch.ChannelLogger(filename=group, mode=mode, group_name=load)
        if mode == 'read':
            # Read load cells
            daq_channels.configure_loads()
            data = daq_channels.read_loads()
            daq_channels.close_loads()
            # Read bridge
            daq_channels.configure_bridge()
            data2 = daq_channels.read_bridge()
            daq_channels.close_bridge()

            # plotter = my_plt.Plotter(data=data)
            # plotter.plot_channel_data()
            # plotter.show_all()

        if mode == 'log':
            daq_channels.log_data()

print('\nProgram execution complete.')

# inspect file
print('Sample TDMS groups/channels')
reader = my_tdms.TdmsReader(filename='+NF')
reader.read()

# Close out and exit
quit()

# Trash Bin:

# Obtain existing system
# sim = ni.system.System.local()
# devices = [device for device in sim.devices]
# print(sim.devices['cDAQ1'].ai_physical_chans)
