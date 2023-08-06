from matplotlib import cbook
from matplotlib import dates as mdates
from matplotlib import patches as mpatches
from matplotlib import pyplot as plt
from matplotlib import ticker
import argparse
import datetime
import json
import numpy as np
import sys
import urllib2


# The base URL used to make a data request from the acis system.
BASE_URL = 'http://data.rcc-acis.org/StnData'

# Default start and end dates
DEFAULT_START_DATE = datetime.date.today() - datetime.timedelta(days = 31)
DEFAULT_END_DATE = datetime.date.today()

MONTH_ABBREV_NAMES = ['', 
    'Jan', 
    'Feb', 
    'Mar', 
    'Apr',
    'May', 
    'Jun', 
    'Jul',
    'Aug', 
    'Sep',
    'Oct', 
    'Nov',
    'Dec'
]


class Product(object):

    def __init__(self, *args, **kwargs):

        self.si_units = kwargs.get('si_units', False)
        self.start_date = kwargs.get('start_date', DEFAULT_START_DATE)
        self.end_date = kwargs.get('end_date', DEFAULT_END_DATE)
        self.station_id = kwargs.get('station_id', '')

        self.__meta = {}
        self.__extremes = {}
        self.__data = []

        self.__process_extremes()
        self.__process_data()
        self.__generate_fig()

        return None

    def __date_md(self, date):

        try:
            md = self.__date_str_component(date.month) + '-' + \
                self.__date_str_component(date.day)

        except:
            md = ''

        return md

    def __date_str_component(self, date_component):

        dc_str = ''

        if date_component < 10:
            dc_str = '0' + str(date_component)

        else:
            dc_str = str(date_component)

        return dc_str

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

            if self.si_units == True:

                emaxt = (emaxt - 32.0) * (5.0 / 9.0)
                emint = (emint - 32.0) * (5.0 / 9.0)

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
                self.__extremes[dx] = {'max': '', 'min': ''}

            if not self.__extremes.has_key(dn):
                self.__extremes[dn] = {'max': '', 'min': ''}

            self.__extremes[dx]['max'] = emaxt
            self.__extremes[dn]['min'] = emint

        return None

    def __process_data(self):

        params = {}
        params['sid'] = self.station_id
        params['sdate'] = str(self.start_date)
        params['edate'] = str(self.end_date)
        params['elems'] = [
            {"name":"maxt"},
            {"name":"maxt","normal":"1","prec":1},
            {"name":"mint"},
            {"name":"mint","normal":"1","prec":1}]

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

        self.__meta = json_output.get('meta', {})
        self.__dates = []
        self.__data = []

        for row in json_output.get('data', []):

            date = datetime.datetime(int(row[0][0:4]), 
                int(row[0][5:7]), 
                int(row[0][8:10])).date()

            data_row = []

            for i in row[1:]:

                value = self.__to_float(i)

                if self.si_units is True:
                    value = (value - 32.0) * (5.0 / 9.0)

                data_row.append(value)

            date_md = self.__date_md(date)
            extx = self.__extremes.get(date_md, {}).get('max', float('nan'))
            extn = self.__extremes.get(date_md, {}).get('min', float('nan'))

            data_row.extend([self.__to_float(extx), self.__to_float(extn)])

            self.__dates.append(date)
            self.__data.append(data_row)

        return None

    def __generate_fig(self):

        # Generate the title that will be displayed on the figure.
        #smon_name = self.start_date.strftime('%b %Y ')
        #emon_name = self.end_date.strftime('%b %Y ')

        smon_name = MONTH_ABBREV_NAMES[self.start_date.month] + ' ' + \
            str(self.start_date.day) + ', ' + \
            str(self.start_date.year) + ' '
        emon_name = MONTH_ABBREV_NAMES[self.end_date.month] + ' ' + \
            str(self.end_date.day) + ', ' + \
            str(self.end_date.year) + ' '

        stn_name = self.__meta.get('name', '')
        title = smon_name + ' To ' + emon_name + 'Temperature Data at ' + \
            stn_name

        # Here we create the numpy arrays for graphing.
        dates = np.array(self.__dates)
        data = np.array(self.__data)

        # Here we get the observed max temp, and observed min temp 
        # arrays.
        ymaxt = data[:, 0]
        ymint = data[:, 2]

        # Here we get the max temp normals and min temp normals arrays.
        ynmaxt = data[:, 1]
        ynmint = data[:, 3]

        # Here we get the record max temp and record min temp arrays.
        yemaxt = data[:, 4]
        yemint = data[:, 5]

        # Create the figure object, setting the size of the figure and 
        # the title.
        fig = plt.figure()
        fig.set_size_inches(10, 7)
        fig.suptitle(title, fontsize = 12, fontweight = 'bold')
        fig.autofmt_xdate(bottom = 0.4)
        #fig.text(0.645, 0.0675, 'Source: http://data.rcc-acis.org')

        # Create the subplot inside the figure.
        ax = fig.add_subplot(111)

        # Plot the observable temperature range.
        ax.vlines(dates, ymint, ymaxt, lw = 5)

        # Plot the temperature normals and fill between the plots with 
        # a semi transparent green.
        ax.plot(dates, ynmaxt, color = 'green', alpha = 0.1)
        ax.plot(dates, ynmint, color = 'green', alpha = 0.1)
        ax.fill_between(dates, ynmint, ynmaxt, facecolor = 'green', 
            alpha = 0.5)

        # Plot the temperature records.  Fill the plot between the 
        # normal max temperatures and the record max temperatures with 
        # a semi transparent red.  Fill the plot between the normal 
        # min temperatures and the record min temperatures with a semi 
        # transparent blue.
        ax.plot(dates, yemaxt, color = 'red')
        ax.plot(dates, yemint, color = 'blue')
        ax.fill_between(dates, ynmaxt, yemaxt, facecolor = 'red', alpha = 0.5)
        ax.fill_between(dates, ynmint, yemint, facecolor = 'blue', alpha = 0.5)

        # Here we will add the axis labels and rotate the tick labels 
        # so the figure will render a bit better.
        ylabel = 'Temperature (F)'

        if self.si_units is True:
            ylabel = 'Temperature (C)'

        ax.grid(True)
        ax.set_ylabel(ylabel)
        ax.set_xlabel('Date')
        ax.xaxis.set_major_locator(mdates.AutoDateLocator())
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))

        for label in ax.xaxis.get_ticklabels():
            label.set_rotation(70)

        #nml_proxy = mpatches.Patch(color='green')
        llines = (mpatches.Patch(color = 'black'), 
            mpatches.Patch(color = 'green'), 
            mpatches.Patch(color = 'red'), 
            mpatches.Patch(color = 'blue'),)
        llabels = ('Observed Temperature Range', 
            'Normal Temperature Range', 
            'Extreme Max', 
            'Extreme Min',)
        ax.legend(llines, llabels, 
            #bbox_to_anchor=(0., .01, 1., .102), 
            loc = 3, 
            bbox_to_anchor = (0., -0.55, 1., .102), 
            ncol = 2, 
            mode = 'expand', 
            borderaxespad = 0.)

        self.figure = fig

        return None

    def __to_float(self, value):

        try:
            value = float(value)

        except:
            value = float('nan')

        return value


def valid_date(date_str):
    return datetime.datetime.strptime(date_str, '%Y-%m-%d').date()


if __name__ == '__main__':

    argparser = argparse.ArgumentParser()
    argparser.add_argument('--save_as', 
        dest = 'save_as', 
        default = '', 
        help = 'Save figure to file')
    argparser.add_argument('--si_units',  
        dest = 'si_units', 
        action = 'store_true', 
        help = 'Convert to SI units')
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
    
    product = Product(si_units = args.si_units, 
        start_date = args.start_date, 
        end_date = args.end_date, 
        station_id = args.station_id)

    if args.save_as != '':
        product.figure.savefig(args.save_as, 
            orientation = 'landscape', 
            dpi = 300)

    else:
        plt.show(product.figure)

    sys.exit(0)


