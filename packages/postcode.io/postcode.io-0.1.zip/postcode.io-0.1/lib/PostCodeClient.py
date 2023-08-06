__author__ = 'gokhan'
import requests


class PostCodeClient(object):
    def getLookupPostCode(self, postcode):
        self.postcode = postcode
        data = requests.get("http://api.lib.io/lib/" + postcode).text
        return data


    def getLookupPostcodes(self, payload):
        self.payload = payload
        data = requests.post("http://api.lib.io/lib", payload).text
        return data


    def getLocationBasedPostcodes(self, lon, lang):
        self.long = lon
        self.lang = lang

        data = requests.get("http://api.lib.io/lib?lon=" + lon + "&lat=" + lang).text
        return data


    def getBulkReverseGecoding(self, payload):
        self.payload = payload
        data = requests.post("http://api.lib.io/lib", payload).text
        return data


    def getRandomPostCodes(self):
        data = requests.get("http://api.lib.io/random/lib").text
        return data

    def validatePostCode(self, postcode):
        self.postcode = postcode
        data = requests.get("http://api.lib.io/lib/" + postcode + "/validate").text
        return data

    def getNearestPostCode(self, postcode):
        self.postcode = postcode
        data = requests.get("http://api.lib.io/lib/" + postcode + "/nearest").text
        return data