# Claymore log file parser

import os
import time
import glob

class Claymologger:
    """ Claymore log file parser class """

    def __init__(self):
        self.logfile_name, self.logfile_time = self.get_last_logfile_name()


    def get_last_logfile_name(self):
        path = os.path.dirname(os.path.abspath(__file__))
        flist = glob.glob(os.path.join(path, '*_log.txt'))
        flist.sort(key = lambda x: os.path.getmtime(x), reverse=True)
        return (flist[0], os.path.getmtime(flist[0]))


    def parse_file(self):
        with open(self.logfile_name) as f:
            print(f.tell(), flush=True)
            f.readline()
            print(f.tell(), flush=True)
            f.readline()
            print(f.tell(), flush=True)
            f.readline()
            print(f.tell(), flush=True)
            f.readline()
            print(f.tell(), flush=True)


    def file_changed(self):
        lstf = self.get_last_logfile_name()
        if lstf[0] != self.logfile_name or lstf[1] != self.logfile_time:
            return True
        return False


    def run(self):
        self.parse_file()
        while True:
            time.sleep(3)
            if self.file_changed():
                self.parse_file()



g = Claymologger()
g.run()
