# Standard Library Imports
import argparse
import calendar
import datetime

# Numpy Package Imports
import numpy as np

# Matplotlib Package Imports
from matplotlib import dates as mdates
from matplotlib import patches as mpatches
from matplotlib import pyplot as plt
from matplotlib import ticker

# nmcc-dry Package Imports
from nmccdry import simple_csv as csv

# Local Package Imports
from ...base import Product as BaseProduct
from ...paramstypes import valid_date

TODAY = datetime.date.today()
DEFAULT_YEAR = TODAY.year


class Product(BaseProduct):

    name = 'StnData'

    def __find_highest(self, response_data):

        highest_yr = None
        highest_val = -999

        data = response_data.get('data', [])

        for d in data:

            tot = self.to_float(d[1][0])
            missing = int(d[1][1])

            if tot > highest_val:

                highest_yr = int(d[0][0:4])
                highest_val = tot

        return highest_yr

    def get_params(self):

        params = {}
        params['sid'] = self.sid
        params['sdate'] = str(self.sdate)
        params['edate'] = str(self.edate)
        params['meta'] = ['valid_daterange', 'name', 'state', 'sids']
        params['elems'] = [{'interval': 'dly', 'duration': 1, 'name': 'pcpn'}, 
            {'interval': 'dly', 'duration': 1, 'name': 'pcpn', 'normal': '1'}]

        return params

    def get_params2(self):

        r1_meta = self.response_data[0].get('meta', {})
        valid_dr = r1_meta.get('valid_daterange', 
            [['1900-12-31', str(datetime.date(DEFAULT_YEAR, 12, 31))], []])
        sdate = datetime.date(int(valid_dr[0][0][0:4]), 12, 31)
        edate = datetime.date(int(valid_dr[0][1][0:4]), 12, 31)

        elems0 = {}
        elems0['interval'] = [1, 0, 0]
        elems0['duration'] = 'std'
        elems0['reduce'] = {'reduce': 'sum', 'add': 'mcnt'}
        elems0['season_start'] = '01-01'
        elems0['name'] = 'pcpn'

        params = {}
        params['sid'] = self.sid
        params['sDate'] = str(sdate)
        params['eDate'] = str(edate)
        params['meta'] = []
        params['elems'] = [elems0]

        return params

    def get_params3(self):

        highest_yr = self.__find_highest(self.response_data[1])

        if highest_yr is not None:

            params = {}
            params['sid'] = self.sid
            params['sDate'] = str(highest_yr) + '-01-01'
            params['eDate'] = str(highest_yr) + '-12-31'
            params['meta'] = []
            params['elems'] = [
                {'interval': 'dly', 'duration': 'dly', 'name': 'pcpn'}]

        else:
            params = {}

        return params

    def setup(self, *args, **kwargs):

        self.sid = kwargs.get('sid', '')
        self.sdate = kwargs.get('sdate', datetime.date(DEFAULT_YEAR, 1, 1))
        self.edate = kwargs.get('edate', datetime.date(DEFAULT_YEAR, 12, 31))

        self.meta = {'sid': self.sid, 
            'name': kwargs.get('stn_name', ''), 
            'latitude': 0, 
            'longitude': 0, 
            'elevation': 0}

        return None


if __name__ == '__main__':

    argparser = argparse.ArgumentParser()
    argparser.add_argument('--csv_filename', 
        type = str, 
        dest = 'csv_filename', 
        default = '', 
        help = 'save the data in a CSV file with the given name')
    argparser.add_argument('--pfig_filename', 
        type = str, 
        dest = 'pfig_filename', 
        default = '', 
        help = 'save the precipitation plot in a file with the given name')
    argparser.add_argument('--year', 
        type = int, 
        dest = 'year', 
        default = datetime.date.today().year, 
        help = 'a year value')
    argparser.add_argument('sid', 
        type = str, 
        help = 'The station ID', 
        nargs = 1)

    args = argparser.parse_args()
    sid = args.sid[0]
    csv_filename = args.csv_filename
    pfig_filename = args.pfig_filename
    year = args.year

    prod = Product(sid = sid, year = year)

    if csv_filename != '':
        csv.write(csv_filename, prod.table, demimiter = ',', 
            quoting = csv.QUOTE_MINIMAL)

    #if pfig_filename != '':
    #    if prod.figure is not None:
    #        prod.figure.savefig(pfig_filename)

    #else:
    #    plt.show(prod.figure)


