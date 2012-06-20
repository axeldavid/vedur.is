#!usr/bin/env python

import os, sys, urllib, datetime
from lxml import etree

class Weather(object):

    params = {
        "op_w" : "xml",
        "type" : "obs",
        "lang" : "is",
        "view" : "xml",
        "ids" : "1"
    }
    force_fetch = False
    resolution = 15 #min

    url = ""
    file_path = ""
    xml = None
    location = ""
    date = None
    temperature = ""
    wind = ""
    winddirection = ""
    weather = ""
    precipitation = ""

    def __init__(self):
        self.url = r"http://xmlweather.vedur.is/?" + urllib.urlencode(self.params)
        self.file_path = self._get_file_path()
        self.xml = self.get_xmlobj()
        self.location = self.get_node("name")
        self.temperature = self.get_node("T")
        self.wind = self.get_node("F")
        self.winddirection = self.get_node("D")
        self.weather = self.get_node("W")
        self.precipitation = self.get_node("R")

    def get_node(self, title):
        result = self.xml.xpath("//observations/station/" + title)
        if result:
            return result[0].text
        return ""

    def _get_file_path(self):
        file_path = os.path.join( os.getenv("HOME"), ".temp", "weather.xml" )
        dirname = os.path.dirname(file_path)
        if not os.path.exists(dirname):
            os.makedirs(dirname)
        return file_path

    def _fetch_xml(self):
        try:
            return urllib.urlopen(self.url).read()
        except:
            return ""

    def _save_xml(self, xml_str=""):
        if not xml_str:
            xml_str = self._fetch_xml()
        f = open(self.file_path, "w")
        f.write(xml_str)
        f.close()

    def _read_xml(self):
        if not os.path.exists(self.file_path):
            self._save_xml()
        f = open(self.file_path, "r")
        xml_str = f.read()
        f.close()
        return xml_str

    def get_xmlobj(self):
        xml = etree.fromstring(self._read_xml())
        date = datetime.datetime.strptime( xml.xpath("//observations/station/time")[0].text, "%Y-%m-%d %H:%M:%S" )
        if datetime.datetime.now() - date > datetime.timedelta(minutes=self.resolution) or self.force_fetch:
            xml_str = self._fetch_xml()
            self._save_xml(xml_str=xml_str)
            xml = etree.fromstring(xml_str)
            date = datetime.datetime.strptime( xml.xpath("//observations/station/time")[0].text, "%Y-%m-%d %H:%M:%S" )
        self.date = date
        return xml

def __main__():
    weather = Weather()
    args = sys.argv[1:]



if __name__ == "__main__":
    __main__()
