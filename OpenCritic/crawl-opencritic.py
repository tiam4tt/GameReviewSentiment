import requests
from bs4 import BeautifulSoup
import pandas as pd
import xml.etree.ElementTree as ET
import re

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

        filtered_game_links = [link for link in game_links if "/media" not in link and "/reviews" not in link]

        return filtered_game_links
    else:
        print(f"Could not retrieve sitemap: {sitemap_link}. Status code: {response.status_code}")
        return []

def parse_game_page(url):
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        title = soup.find('h1', class_='my-2 my-md-4').get_text(strip=True) if soup.find('h1', class_='my-2 my-md-4') else "n/a"
        
        genre_tag = soup.find(text="Genre")
        genre = genre_tag.find_next().get_text(strip=True) if genre_tag else "n/a"
        
        pricing_tag = soup.find(text="Price")
        pricing = pricing_tag.find_next().get_text(strip=True) if pricing_tag else "n/a"
        
        library_size_tag = soup.find(text="Storage")
        library_size = library_size_tag.find_next().get_text(strip=True) if library_size_tag else "n/a"
        
        companies = soup.find('div', {'class': 'companies'})
        publisher_tag = companies.find_all('span') if companies else None
        publisher = [tag.get_text(strip=True) for tag in publisher_tag] if publisher_tag else "n/a"
        
        platform_div = soup.find('div', {'class': 'platforms'})
        platform_tag = platform_div.find_all('span') if platform_div else None
        platform = [tag.get_text(strip=True) for tag in platform_tag] if platform_tag else "n/a"
        
        release_date = "n/a"
        
        if platform_div and "Release Date:" in platform_div.get_text():
            release_text = platform_div.get_text(strip=True).replace("Release Date:", "").strip()
            release_date = release_text.split('-')[0].strip()
        
        rating_tag = soup.find('div', class_="inner-orb")
        rating = rating_tag.get_text(strip=True) if rating_tag else "n/a"
        
        reviews_tag = soup.find('a', href=lambda href: href and "/reviews" in href)
        if reviews_tag:
            match = re.search(r'\d+', reviews_tag.get_text())
            num_reviews = int(match.group()) if match else "n/a"
        else:
            num_reviews = "n/a"
        
        return {
            "Game Title": title,
            "Game Genre": genre,
            "Pricing": pricing,
            "Game Library Size": library_size,
            "Publisher": publisher,
            "Release Date": release_date,
            "Platform": platform,
            "Rating": rating,
            "Number of Rating": num_reviews
        }
    
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from {url}: {e}")
        return None

sitemap_links = get_sitemap_links(sitemap_url)

game_links = get_game_links_from_sitemap(sitemap_links[0])

games_data = []

for link in game_links:
    game_data = parse_game_page(link)
    if game_data and game_data['Game Title'] != "n/a":  
        games_data.append(game_data)
        
df_games = pd.DataFrame(games_data)

df_games = df_games.dropna(how='all')

df_games.to_csv('game_data.csv', index=False, encoding='utf-8')

print(df_games)
