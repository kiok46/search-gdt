from flask import Flask, request, g, render_template, Response
from flask import session, flash, redirect, url_for, make_response
import json
import urllib
import requests
import duckduckgo
import config_ext
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


def common_async_search(search_string, *args):
    """
    Common async search for google, duckduckgo and twitter.
    """
    google_api_result = {}
    twitter_api_result = {}
    duckduckgo_api_result = {} 
    results = {}
    search_result = {}

    # Google API Response
    google_response = requests.get(config_ext.google_search_url.format(config_ext.google_api_key,
                                                                       config_ext.google_cx,
                                                                       search_string))
    # Duck Duck Go API response
    duckduckgo_response = duckduckgo.query(search_string)

    # Twitter API response
    twitter_response = twitter_search.search.tweets(q=urllib.quote(search_string), count=100)

    # Loading google_response
    data = json.loads(google_response.text)
    search_url = "https://search-gdt.herokuapp.com?q={}".format(search_string)
    google_api_result['url'] = search_url
    twitter_api_result['url'] = search_url
    duckduckgo_api_result['url'] = search_url

    google_api_result['text'] = data['items'][0]['title']
    twitter_api_result['text'] = twitter_response['statuses'][0]['text']
    duckduckgo_api_result['text'] = duckduckgo_response.related[0].text

    results['google'] = google_api_result
    results['twitter'] = twitter_api_result
    results['duckduckgo'] = duckduckgo_api_result

    search_result['querry'] = search_string
    search_result['results'] = results

    results_json = json.dumps(search_result, indent=4)
    return Response(results_json,
                    mimetype="application/json"
                    )

    #return render_template('result.html', search_result=search_result)


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
    app.run()
