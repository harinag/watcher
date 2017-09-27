# Коллектор логов с устройств Antminer L3+
# Прототип

import requests
import re
import argparse
import time

class Watcher:
    """ Logs collector class """
    
    def __init__(self, ip):
        self.miner_ip = ip
        self.miner_url = 'http://' + self.miner_ip + '/cgi-bin/minerStatus.cgi'
        self.html_content = ''
        self.log_file_name = self.miner_ip + '.log'


    def load_html_content(self):
        try:
            r = requests.get(self.miner_url, auth=('root', 'root'))
        except Exception as e:
            print("Cannot connect to the specified IP.")
            print("Maybe, the wrong address or not L3+ device.")
            exit()
        r.encoding='utf-8'
        self.html_content = r.text
        return self.html_content


    def parse_html(self):
        if self.html_content == '':
            raise Exception('HTML content is not loaded.')
        mas = []
        # MH/S data
        mhsrt = re.search('<div id="ant_ghs5s">([\d.]+)</div>', self.html_content, re.I).group(1)
        mas.append('Reported hashrate: ' + mhsrt)
        mhsavg = re.search('<div id="ant_ghsav">([\d.]+)</div>', self.html_content, re.I).group(1)
        mas.append('Average hashrate: ' + mhsavg)
        # Pools and chains data
        rows = re.findall('<tr class="cbi-section-table-row cbi-rowstyle-1" id="cbi-table-1">[\s\S]*?</tr>', self.html_content, re.M|re.I)
        pools = []
        chains = []
        for row in rows:
            pool = re.search('<div id="cbi-table-1-pool">([0-9]+?)</div>', row, re.I)
            if pool:
                pool = pool.group(1)
                status = re.search('<div id="cbi-table-1-status">(.+?)</div>', row, re.I).group(1)
                accepted = re.search('<div id="cbi-table-1-accepted">(.+?)</div>', row, re.I).group(1)
                rejected = re.search('<div id="cbi-table-1-rejected">(.+?)</div>', row, re.I).group(1)
                pools.append('* Pool {}: Status: {}; Accepted: {}; Rejected: {}'.format(pool, status, accepted, rejected))
            chain = re.search('<div id="cbi-table-1-chain">([0-9]+?)</div>', row, re.I)
            if chain:
                chain = chain.group(1)
                mhs = re.search('<div id="cbi-table-1-rate">(.+?)</div>', row, re.I).group(1)
                temp_pcb = re.search('<div id="cbi-table-1-temp">(.+?)</div>', row, re.I).group(1)
                temp_chip = re.search('<div id="cbi-table-1-temp2">(.+?)</div>', row, re.I).group(1)
                chains.append('- Chain {}: MH/S(RT): {}; Temp(PCB): {}; Temp(Chip): {}'.format(chain, mhs, temp_pcb, temp_chip))
        mas.append('\n'.join(pools))
        mas.append('\n'.join(chains))
        # Fans data
        fan1 = re.search('<td id="ant_fan1" class="cbi-rowstyle-1 cbi-value-field">(.+?)</td>', self.html_content, re.I).group(1)
        fan2 = re.search('<td id="ant_fan2" class="cbi-rowstyle-1 cbi-value-field">(.+?)</td>', self.html_content, re.I).group(1)
        mas.append('Fan 1 speed: {}'.format(fan1,))
        mas.append('Fan 2 speed: {}'.format(fan2,))
        # Its all!
        s = '\n'.join(mas)
        return(s)



    def run(self):
        """ Run watcher """
        counter = 0
        print("Watcher is running. Press CTRL+C to stop")
        print("Logging to file: " + self.log_file_name)
        while True:
            log_str = self.parse_html()
            with open(self.log_file_name, 'a') as f:
                f.write('\n===\n{}\n{}\n'.format(time.strftime('%d.%m.%Y %H:%M:%S'), log_str))
            counter += 1
            print('Lines logged: {} \r'.format(counter,), flush=True, end='')
            time.sleep(1)


# Start

# Parse command line args
parser = argparse.ArgumentParser()
parser.add_argument('-t', '--test', help='for testing only', action='store_true')
parser.add_argument('-r', '--run', help='run watcher', action='store_true')
parser.add_argument('ip', help='Miner IP address in LAN')
args = parser.parse_args()
# Logging
miner_ip = args.ip
w = Watcher(miner_ip)
if args.test:
    w.miner_url = 'http://localhost/AntMiner.html'
w.load_html_content()
if args.run:
    w.run()
else:
    w.parse_html()
