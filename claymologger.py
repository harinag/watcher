# Claymore log file parser

import os
import time
import re
from watchdog.observers import Observer
import watchdog.events


class MyHandler(watchdog.events.FileSystemEventHandler):
    """ Handler for Observer scheduler """

    current_file = None
    current_seek = 0

    def on_modified(self, event):
        if event.is_directory:
            return
        fname = event.src_path
        if fname != self.current_file:
            if self.current_file is None:
                self.on_created(event)
        else:
            self.parse_lines()


    def on_created(self, event):
        if event.is_directory:
            return
        fname = event.src_path
        if re.match('.*_log.txt$', fname):
            self.__class__.current_file = fname
            self.__class__.current_seek = 0
            self.log_to_console('Swithced to new log file: ' + event.src_path)
            with open(self.current_file, 'r') as f:
                f.seek(0,2)
                self.current_seek = f.tell()


    def parse_lines(self):
        with open(self.current_file, 'r') as f:
            f.seek(self.current_seek)
            for line in f:
                self.log_to_console('### ' + line)            
            self.current_seek = f.tell()


    def log_to_console(self, msg):
        print(msg, flush=True)



class ClayLogger:
    """ Claymore log files parser """

    def __init__(self):
        self.current_file = None    # current log file name
        self.current_seek = 0       # current position in current file


    def run(self):
        obs = Observer()
        obs.schedule(MyHandler(), '.', recursive=False)
        obs.start()
        prop = '\|/-'
        i = 0
        try:
            while True:
                print('Logging ' + prop[i], end='\r', flush=True)
                i += 1
                if i == 4: i = 0
                time.sleep(0.5)
        except (KeyboardInterrupt, SystemExit):
            print('\nCTRL+C detected! Stop logging.', flush=True)
            obs.stop()
        obs.join()


# Start point
logger = ClayLogger()
logger.run()
