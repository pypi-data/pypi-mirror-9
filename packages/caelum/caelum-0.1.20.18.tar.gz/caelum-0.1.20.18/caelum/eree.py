#!/usr/bin/env python
# Copyright (C) 2013 Nathan Charles
#
# This program is free software. See terms in LICENSE file.
"""Global EERE Weather Data Sources"""

import os
import csv
import zipfile
import tempfile
import datetime
from geopy import geocoders
import pytz
import re

#try:
#    from urllib.request import urlopen
#except ImportError:
import urllib2

WEATHER_DATA_PATH = os.environ['HOME'] + "/weather_data"
SRC_PATH = os.path.dirname(os.path.abspath(__file__))

DATA_EXTENTIONS = {'SWERA':'epw', \
        'CSWD':'epw', \
        'CWEC':'epw', \
        'ETMY':'epw', \
        'IGDG':'epw', \
        'IMGW':'epw', \
        'INETI':'epw', \
        'ISHRAE':'epw', \
        'ITMY':'epw', \
        'IWEC':'epw', \
        'KISR':'epw', \
        'MSI':'epw', \
        'NIWA':'epw', \
        'RMY':'epw', \
        'SWEC':'epw', \
        'TMY':'epw', \
        'TMY2':'epw', \
        'TMY3':'epw', \
        'IWEC':'epw', \
        'stat':'stat', \
        'ddy':'ddy'}

try:
    os.listdir(WEATHER_DATA_PATH)
except OSError:
    try:
        os.mkdir(WEATHER_DATA_PATH)
    except IOError:
        pass

def _muck_w_date(record):
    """muck with the date because EPW starts counting from 1 and goes to 24"""
    temp_d = datetime.datetime(int(record['Year']), int(record['Month']), \
            int(record['Day']), int(record['Hour'])%24, \
            int(record['Minute'])%60) #minute 60 is actually minute 0?
    d_off = int(record['Hour'])//24  #hour 24 is actually hour 0
    if d_off > 0:
        temp_d += datetime.timedelta(days=d_off)
    #print d, '%s-%s-%s %s:%s' % (record['Year'], record['Month'], \
    #record['Day'],record['Hour'],record['Minute'])
    return temp_d

def download(url):
    """download TMY3 file"""
    print("Downloading %s" % url)
    request = urllib2.Request(url)
    request.add_header('User-Agent', \
            'caelum/0.1 +https://github.com/nrcharles/caelum')
    #data_handle = urlopen(url)
    opener = urllib2.build_opener()
    with tempfile.TemporaryFile(suffix='.zip', dir=WEATHER_DATA_PATH) \
            as local_file:
        local_file.write(opener.open(request).read())
        compressed_file = zipfile.ZipFile(local_file, 'r')
        compressed_file.extractall(WEATHER_DATA_PATH)
        local_file.close()

def _eere_url(station_code):
    """build EERE EPW url for station code"""
    baseurl = 'http://apps1.eere.energy.gov/buildings/energyplus/weatherdata/'
    return baseurl + _station_info(station_code)['url']

def _station_info(station_code):
    """filename based meta data for a station code"""
    url_file = open(SRC_PATH + '/eree.csv')
    for line in csv.DictReader(url_file):
        if line['station_code'] == station_code:
            return  line
    raise KeyError('Station not found')


def _basename(station_code, fmt=None):
    "region, country, weather_station, station_code, data_format, url"
    info = _station_info(station_code)
    if not fmt:
        fmt = info['data_format']
    basename = '%s.%s' % (info['url'].rsplit('/', 1)[1].rsplit('.', 1)[0], \
            DATA_EXTENTIONS[fmt])
    print basename
    return basename

def twopercent(station_code):
    """two percent Temperature"""
    #(DB=>MWB) 2%, MaxDB=
    temp = None
    try:
        fin = open('%s/%s' % (WEATHER_DATA_PATH, \
                _basename(station_code, 'ddy')))
        for line in fin:
            value = re.search("""2%, MaxDB=(\\d+\\.\\d*)""", line)
            if value:
                temp = float(value.groups()[0])
    except IOError:
        pass

    if not temp:
        #(DB=>MWB) 2%, MaxDB=
        try:
            fin = open('%s/%s' % (WEATHER_DATA_PATH, \
                    _basename(station_code, 'stat')))
            flag = 0
            tdata = []
            for line in fin:
                if line.find('2%') is not -1:
                    flag = 3
                if flag > 0:
                    tdata.append(line.split('\t'))
                    flag -= 1
            temp = float(tdata[2][5].strip())
        except IOError:
            pass
    if temp:
        return temp
    else:
        print "Warning: 2% High Temperature not found, using worst case"
        return 38.0

def minimum(station_code):
    """minimum temperature"""
    #(DB=>MWB) 2%, MaxDB=
    temp = None
    fin = None
    try:
        fin = open('%s/%s' % (WEATHER_DATA_PATH, \
                _basename(station_code, 'ddy')))
    except IOError:
        print "File not found"
        print "Downloading ..."
        download(_eere_url(station_code))
        fin = open('%s/%s' % (WEATHER_DATA_PATH, \
                _basename(station_code, 'ddy')))
    for line in fin:
        value = re.search('Max Drybulb=(-?\\d+\\.\\d*)', line)
        if value:
            temp = float(value.groups()[0])
    if not temp:
        try:
            fin = open('%s/%s' % (WEATHER_DATA_PATH, \
                    _basename(station_code, 'stat')))
            for line in fin:
                if line.find('Minimum Dry Bulb') is not -1:
                    return float(line[37:-1].split('\xb0')[0])
        except IOError:
            pass
    if temp:
        return temp
    else:
        print "Warning: Minimum Temperature not found, using worst case"
        return -23.0

class EPWdata(object):
    """EPW weather generator"""
    def __init__(self, station_code, DST=False):
        #filename = path + station_code + 'TY.csv'
        filename = WEATHER_DATA_PATH + '/' + _basename(station_code)
        self.csvfile = None
        try:
            self.csvfile = open(filename)
        except IOError:
            print("File not found")
            download(_eere_url(station_code))
            self.csvfile = open(filename)
        fieldnames = ["Year", "Month", "Day", "Hour", "Minute", "DS", \
                "Dry-bulb (C)", "Dewpoint (C)", "Relative Humidity", \
                "Pressure (Pa)", "ETR (W/m^2)", "ETRN (W/m^2)", "HIR (W/m^2)", \
                "GHI (W/m^2)", "DNI (W/m^2)", "DHI (W/m^2)", "GHIL (lux)", \
                "DNIL (lux)", "DFIL (lux)", "Zlum (Cd/m2)", "Wdir (degrees)", \
                "Wspd (m/s)", "Ts cover", "O sky cover", "CeilHgt (m)", \
                "Present Weather", "Pw codes", "Pwat (cm)", "AOD (unitless)", \
                "Snow Depth (cm)", "Days since snowfall"]
        station_meta = self.csvfile.readline().split(',')
        self.station_name = station_meta[1]
        self.CC = station_meta[3]
        self.station_fmt = station_meta[4]
        self.station_code = station_meta[5]
        self.lat = station_meta[6]
        self.lon = station_meta[7]
        self.TZ = float(station_meta[8])
        self.ELEV = station_meta[9]
        self.DST = DST

        if self.DST:
            geocoder = geocoders.GoogleV3()
            self.local_tz = pytz.timezone(\
                    geocoder.timezone((self.lat, self.lon)).zone)
        dummy = ""
        for _ in range(7):
            dummy += self.csvfile.readline()
        self.epw_data = csv.DictReader(self.csvfile, fieldnames=fieldnames)

    def __iter__(self):
        return self

    def next(self):
        """generator handle"""
        record = self.epw_data.next()
        local_time = _muck_w_date(record)
        record['datetime'] = local_time
        #does this fix a specific data set or a general issue?
        if self.DST:
            localdt = self.local_tz.localize(record['datetime'])
            record['utc_datetime'] = localdt.astimezone(pytz.UTC)
        else:
            record['utc_datetime'] = \
                    local_time - datetime.timedelta(hours=self.TZ)

        return record
        #'LOCATION,BEEK,-,NLD,IWEC Data,063800,50.92,5.78,1.0,116.0'

    def __del__(self):
        self.csvfile.close()

if __name__ == '__main__':
    SCODE = '418830'
    STATION_CODE = '063800'
    PLACE = (52.443371, 5.628186)
    print sum([int(i['GHI (W/m^2)']) for i in EPWdata(STATION_CODE)])
    print sum([int(i['GHI (W/m^2)']) for i in EPWdata(STATION_CODE, False)])
    from solpy import irradiation
    tr = 10
    az = 180
    print sum([irradiation.irradiation(record=rec, place=PLACE, horizon=None, \
            t=tr, array_azimuth=az, model='p9') \
            for rec in EPWdata(STATION_CODE)])/1000
