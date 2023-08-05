from .base import Product as BaseProduct
from .paramstypes import valid_date
from simpletz import SimpleOffset
from simpletz import utc
import argparse
import copy
import datetime
import json


# Default start and end dates
DEFAULT_START_DATE = datetime.date.today() - datetime.timedelta(days = 31)
DEFAULT_END_DATE = datetime.date.today()


COLUMN_INDICES = {'temp_max': 1, 'temp_min': 4, 'temp_mean': 7, 
    'temp_max_normal': 2, 'temp_min_normal': 5, 'temp_mean_normal': 8, 
    'temp_max_departure': 3, 'temp_min_departure': 6, 'temp_mean_departure': 9, 
    'temp': 10, 
    'precip_total': 11, 'snowfall_total': 14, 
    'precip_total_normal': 12, 'snowfall_total_normal': 15, 
    'precip_total_departure': 13, 'snowfall_total_departure': 16, 
    'snowdepth_total': 17}


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

DAILY_VARIABLE_IDS_WN = ['temp_max', 'temp_min', 'temp_mean',
    'precip_total', 
    'snowfall_total']

# The limits of variable values
VALUE_LIMITS = {'temp_max': (-55.0, 55.0),
    'temp_mean': (-55.0, 55.0),
    'temp_min': (-55.0, 55.0),
    'precip_total': (0.0, 500.0),
    'snowfall_total': (0.0, 5000.0), 
    'snowdepth_total': (0.0, 25000.0)}

# The default element codes used to request data from the ACIS 
# system.
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


class Retriever(BaseProduct):

    name = 'StnData'

    def __check_qc(self, value):

        return '1'

    def __convert(self, converter, value):

        try:

            fvalue = float(value)
            fvalue = converter(fvalue)

        except:
            fvalue = value

        return fvalue

    def __date_str(self, date_component):

        dc_str = ''

        if date_component < 10:
            dc_str = '0' + str(date_component)

        else:
            dc_str = str(date_component)

        return dc_str

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

    def json_output(self):

        output = {'meta': {}, 'data': []}
        output['meta']['start_date'] = [str(self.sdt)]
        output['meta']['end_date'] = [str(self.edt)]
        output['meta']['utcoffsets'] = [self.utcoffset]
        output['meta']['station_ids'] = [self.station_id]
        output['meta']['frequency_ids'] = ['daily']
        output['meta']['variable_ids'] = DAILY_VARIABLE_IDS

        for i in self.data_list:

            row = copy.copy(i)
            row['rdt'] = str(row['rdt'])

            for j in DAILY_VARIABLE_IDS:

                value_dict = row.get(j, {})
                ext_dict = value_dict.get('extreme', {})
                ext_rdt = ext_dict.get('rdt', None)

                if ext_rdt is not None:
                    ext_dict['rdt'] = str(ext_dict['rdt'])

            output['data'].append(row)

        output = json.dumps(output)

        return output

    def post_process(self):

        r2 = self.response_data[1]
        r2smry = r2.get('smry', [[], []])

        ext = {}
        count = 0
        length = len(r2smry[0])

        while count < length:

            converter = lambda x: (x - 32.0) * (5.0 / 9.0)

            emaxt = self.__convert(converter, r2smry[0][count][0])
            emint = self.__convert(converter, r2smry[1][count][0])
            d_emaxt = datetime.datetime(int(r2smry[0][count][1][0:4]), 
                int(r2smry[0][count][1][5:7]), 
                int(r2smry[0][count][1][8:10]))
            d_emaxt = d_emaxt.replace(tzinfo = self.tzinfo).astimezone(utc)
            d_emint = datetime.datetime(int(r2smry[1][count][1][0:4]), 
                int(r2smry[1][count][1][5:7]), 
                int(r2smry[1][count][1][8:10]))
            d_emint = d_emint.replace(tzinfo = self.tzinfo).astimezone(utc)

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
        r1data = r1.get('data', [])

        for row in r1data:

            rdt = datetime.datetime(int(row[0][0:4]), 
                int(row[0][5:7]), 
                int(row[0][8:10]))
            rdt = rdt.replace(tzinfo = self.tzinfo)

            extremes = ext[rdt.strftime('%m-%d')]

            parsed_row = {}
            parsed_row['rdt'] = rdt

            for variable_id in DAILY_VARIABLE_IDS:

                index = COLUMN_INDICES.get(variable_id, None)
                converter = CONVERSIONS.get(variable_id, lambda x: x)
                value = self.__convert(converter, row[index])

                value_dict = {}
                value_dict['value'] = value
                value_dict['qc'] = self.__check_qc(value)

                if variable_id == 'temp_max':

                    ex = extremes['max']
                    value_dict['extreme'] = {}
                    value_dict['extreme']['rdt'] = ex[1]
                    value_dict['extreme']['value'] = ex[0]

                if variable_id == 'temp_min':

                    en = extremes['min']
                    value_dict['extreme'] = {}
                    value_dict['extreme']['rdt'] = en[1]
                    value_dict['extreme']['value'] = en[0]

                if variable_id in DAILY_VARIABLE_IDS_WN:

                    ni = COLUMN_INDICES.get(variable_id + '_normal', None)
                    nval = self.__convert(converter, row[ni])
                    value_dict['normal'] = nval

                    di = COLUMN_INDICES.get(variable_id + '_departure', None)
                    dval = self.__convert(converter, row[di])
                    value_dict['departure'] = dval

                parsed_row[variable_id] = value_dict

            self.data_dict[str('rdt')] = parsed_row
            self.data_list.append(parsed_row)

        return None

    def setup(self, *args, **kwargs):

        self.start_date = kwargs.get('start_date', DEFAULT_START_DATE)
        self.end_date = kwargs.get('end_date', DEFAULT_END_DATE)
        self.utcoffset = kwargs.get('utcoffset', None)
        self.station_id = kwargs.get('station_id', '')

        # These data structures will contain the rows of data as 
        # dictionaries.
        self.data_dict = {}
        self.data_list = []

        # Create the tzinfo offset for the rdt values inside the 
        # dictionaries stored in the data_dict and data_list 
        # data structures.
        self.tzinfo = SimpleOffset(self.utcoffset)

        # Here we will create the sdt and edt datetime attributes. 
        # These attributes are timezone aware datetime objects in 
        # UTC time.
        t = datetime.time(0)
        self.sdt = datetime.datetime.combine(self.start_date, t)
        self.sdt = self.sdt.replace(tzinfo = self.tzinfo).astimezone(utc)
        self.edt = datetime.datetime.combine(self.end_date, t)
        self.edt = self.edt.replace(tzinfo = self.tzinfo).astimezone(utc)

        return None


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
        help = 'the UTC offset of the given station in seconds')
    argparser.add_argument('station_id', 
        type = str, 
        help = 'the station ID')

    args = argparser.parse_args()
    start_date = args.start_date
    end_date = args.end_date
    utcoffset = args.utcoffset
    station_id = args.station_id

    retr = Retriever(start_date = start_date, 
        end_date = end_date, 
        utcoffset = utcoffset, 
        station_id = station_id)

    print retr.json_output()


