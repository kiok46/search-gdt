"""
KULDEEP SINGH
"""

from flask import Flask, request, g, render_template, Response, jsonify
from flask import session, flash, redirect, url_for, make_response
from flask_restful import Resource, Api
import json
import urllib
import requests
import config_ext
import asyncio
import sys
import time
from twitter import *


app = Flask(__name__)
api = Api(app)


twitter_search = Twitter(
    auth=OAuth(config_ext.twitter_access_token,
               config_ext.twitter_access_secret_key,
               config_ext.twitter_customer_key,
               config_ext.twitter_secrey_key))


@app.route('/')
def index():
    '''
    Entry point.
    '''
    return render_template("index.html")


async def async_google_search(search_string, search_url, timeout):
    '''
    Async google search api.
    Returns the url, response time of the google custom search api and the
    text of the first tweet from the response.

    params:
        - search_string
        type: string

        - search_url
        type: string
    '''
    
    google_api_result = {}
    start = time.time()
    google_api_response = requests.get(config_ext.google_search_url.format(config_ext.google_api_key,
                                                                           config_ext.google_cx,
                                                                           search_string))
    end = time.time()
    if end-start > timeout:
        return False
    google_response = json.loads(google_api_response.text)
    try:
        google_api_result['text'] = google_response.get('items')[0].get('title')
    except:
        google_api_result['text'] = "No valid response from google api," + \
                                    " status code: {}".format(google_api_response.status_code)
    google_api_result['url'] = search_url
    
    google_api_result['response_time'] = str(end-start)
    return google_api_result


async def async_duckduckgo_search(search_string, search_url, timeout):
    '''
    Async duckduckgo search api.
    Returns the url, response time of the duckduckgo open api and the text of the first
    tweet from the response.

    params:
        - search_string
        type: string

        - search_url
        type: string
    '''
    
    duckduckgo_api_result = {}
    start = time.time()
    duckduckgo_api_response = requests.get(config_ext.duckduckgo_base_url.format(search_string))
    end = time.time()
    if end-start > timeout:
        return False
    duckduckgo_response = json.loads(duckduckgo_api_response.text)
    try:
        duckduckgo_api_result['text'] = duckduckgo_response.get('RelatedTopics')[0].get('Text')
    except:
        duckduckgo_api_result['text'] = "No valid response from duckduckgo api."
    duckduckgo_api_result['url'] = search_url
    
    duckduckgo_api_result['response_time'] = str(end-start)
    
    return duckduckgo_api_result


async def async_twitter_search(search_string, search_url, timeout):
    '''
    Async twitter search api.
    Returns the url, response time of the twitter api and the text of the first
    tweet from the response.

    params:
        - search_string
        type: string

        - search_url
        type: string
    '''
    twitter_api_result = {}
    start = time.time()
    twitter_response = twitter_search.search.tweets(q=urllib.parse.quote(search_string), count=100)
    end = time.time()
    if end-start > timeout:
        return False

    try:
        twitter_api_result['text'] = twitter_response['statuses'][0]['text']
    except:
        twitter_api_result['text'] = "No valid response from twitter api."

    twitter_api_result['url'] = search_url
    twitter_api_result['response_time'] = str(end-start)
    return twitter_api_result


def common_async_search(search_string, *args):
    '''
    Common async search for google, duckduckgo and twitter.
    '''

    results = {}
    search_result = {}

    search_url = "https://search-gdt.herokuapp.com/search/{}".format(search_string)
    event_loop = asyncio.get_event_loop()
    try:
        timeout = 1.5
        task_duckduckgo = event_loop.create_task(async_duckduckgo_search(search_string=search_string,
                                                                         search_url=search_url,
                                                                         timeout=timeout))
        task_google = event_loop.create_task(async_google_search(search_string=search_string,
                                                                 search_url=search_url,
                                                                 timeout=timeout))
        task_twitter = event_loop.create_task(async_twitter_search(search_string=search_string,
                                                                   search_url=search_url,
                                                                   timeout=timeout))

        event_loop.run_until_complete(task_duckduckgo)
        event_loop.run_until_complete(task_google)
        event_loop.run_until_complete(task_twitter)

    finally:
        #event_loop.run_forever()
        asyncio.set_event_loop(asyncio.new_event_loop())

    duckduckgo_api_result = task_duckduckgo.result()
    google_api_result = task_google.result()
    twitter_api_result = task_twitter.result()

    error_report = ''

    if not duckduckgo_api_result:
        error_report+= "DuckGuckGo "

    if not google_api_result:
        error_report+= "Google "

    if not twitter_api_result:
        error_report+= "Twitter "

    if error_report:
        return render_template("time_limit_exceded.html",
                               error_report=error_report,
                               timeout=timeout)


    results['google'] = google_api_result
    results['twitter'] = twitter_api_result
    results['duckduckgo'] = duckduckgo_api_result

    search_result['querry'] = search_string
    search_result['results'] = results

    results_json = json.dumps(search_result, indent=4)
    return Response(results_json,
                    mimetype="application/json"
                    )


@app.errorhandler(404)
def not_found(error):
    '''
    Handles if 404 occurs.
    '''
    return render_template("404.html")


class SearchGDT(Resource):

    def get(self, search_string):
        return common_async_search(search_string)


@app.route('/result', methods=['GET', 'POST'])
def result():
    '''
    This function returns in json format of the search result.
    '''
    if request.method == 'POST':
        search_string = request.form['search-string']
        return common_async_search(search_string)

    return render_template("index.html")


api.add_resource(SearchGDT, '/api/search/<search_string>')


if __name__ == "__main__":
    app.run()
