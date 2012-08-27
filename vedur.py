#!usr/bin/env python

import os, sys, urllib, datetime
from lxml import etree

class Weather(object):
    
    """
        This is a simple python interface to get weather information form vedur.is
        
        PARAMETERS:
        ids             The default weather station is in Reykjavik and can be set with
                        this parameter. More stations can be found at
                        http://www.vedur.is/vedur/stodvar

        resolution:     Caching time (minutes). Default is 15 minutes.
    """

    params = {
        "op_w" : "xml",
        "type" : "obs",
        "lang" : "is",
        "view" : "xml"
    }

    def __init__(self, ids="1", resolution=15, force_fetch=False, cache=True):
        self.params["ids"] = str(ids)
        self.resolution = int(resolution)
        self.url = r"http://xmlweather.vedur.is/?" + urllib.urlencode(self.params)
        self.xml = self.get_xmlobj(force_fetch=force_fetch, cache=cache)
        if self.xml is not None:
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
        file_path = os.path.join( os.getenv("HOME"), ".vedur", "vedur.xml" )
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

    def _update_weather(self, xml_str):
        xml = etree.fromstring(xml_str)
        date = datetime.datetime.strptime( self.get_node("time", xml=xml), "%Y-%m-%d %H:%M:%S" )
        if datetime.datetime.now() - date > datetime.timedelta(minutes=self.resolution):
            xml_str = self.fetch_xml()
            xml = etree.fromstring(xml_str)
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
    weather = Weather()
    args = sys.argv[1:]


if __name__ == "__main__":
    __main__()
