# Коллектор логов с устройств Antminer L3+
# Прототип

import requests
import re
import sys


class Watcher:
    """ Logs collector class """
    
    def __init__(self, ip):
        self.miner_ip = ip
        self.html_content = ''

    def load_content_L3plus(self):
        try:
            r = requests.get('http://' + self.miner_ip + '/cgi-bin/minerStatus.cgi', auth=('root', 'root'))
        except Exception as e:
            print("Cannot connect to the specified IP.")
            print("Maybe, the wrong address or not L3+ device.")
            exit()
        r.encoding='utf-8'
        self.html_content = r.text
        return self.html_content

    def load_content_by_url(self, url):
        """ for test only ! """
        r = requests.get(url)
        r.encoding='utf-8'
        self.html_content = r.text
        return self.html_content

    def parse_log_string(self):
        if self.html_content == '':
            raise Exception('HTML content is not loaded. Use get_html_content method at first.')
        print(self.html_content)


# Start

if len(sys.argv) < 2:
    print('Please, specify the miner IP address')
    exit()
miner_ip = sys.argv[1]
w = Watcher(miner_ip)
#w.load_content_by_url('http://localhost/AntMiner.html')
w.load_content_L3plus()
w.parse_log_string()
