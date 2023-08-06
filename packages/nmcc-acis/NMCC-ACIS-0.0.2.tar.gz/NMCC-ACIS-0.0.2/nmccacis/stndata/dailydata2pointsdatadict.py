from simpletz import SimpleOffset
from simpletz import utc
import argparse
import copy
import datetime
import json
import sys
import urllib2


# The base URL used to make a data request from the acis system.
BASE_URL = 'http://data.rcc-acis.org/StnData'

# Default start and end dates
DEFAULT_START_DATE = datetime.date.today() - datetime.timedelta(days = 31)
DEFAULT_END_DATE = datetime.date.today()

COLUMN_INDICES = {'temp_max': 1, 'temp_min': 2, 'temp_mean': 3, 'temp': 4, 
    'precip_total': 5, 'snowfall_total': 6, 'snowdepth_total': 7}

# A dictionary of conversions to convert from imperial to SI units.
CONVERSIONS = {'temp_max': lambda x: (x - 32.0) * (5.0 / 9.0), 
    'temp_min': lambda x: (x - 32.0) * (5.0 / 9.0), 
    'temp_mean': lambda x: (x - 32.0) * (5.0 / 9.0), 
    'precip_total': lambda x: x * 25.4, 
    'snowfall_total': lambda x: x * 25.4, 
    'snowdepth_total': lambda x: x * 25.4}

# The daily variables used to construct the row dictionaries that will 
# be stored in the Product object's data_dict and data_list data 
# structures.
DAILY_VARIABLE_IDS = ['temp_max', 'temp_min', 'temp_mean', 'temp', 
    'precip_total', 
    'snowfall_total', 
    'snowdepth_total']


class Product(object):

    def __init__(self, *args, **kwargs):

        self.start_date = kwargs.get('start_date', DEFAULT_START_DATE)
        self.end_date = kwargs.get('end_date', DEFAULT_END_DATE)
        self.utcoffset = kwargs.get('utcoffset', None)
        self.station_id = kwargs.get('station_id', '')
        self.output = {'meta': {}, 'data': []}

        if self.utcoffset is not None:

            self.tzinfo = SimpleOffset(self.utcoffset)
            self.__process_data()

        return None

    def __check_qc(self, variable_id, converter, value):

        si_value = value

        try:

            si_value = float(value)
            si_value = converter(si_value)

        except:
            si_value = value

        return '1'

    def __convert(self, converter, value):

        try:

            fvalue = float(value)
            fvalue = converter(fvalue)

        except:
            fvalue = value

        return fvalue

    def __process_data(self):

        params = {}
        params['sid'] = self.station_id
        params['sdate'] = str(self.start_date)
        params['edate'] = str(self.end_date)
        params['elems'] = [
            {"name":"maxt"},
            {"name":"mint"},
            {"name":"avgt"},
            {"name":"obst"},
            {"name":"pcpn"},
            {"name":"snow"},
            {"name":"snwd"}]

        url = BASE_URL
        req = urllib2.Request(url, json.dumps(params), 
            {"Content-Type":"application/json"})

        try:

            response = urllib2.urlopen(req)
            json_output = json.loads(response.read())

        except urllib2.HTTPError as e:

            if e.code == 400: 
                print e.msg

            json_output = {}

        except Exception as e:

            print str(e)
            json_output = {}

        self.output['meta']['point_ids'] = [self.station_id]
        self.output['meta']['frequency_ids'] = ['daily']
        self.output['meta']['variable_ids'] = DAILY_VARIABLE_IDS

        for d in json_output.get('data', []):

            rdt = datetime.datetime(int(d[0][0:4]), 
                int(d[0][5:7]), 
                int(d[0][8:10]), 
                tzinfo = self.tzinfo).astimezone(utc)

            row = {}
            row['rdt'] = str(rdt)
            row['point_id'] = self.station_id
            row['frequency_id'] = 'daily'

            vbl_count = 0

            for variable_id in DAILY_VARIABLE_IDS:

                index = COLUMN_INDICES.get(variable_id, None)
                converter = CONVERSIONS.get(variable_id, lambda x: x)
                value = self.__convert(converter, d[index])

                val_dict = {}
                val_dict['value'] = value
                val_dict['qc'] = self.__check_qc(variable_id, converter, value)

                if value != 'M':

                    row[variable_id] = val_dict
                    vbl_count += 1

            if vbl_count > 0:
                self.output['data'].append(row)

        return None


def valid_date(date_str):
    return datetime.datetime.strptime(date_str, '%Y-%m-%d').date()


if __name__ == '__main__':

    argparser = argparse.ArgumentParser()
    argparser.add_argument('--start_date', 
        type = valid_date, 
        dest = 'start_date', 
        default = str(DEFAULT_START_DATE), 
        help = 'a start date in the form yyyy-mm-dd')
    argparser.add_argument('--end_date', 
        type = valid_date, 
        dest = 'end_date', 
        default = str(DEFAULT_END_DATE), 
        help = 'an end date in the form yyyy-mm-dd')
    argparser.add_argument('utcoffset', 
        type = int, 
        help = 'Adjust dates to utc datetimes')
    argparser.add_argument('station_id', 
        type = str, 
        help = 'the station ID')
    args = argparser.parse_args()

    product = Product(start_date = args.start_date, 
        end_date = args.end_date, 
        utcoffset = args.utcoffset, 
        station_id = args.station_id)

    sys.stdout.write(json.dumps(product.output) + '\n')
    sys.exit(0)


