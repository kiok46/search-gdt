import os
import unittest
import tempfile
import requests
import urllib
from twitter import *

from os import sys, path
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
import config_ext

class SearchGDTTestCase(unittest.TestCase):

    def test_google_request(self):
        search_string = "test"
        google_api_response = requests.get(config_ext.google_search_url.format(config_ext.google_api_key,
                                                                               config_ext.google_cx,
                                                                               search_string))

    def test_duckduckgo_request(self):
        search_string = "test"
        duckduckgo_api_response = requests.get(config_ext.duckduckgo_base_url.format(search_string))

    def test_twitter_request(self):
        twitter_search = Twitter(
            auth=OAuth(config_ext.twitter_access_token,
                       config_ext.twitter_access_secret_key,
                       config_ext.twitter_customer_key,
                       config_ext.twitter_secrey_key))
        search_string = "test"
        twitter_response = twitter_search.search.tweets(q=urllib.parse.quote(search_string), count=100)


if __name__ == '__main__':
    unittest.main()