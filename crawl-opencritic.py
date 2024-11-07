import requests
from bs4 import BeautifulSoup
import pandas as pd
import xml.etree.ElementTree as ET

sitemap_url = 'https://opencritic.com/sitemap.xml'

def get_sitemap_links(sitemap_url):
    response = requests.get(sitemap_url)
    if response.status_code == 200:
        root = ET.fromstring(response.content)
        namespaces = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
        sitemap_links = [elem.text for elem in root.findall('.//ns:loc', namespaces) if 'sitemap_games' in elem.text]
        return sitemap_links
    else:
        print(f"Could not retrieve sitemap. Status code: {response.status_code}")
        return []

def get_game_links_from_sitemap(sitemap_link):
    response = requests.get(sitemap_link)
    if response.status_code == 200:
        root = ET.fromstring(response.content)
        namespaces = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
        game_links = [elem.text for elem in root.findall('.//ns:loc', namespaces)]
        return game_links  # Trả về tất cả các liên kết game
    else:
        print(f"Could not retrieve sitemap: {sitemap_link}. Status code: {response.status_code}")
        return []
