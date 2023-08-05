"""This is my "spider001.py" module and it provides one function called scrap_page() which scrap all data on the web page."""

import requests

def scrap_page(url, data={}):
    """This function takes two positional arguments. First one called "url", which is the url of that web page you want to scrap. The second arguments named "data", which has a default value equal empty dictionary. The second one is optional. And this function will generate a new file called web_page.html which contain all scraped data."""
    if data == {}:
        page = requests.get(url)
    else:
        page = requests.post(url, data)
    newfile = open("web_page.html", "w")
    newfile.write(page.text)
    newfile.close()
