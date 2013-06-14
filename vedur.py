#!usr/bin/env python

import datetime
import os
import urllib
from lxml import etree


class Weather(object):

    """
        This is a simple python interface to get weather information form
        vedur.is

        PARAMETERS:
        ids             The default weather station is in Reykjavik and can be
                        set with this parameter. More stations can be found at
                        http://www.vedur.is/vedur/stodvar

        resolution:     Caching time (minutes). Default is 15 minutes.

        force_fetch:    Nothing will be read from cache if this is set to True

        cache:          No data will be saved if this is set to False.
    """

    params = {
        "op_w": "xml",
        "type": "obs",
        "view": "xml"
    }

    date = None
    location = ""
    temperature = ""
    wind = ""
    winddirection = ""
    weather = ""
    precipitaion = ""
    max_wind = ""
    max_blast = ""

    def __init__(self, ids="1", resolution=15, force_fetch=False, cache=True,
                 lang='is'):
        self.params.update({
            'ids': str(ids),
            'lang': lang
        })
        self.resolution = int(resolution)
        self.url = r"http://xmlweather.vedur.is/?%s" % urllib.urlencode(self.params)
        self.xml = self.get_xmlobj(force_fetch=force_fetch, cache=cache)
        if self.xml is not None:
            self.location = self.get_node("name")
            self.temperature = self.get_node("T")
            self.wind = self.get_node("F")
            self.winddirection = self.get_node("D")
            self.weather = self.get_node("W")
            self.precipitation = self.get_node("R")
            self.max_wind = self.get_node("FX")
            self.max_blast = self.get_node("FG")
            self.date = self._get_date(self.xml)

    def get_node(self, title, except_val="", xml=None):
        xml = self.xml if xml is None else xml
        result = xml.xpath("//observations/station/%s" % title)
        return result and result[0].text or except_val

    def _get_file_path(self):
        file_path = os.path.join(os.getenv("HOME"), ".vedur", "vedur.xml")
        dirname = os.path.dirname(file_path)
        if not os.path.exists(dirname):
            os.makedirs(dirname)
        return file_path

    def fetch_xml(self):
        try:
            return urllib.urlopen(self.url).read()
        except:
            # TODO: Improve exception, raise error
            return ""

    def save_xml(self, file_path, xml_str):
        f = open(file_path, "w")
        f.write(xml_str)
        f.close()

    def read_xml(self, file_path):
        f = open(file_path, "r")
        xml_str = f.read()
        f.close()
        return xml_str

    def _get_date(self, xml):
        date_str = self.get_node("time", xml=xml)
        return datetime.datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")

    def _update_weather(self, xml_str):
        xml = etree.fromstring(xml_str)
        self.date = self._get_date(xml)
        if datetime.datetime.now() - self.date > datetime.timedelta(minutes=self.resolution):
            xml_str = self.fetch_xml()
            xml = etree.fromstring(xml_str)
            self.date = self._get_date(xml)
        return xml_str, xml

    def get_xmlobj(self, force_fetch=False, cache=True):
        xml = None
        if cache or not force_fetch:
            file_path = self._get_file_path()
        if not force_fetch and os.path.exists(file_path):
            xml_str = self.read_xml(file_path)
            if xml_str:
                xml_str, xml = self._update_weather(self.read_xml(file_path))
        else:
            xml_str = self.fetch_xml()
            if xml_str:
                xml = etree.fromstring(xml_str)

        if xml_str and cache:
            self.save_xml(file_path, xml_str)
        return xml


def __main__():
    w = Weather()
    weather = u"The temperature in %s is %s celsius degrees"
    print weather % (w.location, w.temperature)

if __name__ == "__main__":
    __main__()
