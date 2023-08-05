# Standard Library Imports
import json
import os
import urllib2

# Matplotlib Package Imports
from matplotlib import cbook
from matplotlib import pyplot as plt


# The base URL used to make a data request from the acis system.  This 
# URL is only the hostname of the acis servers.  To use it for a 
# product, an application string must be appended.  For example, 
# to retrieve single station data, 'StnData' would be appended.
BASE_URL = 'http://data.rcc-acis.org/'


class Product(object):

    name = ''

    def __init__(self, *args, **kwargs):

        self.response_data = []
        self.num_requests = 0

        for aname in dir(self):
            if aname.startswith('get_params'):
                self.num_requests += 1

        self.handle(*args, **kwargs)

        return None

    def handle(self, *args, **kwargs):

        self.setup(*args, **kwargs)
        self.make_requests()
        self.post_process()

        return None

    def make_request(self, params):

        url = BASE_URL + self.name
        req = urllib2.Request(url, json.dumps(params), 
            {"Content-Type":"application/json"})

        try:

            response = urllib2.urlopen(req)
            response_data = json.loads(response.read())

        except urllib2.HTTPError as e:

            if e.code == 400: 
                print e.msg

            else:
                print str(e)

            response_data = {}

        except Exception as e:

            print str(e)
            response_data = {}

        return response_data

    def make_requests(self):

        for i in range(1, self.num_requests + 1):

            method_name = 'get_params'

            if i > 1:
                method_name += str(i)

            response_data = {}
            method = getattr(self, method_name, None)

            try:
                params = method()

            except Exception as e:

                print str(e)
                params = {}

            if len(params.keys()) > 0:
                response_data = self.make_request(params)

            self.response_data.append(response_data)

        return None

    def post_process(self):

        return None

    def setup(self, *args, **kwargs):

        return None

    def to_float(self, value):

        try:
            value = float(value)

        except:
            value = float('nan')

        return value


def savefig(filename, figure):

    #TESTING
    path = os.path.dirname(os.path.abspath(__file__)) + '/static/nmccacis/'
    image_filename = path + 'nm_climate_center_logo_small_trans.png'
    image_file = cbook.get_sample_data(image_filename)
    image = plt.imread(image_file)

    figure.figimage(image, 35, 20)
    figure.savefig(filename, orientation = 'landscape', dpi = 300)

    return None


