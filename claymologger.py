# Claymore log file parser

import os
import time
import glob
import logging
from watchdog.observers import Observer
import watchdog.events

class MyHandler(watchdog.events.FileSystemEventHandler):
    """ Handler for Observer scheduler """

    def on_modified(self, event):
        print(event, flush=True)

    def on_created(self, event):
        print(event, flush=True)


# Start point

obs = Observer()
hndl = MyHandler()
obs.schedule(hndl, '.', recursive=False)
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

