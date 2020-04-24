import http.client
import requests

def read_auto_inf():
    # Funcion para leer la ip, port y remember_status (recordar datos) de un archivo

    try:
        fp = open("auto_ip.inf", 'r')
        lines = fp.readlines()
        for line in lines:
            if "ip" in line:
                ip = line.replace(' ', '').replace('\n', '').split(':')[1]

            elif "port" in line:
                port = line.replace(' ', '').replace('\n', '').split(':')[1]

            elif "remember_status" in line:
                remember_status = line.replace(' ', '').replace('\n', '').split(':')[1]
        fp.close()
        return ip, port, int(remember_status)
    except IOError:
        return -1

def connection(server_url):
    cmd = 'connection_test'
    url = server_url + cmd + "/"
    print('url: %s' % url)
    # if server find there is 'connection_test' in request url, server will response 'Ok'
    try:
        r = requests.get(url)
        if r.text == 'OK':
            return True
    except:
        return False

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


# Actions -------------------------------------------------------------------------------------------------

def __request__(url, times=10):
    for x in range(times):
        try:
            requests.get(url)
            return 0
        except:
            print("Connection error, try again")
    print("Abort")
    return -1

def run_action(cmd, base_url):  # Esta funcion le pide al servidor que haga algo, las posibles opciones estan abajo
    # Estoy pensando que quizas podamos modificar estas opciones en el archivo del servidor
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
    url = base_url + 'run/?action=' + cmd
    print('url: %s' % url)
    # post request with url
    __request__(url)

def run_speed(speed, base_url):
    """Ask server to set speed, use in running mode

    Post requests to server, server will set speed according to the url.
    This function for running mode.

    Args:
        '0'~'100'
    """
    # Set set-speed url
    url = base_url + 'run/?speed=' + str(speed)
    print('url: %s' % url)
    # Set speed
    __request__(url)

def cali_action(cmd, base_url):
    """Ask server to do sth, use in calibration mode

    Post requests to server, server will do what client want to do according to the url.
    This function for calibration mode

    Args:
        # ============== Back wheels =============
        'bwcali' | 'bwcalileft' | 'bwcaliright' | 'bwcaliok'

        # ============== Front wheels =============
        'fwcali' | 'fwcalileft' | 'fwcaliright' |  'fwcaliok'

        # ================ Camera =================
        'camcali' | 'camcaliup' | 'camcalidown' | 'camcalileft' | 'camright' | 'camcaliok'

    """
    # set the url include cali information
    url = base_url + 'cali/?action=' + cmd
    print('url: %s' % url)
    # post request with url
    __request__(url)