import argparse
import datetime
import json
import math
import sys
import urllib2
import wrapcsv as csv


# The base URL used to make a data request from the acis system.
BASE_URL = 'http://data.rcc-acis.org/StnData'

# Default start and end dates
DEFAULT_START_DATE = datetime.date.today() - datetime.timedelta(days = 31)
DEFAULT_END_DATE = datetime.date.today()

# The default element codes used to request data from the ACIS 
# system.
COLUMN_NAMES = ['Date', 
    'Max Temp (F)', 'Max Temp Normal (F)', 'Max Temp Departure (F)', 
    'Min Temp (F)', 'Min Temp Normal (F)', 'Min Temp Departure (F)', 
    'Mean Temp (F)', 'Mean Temp Normal (F)', 'Mean Temp Departure (F)', 
    'Observed Temp (F)', 
    'Precip (in)', 'Precip Normal (in)', 'Precip Departure (in)', 
    'Snowfall (in)', 'Snowfall Normal (in)', 'Snowfall Departure (in)', 
    'Snowdepth', 
    'Extreme Max Temp (F)', 'Extreme Max Temp Date', 
    'Extreme Min Temp (F)', 'Extreme Min Temp Date', 
    'Reference ET (in)']


class Product(object):

    def __init__(self, *args, **kwargs):

        self.start_date = kwargs.get('start_date', DEFAULT_START_DATE)
        self.end_date = kwargs.get('end_date', DEFAULT_END_DATE)
        self.station_id = kwargs.get('station_id', '')

        self.__extremes = {}
        self.output_listing = []

        self.__process_extremes()
        self.__process_data()

        return None

    def __calc_eth(self, date, latitude, temp_max, temp_min):

        # Convert temperatures to Celsius prior to computing the 
        # Hargreaves and Samani reference ET.
        temp_max = (temp_max - 32.0) * (5.0 / 9.0)
        temp_min = (temp_min - 32.0) * (5.0 / 9.0)

        phi = latitude * math.pi / 180.0
        day = self.__day(date)
        angle = 2 * math.pi / 365 * day
        delta = 0.409 * math.sin(angle -1.39)
        omegas = math.acos(-1.00 * math.tan(phi) * math.tan(delta))
        dr = 1 + 0.033 * math.cos(angle)

        term1 = (24.0 * 60.0) / math.pi
        term2 = omegas * math.sin(delta) * math.sin(phi)
        term3 = math.cos(phi) * math.cos(delta) * math.sin(omegas)

        # The value 0.082 is the Gsc solar constant.
        Ra = term1 * 0.082 * dr * (term2 + term3)

        term1 = 0.0023 * Ra
        term2 = ((temp_max + temp_min) / 2.0) + 17.8
        term3 = math.sqrt(temp_max - temp_min)

        eth = 0.408 * (term1 * term2 * term3)

        # Convert eth from mm to inches.
        eth = eth / 25.4

        return eth

    def __date_md(self, date):

        md = self.__date_str(date.month) + '-' + \
            self.__date_str(date.day)

        return md

    def __date_str(self, date_component):

        dc_str = ''

        if date_component < 10:
            dc_str = '0' + str(date_component)

        else:
            dc_str = str(date_component)

        return dc_str

    def __day(self, date):

        if date.year >= 1900:
            day = int(date.strftime('%j'))

        else:

            td = date - datetime.date(date.year, 1, 1)
            day = td.days + 1

        return day

    def __to_float(self, value):

        try:
            fvalue = float(value)

        except:
            fvalue = value

        return fvalue

    def __process_extremes(self):

        params = {}
        params['sid'] = self.station_id
        params['sdate'] = 'por'
        params['edate'] = 'por'
        params['meta'] = ['name', 'state', 'valid_daterange', 'sids']
        params['elems'] = []
        params['elems'].append({'name': 'maxt', 
            'interval': 'dly', 
            'duration': 'dly', 
            'smry': {'reduce': 'max', 'add': 'date'}, 
            'smry_only': 1, 
            'groupby': ['year', '01-01', '12-31']})
        params['elems'].append({'name': 'mint', 
            'interval': 'dly', 
            'duration': 'dly', 
            'smry': {'reduce': 'min', 'add': 'date'}, 
            'smry_only': 1, 
            'groupby': ['year', '01-01', '12-31']})

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

        summary = json_output.get('smry', [[], []])

        for count in range(0, len(summary[0])):

            # These are the temperature extreme values for a month and 
            # day.
            emaxt = float(summary[0][count][0])
            emint = float(summary[1][count][0])

            # The dates that the max and min extremes occurred on.
            d_emaxt = datetime.datetime(int(summary[0][count][1][0:4]), 
                int(summary[0][count][1][5:7]), 
                int(summary[0][count][1][8:10])).date()
            d_emint = datetime.datetime(int(summary[1][count][1][0:4]), 
                int(summary[1][count][1][5:7]), 
                int(summary[1][count][1][8:10])).date()

            # Create a string of the month and day for the max and min 
            # extremes.
            dx = self.__date_md(d_emaxt)
            dn = self.__date_md(d_emint)

            if not self.__extremes.has_key(dx):
                self.__extremes[dx] = {'max': {}, 'min': {}}

            if not self.__extremes.has_key(dn):
                self.__extremes[dn] = {'max': {}, 'min': {}}

            self.__extremes[dx]['max']['value'] = emaxt
            self.__extremes[dn]['min']['value'] = emint
            self.__extremes[dx]['max']['date'] = d_emaxt
            self.__extremes[dn]['min']['date'] = d_emint

        return None

    def __process_data(self):

        params = {}
        params['sid'] = self.station_id
        params['sdate'] = str(self.start_date)
        params['edate'] = str(self.end_date)
        params['elems'] = [
            {"name":"maxt"},
            {"name":"maxt","normal":"1","prec":1},
            {"name":"maxt","normal":"departure","prec":1},
            {"name":"mint"},
            {"name":"mint","normal":"1","prec":1},
            {"name":"mint","normal":"departure","prec":1},
            {"name":"avgt"},
            {"name":"avgt","normal":"1","prec":1},
            {"name":"avgt","normal":"departure","prec":1},
            {"name":"obst"},
            {"name":"pcpn"},
            {"name":"pcpn","normal":"1","prec":1},
            {"name":"pcpn","normal":"departure","prec":1},
            {"name":"snow"},
            {"name":"snow","normal":"1","prec":1},
            {"name":"snow","normal":"departure","prec":1},
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

        for d in json_output.get('data', []):

            date = datetime.datetime(int(d[0][0:4]), 
                int(d[0][5:7]), 
                int(d[0][8:10])).date()
            row = [date]

            for i in d[1:]:
                row.append(self.__to_float(i))

            date_md = self.__date_md(date)
            extx = self.__extremes.get(date_md, {}).get('max', {})
            extn = self.__extremes.get(date_md, {}).get('min', {})
            ext = [extx.get('value', ''), extx.get('date', ''), 
                extn.get('value', ''), extn.get('date', '')]
            row.extend(ext)

            lat = json_output.get('meta', {}).get('ll', [None, None])[1]

            try:
                eth = self.__calc_eth(date, float(lat), float(d[1]), 
                    float(d[4]))

            except:
                eth = 0.0

            row.append(eth)

            self.output_listing.append(row)

        return None


def valid_date(date_str):
    return datetime.datetime.strptime(date_str, '%Y-%m-%d').date()


if __name__ == '__main__':

    argparser = argparse.ArgumentParser()
    argparser.add_argument('--save_as', 
        dest = 'save_as', 
        default = '', 
        help = 'Save data to file')
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
    argparser.add_argument('station_id', 
        type = str, 
        help = 'the station ID')
    args = argparser.parse_args()

    product = Product(start_date = args.start_date, 
        end_date = args.end_date, 
        station_id = args.station_id)
    listing = product.output_listing

    output = ','.join(COLUMN_NAMES) + '\n'

    for l in listing:

        newrow = []

        for i in l:
            newrow.append(str(i))

        output += ','.join(newrow) + '\n'

    if args.save_as != '':

        f = open(args.save_as, 'w')
        f.write(output)
        f.close()

    else:
        sys.stdout.write(output)

    sys.exit(0)


