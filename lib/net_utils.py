import numpy as np
import requests
from PIL import Image

import http.client
import io
from time import sleep


def __request__(url, times=10):
    for x in range(times):
        try:
            requests.get(url)
            return 0
        except:
            print("Connection error, try again")
    print('Abort')
    return -1

class QueryImage:
    """Query Image

    Query images form http. eg: queryImage = QueryImage(HOST)

    Attributes:
        host, port. Port default 8080, post need to set when creat a new object

    """

    def __init__(self, host, port=8080, argv="/?action=snapshot"):
        # default port 8080, the same as mjpg-streamer server
        self.host = host
        self.port = port
        self.argv = argv
        #print(self.argv)

    def queryImage(self):
        """Query Image
        Query images form http.eg:data = queryImage.queryImage()
        Args:
            None
        Return:
            returnmsg.read(), http response data
        """
        http_data = http.client.HTTPConnection(self.host, self.port)
        http_data.putrequest('GET', self.argv)
        http_data.putheader('Host', self.host)
        http_data.putheader('User-agent', 'python-http.client')
        http_data.putheader('Content-type', 'image/jpeg')
        http_data.endheaders()

        returnmsg = http_data.getresponse()

        return returnmsg.read()

class Connect():

    def __init__(self, server_ip, server_port, timeout=1):
        self.server_ip = server_ip
        self.server_port = server_port
        self.timeout = timeout
        self.server_url = 'http://' + server_ip + ':' + server_port + '/'
        print(self.server_url)
    def connection_ok(self):
        """Check if connection is ok
        Post a request to server, if connection ok, server will return http response 'ok'
        Args:
            none
        Returns:
            if connection ok, return True
            if connection not ok, return False
        """
        cmd = 'connection_test'
        url = self.server_url + cmd + "/"
        print('url: %s' % url)
        # if server find there is 'connection_test' in request url, server will response 'Ok'
        try:
            r = requests.get(url)
            if r.text == 'OK':
                return True
        except:
            return False

    def capture_one_img(self):
        self.queryImage = QueryImage(self.server_ip)  # Hace la conexion con el servidor
        data = self.queryImage.queryImage()  # Recibe la imagen del servidor (en bits)
        if not data:
            print('No data received')
            return None
        else:
            image = np.array(Image.open(io.BytesIO(data)))
            return image

    def start_stream(self, frame_frecuency=0.01):
        while True:
            image = self.capture_one_img()
            sleep(frame_frecuency)
            #cv2.imwrite('./images/{}.jpg'.format(time.time()), image[:,:,[2,1,0]])
            return image

    def run_action(self, cmd):
        """Ask server to do sth, use in running mode

        Post requests to server, server will do what client want to do according to the url.
        This function for running mode

        Args:
        # ============== Back wheels =============
        'bwready' | 'forward' | 'backward' | 'stop'

        # ============== Front wheels =============
        'fwready' | 'fwleft' | 'fwright' |  'fwstraight'

        # ================ Camera =================
        'camready' | 'camleft' | 'camright' | 'camup' | 'camdown'
        """
        # set the url include action information
        url = self.server_url + 'run/?action=' + cmd
        #print('url: %s' % url)
        # post request with url
        __request__(url)
        return None