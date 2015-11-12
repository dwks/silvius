import os

class Automator:
    def __init__(self, real = True):
        self.xdo_list = []
        self.real = real

    def xdo(self, xdo):
        self.xdo_list.append(xdo)

    def flush(self):
        if len(self.xdo_list) == 0: return

        command = '/usr/bin/xdotool' + ' '
        command += ' '.join(self.xdo_list)
        self.execute(command)
        self.xdo_list = []

    def execute(self, command):
        if command == '': return

        print "`%s`" % command
        if self.real:
            os.system(command)
