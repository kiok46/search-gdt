# search-gdt
Search for Google, DuckDuckgo and Twitter using a single search query.


### How to run?

Get Search API keys of Google, Twitter and DuckDuckGo. and update them in the config_ext.py file

```
# Google url

google_search_url = "https://www.googleapis.com/customsearch/v1?key={}&cx={}&q={}"
google_api_key = ""
google_cx = ""

# DuckDuckGo urls

duckduckgo_base_url = "http://api.duckduckgo.com/?q={}&format=json"

# Twitter urls

twitter_customer_key = ""
twitter_secrey_key = ""
twitter_access_token = ""
twitter_access_secret_key = ""
```

After you are done.

Open terminal, cd to the folder and type the following commands.
```
virtualenv venv
source venv/bin/activate
pip3 install -r requirements.txt
python3 app.py
```

This is what you should see.

![ScreenShot](https://raw.github.com/kiok46/search-gdt/master/screenshots/screenshot.png)
