#!/usr/bin/env python
from urllib.request import FancyURLopener
import urllib.request
import simplejson


"""
Class: ImagineOpener
Description: Customized URL opener.
"""


class ImagineOpener(FancyURLopener):
    version = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; it; rv:1.8.1.11) Gecko/20071127 Firefox/2.0.0.11'


"""
Class: Imagine
Description: Given a query, download the first n images from Google.
Params: String query, int n (default=1)
"""


class Imagine:
    def __init__(self, query, n=1):
        self.query = query.replace(' ', "%20")
        self.n = n

    def execute(self):
        opener = ImagineOpener()
        url = ('https://ajax.googleapis.com/ajax/services/search/images?' + 'v=1.0&q=' + self.query
               + '&start=0&userip=188.79.132.104')

        print("(debug)\t\tFetching URL:\t" + url)
        request = urllib.request.Request(url, None, {'Referer': 'testing'})
        response = urllib.request.urlopen(request)

        # Parse JSON data
        results = simplejson.load(response)
        data = results["responseData"]
        data_info = data["results"]

        # Start loop in case several results are wanted
        k = 1  # Counter
        while k <= self.n:
            match = data_info[k]["unescapedUrl"]
            print("(debug)\t\tBest match URL (" + str(k) + "):\t" + match)

            # Save image
            opener.retrieve(match, "cover-" + str(k) + ".jpg")
            k += 1

