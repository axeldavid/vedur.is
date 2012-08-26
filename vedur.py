#!usr/bin/env python

import os, sys, urllib, datetime
from lxml import etree

class Weather(object):

    params = {
        "op_w" : "xml",
        "type" : "obs",
        "lang" : "is",
        "view" : "xml"
    }

    def __init__(self, ids="1", resolution=15, force_fetch=False):
        self.params["ids"] = str(ids)
        self.resolution = resolution
        self.url = r"http://xmlweather.vedur.is/?" + urllib.urlencode(self.params)
        self.xml = self.get_xmlobj(self._get_file_path(), force_fetch=force_fetch)
        self.location = self.get_node("name")
        self.temperature = self.get_node("T")
        self.wind = self.get_node("F")
        self.winddirection = self.get_node("D")
        self.weather = self.get_node("W")
        self.precipitation = self.get_node("R")

    def get_node(self, title, except_val="", xml=None):
        xml = self.xml if xml is None else xml
        result = xml.xpath("//observations/station/%s" % title)
        return result and result[0].text or except_val

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
            # TODO: Improve exception, raise error
            return ""

    def _save_xml(self, file_path, xml_str=""):
        if not xml_str:
            xml_str = self._fetch_xml()
        f = open(file_path, "w")
        f.write(xml_str)
        f.close()

    def _read_xml(self, file_path):
        if not os.path.exists(file_path):
            self._save_xml(file_path)
        f = open(file_path, "r")
        xml_str = f.read()
        f.close()
        return xml_str

    def get_xmlobj(self, file_path, force_fetch=False):
        xml_str = self._read_xml(file_path)
        xml = etree.fromstring(xml_str)
        date = datetime.datetime.strptime( self.get_node("time", xml=xml), "%Y-%m-%d %H:%M:%S" )
        if force_fetch or datetime.datetime.now() - date > datetime.timedelta(minutes=self.resolution):
            xml_str = self._fetch_xml()
            self._save_xml(file_path, xml_str=xml_str)
            xml = etree.fromstring(xml_str)
            date = datetime.datetime.strptime(self.get_node("time", xml=xml), "%Y-%m-%d %H:%M:%S")
        self.date = date
        return xml

def __main__():
    weather = Weather()
    args = sys.argv[1:]



if __name__ == "__main__":
    __main__()
