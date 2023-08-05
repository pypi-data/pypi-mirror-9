"""This is my "spider001.py" module and it provides one function called scrap_page() which prints data on website."""

import requests

def scrap_page(url):
    """This function takes one positianl argument called "url", which is url of the web page you want to scrap. And function will prints the page text."""
    page = requests.post(url)
    print(page.text)