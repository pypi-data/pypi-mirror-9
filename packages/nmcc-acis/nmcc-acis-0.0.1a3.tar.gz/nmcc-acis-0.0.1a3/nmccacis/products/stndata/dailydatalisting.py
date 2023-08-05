from ...base import Product as BaseProduct
from ...paramstypes import valid_date
from matplotlib import cbook
from matplotlib import dates as mdates
from matplotlib import patches as mpatches
from matplotlib import pyplot as plt
from matplotlib import ticker
import argparse
import datetime
import math
import numpy as np
import wrapcsv as csv


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

ELEM_PARAMS = [
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


PLOT_TEMP = 'temp'
PLOT_PRECIP = 'precip'


class Product(BaseProduct):

    name = 'StnData'

    def __calculate_eth(self, date, latitude, temp_max, temp_min):

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

    def __generate_temp_plot(self):

        # Generate the title that will be displayed on the figure.
        #smon_name = self.start_date.strftime('%b %Y ')
        #emon_name = self.end_date.strftime('%b %Y ')

        smon_name = MONTH_ABBREV_NAMES[self.start_date.month] + ' ' + \
            str(self.start_date.year) + ' '
        emon_name = MONTH_ABBREV_NAMES[self.end_date.month] + ' ' + \
            str(self.end_date.year) + ' '

        stn_name = self.station_name
        title = smon_name + ' To ' + emon_name + 'Temperature Data at ' + \
            stn_name

        # Here we create the numpy arrays for graphing.
        dates = np.array(self.__dates)
        data = np.array(self.__data)

        # Here we get the observed max temp, and observed min temp 
        # arrays.
        ymaxt = data[:, 0]
        ymint = data[:, 3]

        # Here we get the max temp normals and min temp normals arrays.
        ynmaxt = data[:, 1]
        ynmint = data[:, 4]

        # Here we get the record max temp and record min temp arrays.
        yemaxt = data[:, -3]
        yemint = data[:, -2]

        # Create the figure object, setting the size of the figure and 
        # the title.
        fig = plt.figure()
        fig.set_size_inches(10, 7)
        fig.suptitle(title, fontsize = 14, fontweight = 'bold')
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
        ax.grid(True)
        ax.set_ylabel('Temperature (F)')
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

        # The temperature figure is saved to an attribute with a name 
        # containing plot instead of figure.  Better for human 
        # readability?
        self.output_temp_plot = fig

        return None

    def get_params(self):

        params = {}
        params['sid'] = self.station_id
        params['sdate'] = str(self.start_date)
        params['edate'] = str(self.end_date)
        params['elems'] = ELEM_PARAMS

        return params

    def get_params2(self):

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

        return params

    def post_process(self):

        r2 = self.response_data[1]
        r2smry = r2.get('smry', [[], []])

        ext = {}
        count = 0
        length = len(r2smry[0])

        while count < length:

            emaxt = r2smry[0][count][0]
            emint = r2smry[1][count][0]
            d_emaxt = datetime.datetime(int(r2smry[0][count][1][0:4]), 
                int(r2smry[0][count][1][5:7]), 
                int(r2smry[0][count][1][8:10])).date()
            d_emint = datetime.datetime(int(r2smry[1][count][1][0:4]), 
                int(r2smry[1][count][1][5:7]), 
                int(r2smry[1][count][1][8:10])).date()

            dxm = self.__date_str(d_emaxt.month)
            dxd = self.__date_str(d_emaxt.day)

            dnm = self.__date_str(d_emint.month)
            dnd = self.__date_str(d_emint.day)

            dx = dxm + '-' + dxd
            dn = dnm + '-' + dnd

            if not ext.has_key(dx):
                ext[dx] = {'max': [0, 0], 'min': [0, 0]}

            if not ext.has_key(dn):
                ext[dn] = {'max': [0, 0], 'min': [0, 0]}

            ext[dx]['max'] = [emaxt, d_emaxt]
            ext[dn]['min'] = [emint, d_emint]

            count += 1

        r1 = self.response_data[0]
        r1meta = r1.get('meta', {})
        r1data = r1.get('data', [])

        self.latitude = r1meta.get('ll', [0, 0])[1]
        self.longitude = r1meta.get('ll', [0, 0])[0]
        self.elevation = r1meta.get('elev', 0)

        if self.station_name == '':
            self.station_name = r1meta.get('name', '')

        #self.output_table = [COLUMN_NAMES]

        for d in r1data:

            date = datetime.datetime(int(d[0][0:4]), 
                int(d[0][5:7]), 
                int(d[0][8:10])).date()

            drow = []
            #row = [str(date)]
            row = [date]

            for i in d[1:]:

                drow.append(self.to_float(i))
                row.append(i)

            date_md = self.__date_md(date)
            extremes = ext[date_md]
            ex = extremes['max']
            en = extremes['min']

            try:
                eth = self.__calculate_eth(date, self.latitude, 
                    float(d[1]), float(d[4]))

            except:
                eth = 0.0

            drow.extend([self.to_float(ex[0]), self.to_float(en[0]), eth])
            row.extend([ex[0], ex[1], en[0], en[1], eth])

            self.__dates.append(date)
            self.__data.append(drow)
            self.output_table.append(row)            

        self.__generate_temp_plot()

        return None

    def setup(self, *args, **kwargs):

        self.start_date = kwargs.get('start_date', DEFAULT_START_DATE)
        self.end_date = kwargs.get('end_date', DEFAULT_END_DATE)
        self.station_id = kwargs.get('station_id', '')
        self.station_name = kwargs.get('station_name', '')
        self.latitude = 0
        self.longitude = 0
        self.elevation = 0

        # Internal data structures for building figures.  Not intended 
        # to be called from outside this class.
        self.__dates = []
        self.__data = []

        # The human readable CSV output.
        self.output_table = []

        # The figure attributes.  These contain matplotlib rendered 
        # figures that can be saved or displayed.
        self.output_temp_plot = None
        self.output_precip_plot = None

        return None


if __name__ == '__main__':

    argparser = argparse.ArgumentParser()
    argparser.add_argument('--plot', 
        choices = [PLOT_TEMP], 
        dest = 'plot', 
        default = PLOT_TEMP, 
        help = 'choose the type of plot to show or save')
    argparser.add_argument('--output_to', 
        type = str, 
        dest = 'output_to', 
        default = '', 
        help = 'output data to a given location')
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
    plot = args.plot
    output_to = args.output_to
    start_date = args.start_date
    end_date = args.end_date
    station_id = args.station_id

    prod = Product(start_date = start_date, end_date = end_date, 
        station_id = station_id)

    if output_to.endswith('.csv'):
        csv.write(output_to, 
            prod.output_table, 
            delimiter = ',', 
            quoting = csv.QUOTE_MINIMAL, 
            header = [COLUMN_NAMES])

    elif output_to.endswith('.png'):

        if plot == PLOT_TEMP:
            if prod.output_temp_plot is not None:
                prod.output_temp_plot.savefig(output_to, 
                    orientation = 'landscape', 
                    dpi = 300)

    else:
        plt.show(prod.output_temp_plot)


