from flask import Flask, request, g, render_template, Response
from flask import session, flash, redirect, url_for, make_response
import json
import urllib
import requests
import config_ext
import asyncio
import aiohttp
import sys
from twitter import *


app = Flask(__name__)


twitter_search = Twitter(
    auth=OAuth(config_ext.twitter_access_token,
               config_ext.twitter_access_secret_key,
               config_ext.twitter_customer_key,
               config_ext.twitter_secrey_key))


@app.route('/')
def index():
    return render_template("index.html")


async def async_google_search(search_string, search_url):
    try:
        google_api_result = {}
        google_api_response = requests.get(config_ext.google_search_url.format(config_ext.google_api_key,
                                                                           config_ext.google_cx,
                                                                           search_string))
        google_response = json.loads(google_api_response.text)
        try:
            google_api_result['text'] = google_response.get('items')[0].get('title')
        except:
            google_api_result['text'] = "No valid response from google api."
        google_api_result['url'] = search_url
        return google_api_result
    except:
        raise Exception("Error from google api")


async def async_duckduckgo_search(search_string, search_url):
    try:
        duckduckgo_api_result = {}
        duckduckgo_api_response = requests.get(config_ext.duckduckgo_base_url.format(search_string))

        duckduckgo_response = json.loads(duckduckgo_api_response.text)
        try:
            duckduckgo_api_result['text'] = duckduckgo_response.get('RelatedTopics')[0].get('Text')
        except:
            duckduckgo_api_result['text'] = "No valid response from duckduckgo api."
        duckduckgo_api_result['url'] = search_url
        return duckduckgo_api_result
    except:
        raise Exception("Error from duckduckgo api")


async def async_twitter_search(search_string, search_url):
    try:
        twitter_api_result = {}
        if sys.version_info[0] == 3:
            twitter_response = twitter_search.search.tweets(q=urllib.parse.quote(search_string), count=100)
        else:
            twitter_response = twitter_search.search.tweets(q=urllib.quote(search_string), count=100)

        try:
            twitter_api_result['text'] = twitter_response['statuses'][0]['text']
        except:
            twitter_api_result['text'] = "No valid response from twitter api."

        twitter_api_result['url'] = search_url

        return twitter_api_result
    except:
        raise Exception("Error from twitter api")


def common_async_search(search_string, *args):
    """
    Common async search for google, duckduckgo and twitter.
    """

    results = {}
    search_result = {}

    search_url = "https://search-gdt.herokuapp.com?q={}".format(search_string)
    
    try:
        event_loop = asyncio.get_event_loop()
        task_duckduckgo = event_loop.create_task(async_duckduckgo_search(search_string=search_string,
                                                                         search_url=search_url))
        task_google = event_loop.create_task(async_google_search(search_string=search_string,
                                                                 search_url=search_url))
        task_twitter = event_loop.create_task(async_twitter_search(search_string=search_string,
                                                                   search_url=search_url))
        event_loop.run_until_complete(task_duckduckgo)
        event_loop.run_until_complete(task_google)
        event_loop.run_until_complete(task_twitter)
    finally:
        pass
        #event_loop.close()

    duckduckgo_api_result = task_duckduckgo.result()
    google_api_result = task_google.result()
    twitter_api_result = task_twitter.result()

    results['google'] = google_api_result
    results['twitter'] = twitter_api_result
    results['duckduckgo'] = duckduckgo_api_result

    search_result['querry'] = search_string
    search_result['results'] = results

    results_json = json.dumps(search_result, indent=4)
    return Response(results_json,
                    mimetype="application/json"
                    )


@app.route('/search/<search_string>', methods=['GET', 'POST'])
def search_gdt(search_string):
    if request.method == 'GET':
        return common_async_search(search_string)

    return render_template("index.html")


@app.route('/result', methods=['GET', 'POST'])
def result():
    if request.method == 'POST':
        search_string = request.form['search-string']
        return common_async_search(search_string)

    return render_template("index.html")


if __name__ == "__main__":
    app.run(port=4000)
