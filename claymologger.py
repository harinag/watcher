# Claymore log file parser

import os
import time
import re
from watchdog.observers import Observer
import watchdog.events
import json


class MyHandler(watchdog.events.FileSystemEventHandler):
    """ Handler for Observer scheduler """

    current_file = None
    current_seek = 0

    def on_modified(self, event):
        print("-M-", flush=True)
        if event.is_directory:
            return
        fname = event.src_path
        if fname != self.current_file:
            self.on_created(event)
        else:
            self.process_lines()


    def on_created(self, event):
        print("-C-", flush=True)
        if event.is_directory:
            return
        fname = event.src_path
        if re.match('.*_log.txt$', fname):
            self.__class__.current_file = fname
            self .__class__.current_seek = 0
            self.log_to_console('Swithced to new log file: ' + event.src_path)
            with open(self.current_file, 'r') as f:
                f.seek(0,2)
                self.current_seek = f.tell()


    def process_lines(self):
        with open(self.current_file, 'r') as f:
            try:
                f.seek(self.current_seek)
            except:
                print("Trouble with seek call", flush=True)
                return
            for line in f:
                print("Processing: " + line)
                if len(line) < 3: continue
                j = self.parse_line(line)
                #self.log_to_server(j)
                if j: self.log_to_console('Logged: ' + j)
            self.current_seek = f.tell()


    def parse_line(self, line):
        # Recognized line formats:
        # 1) ETH: GPU0 21.166 Mh/s, GPU1 16.327 Mh/s, GPU2 21.167 Mh/s
        # 2) GPU0 t=63C fan=45%, GPU1 t=63C fan=49%, GPU2 t=61C fan=40%
        # 3) ETH - Total Speed: 58.660 Mh/s, Total Shares: 0, Rejected: 0, Time: 00:00
        j = {
            'account_name' : 'test', 'account_key' : 123, 'rig_id' : 1, 'unchanged' : None,
            'logs' : {
                'gpus' : {},
                'total_speed' : [],
                'total_shares' : [],
                'rejected' : []
            }
        }
        gpu = { 'speed' : [], 'temp' : [], 'fan': [] }
        r = re.match('(\d\d:\d\d:\d\d:\d\d\d).(...).(.+)', line)
        if not r: return None
        log_time = r.group(1)
        log_prefix = r.group(2)
        msg = r.group(3)
        # Try to identify line N1
        match = re.findall('(GPU\d) (.+?) Mh/s', msg)
        if match:
            # matched line N1
            del j['unchanged']
            for tpl in match:
                g = gpu.copy()
                g['speed'] = [tpl[1]]
                j['logs']['gpus'][tpl[0]] = g
        # Try to identify line N2
        match = re.findall('(GPU\d) t=(.+?)C fan=(.+?)%', msg)
        if match:
            # matched line N2
            del j['unchanged']
            for tpl in match:
                g = gpu.copy()
                g['temp'] = [tpl[1]]
                g['fan'] = [tpl[2]]
                j['logs']['gpus'][tpl[0]] = g
        # Try to identify line N3
        match = re.search('Total Speed: (.+?) Mh/s, Total Shares: (.+?), Rejected: (.+?),', msg)
        if match:
            #matched line N3
            del j['unchanged']
            j['logs']['total_speed'] = match.group(1)
            j['logs']['total_shares'] = match.group(2)
            j['logs']['rejected'] = match.group(3)
        # Now j contains found data (if did) 
        if 'unchanged' in j: return None
        else: return json.dumps(j)


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
#print(MyHandler.parse_line('18:57:28:792 1d8 got 248 bytes'))
