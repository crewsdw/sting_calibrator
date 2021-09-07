from nptdms import TdmsFile


class TdmsReader:
    def __init__(self, filename):
        self.filename = filename
        self.file = TdmsFile.read('data\\' + filename + '.tdms')

    def read(self):
        all_groups = self.file.groups()
        print(all_groups)
        channels0 = all_groups[0].channels()
        channels1 = all_groups[1].channels()
        print(channels0)
        print(channels1)
