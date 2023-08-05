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
from ...base import savefig
from .dailydatalisting import ELEM_NAMES
from .dailydatalisting import Product as BaseProduct


class Product(BaseProduct):

    def generate_figure(self):

        super(Product, self).generate_figure()

        # Generate the title that will be displayed on the figure.
        mon_name = self.sdate.strftime('%B %Y ')
        stn_name = self.meta['name']
        title = mon_name + 'Temperature Data at ' + stn_name

        self.figure.suptitle(title, fontsize = 14, fontweight = 'bold')

        return None

    def get_params2(self):

        params = super(Product, self).get_params2()

        elems = params['elems']
        elems[0]['group_by'] = ['year', 
            self.sdate.strftime('%m-%d'), 
            self.edate.strftime('%m-%d')]
        elems[1]['group_by'] = ['year', 
            self.sdate.strftime('%m-%d'), 
            self.edate.strftime('%m-%d')]
        #params['elems'] = elems

        return params

    def setup(self, *args, **kwargs):

        today = datetime.date.today()
        self.year = kwargs.get('year', today.year)
        self.month = kwargs.get('month', today.month)

        mrange = calendar.monthrange(self.year, self.month)
        kwargs['sdate'] = datetime.date(self.year, self.month, 1)
        kwargs['edate'] = datetime.date(self.year, self.month, mrange[1])

        super(Product, self).setup(*args, **kwargs)

        return None


if __name__ == '__main__':

    argparser = argparse.ArgumentParser()
    argparser.add_argument('--csv_filename', 
        type = str, 
        dest = 'csv_filename', 
        default = '', 
        help = 'save the data in a CSV file with the given name')
    argparser.add_argument('--tfig_filename', 
        type = str, 
        dest = 'tfig_filename', 
        default = '', 
        help = 'save the temperature plot in a file with the given name')
    argparser.add_argument('--year', 
        type = int, 
        dest = 'year', 
        default = datetime.date.today().year, 
        help = 'a year value')
    argparser.add_argument('--month', 
        type = int, 
        dest = 'month', 
        default = datetime.date.today().month, 
        help = 'a month value')
    argparser.add_argument('sid', 
        type = str, 
        help = 'The station ID', 
        nargs = 1)

    args = argparser.parse_args()
    sid = args.sid[0]
    csv_filename = args.csv_filename
    tfig_filename = args.tfig_filename
    year = args.year
    month = args.month

    prod = Product(sid = sid, year = year, month = month)

    if csv_filename != '':
        csv.write(csv_filename, prod.table, demimiter = ',', 
            quoting = csv.QUOTE_MINIMAL)

    if tfig_filename != '':
        if prod.figure is not None:
            savefig(tfig_filename, prod.figure)
            prod.figure.savefig(tfig_filename, orientation = 'landscape', 
                dpi = 300)

    else:
        plt.show(prod.figure)


