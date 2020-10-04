import urllib
import urllib.request
import time
import pandas as pd
import os
import requests

from bs4 import BeautifulSoup
from datetime import datetime

steampage = BeautifulSoup(urllib.request.urlopen('http://store.steampowered.com/stats/?l=english').read())

top100CSV = open('SteamTop100.csv', 'a')

for row in steampage('tr', {'class': 'player_count_row'}):
    steamAppID = row.a.get('href').split("/")[4]
    steamGameName = row.a.get_text().encode('utf-8')
    currentConcurrent = row.find_all('span')[0].get_text()
    maxConcurrent = row.find_all('span')[1].get_text()

    top100CSV.write('{0},{1},"{2}","{3}","{4}"\n'.format(currentTime, steamAppID, steamGameName, currentConcurrent, maxConcurrent))

top100CSV.close()
header_list = ["currentTime", "steamAppID", "steamGameName", "currentConcurrent", "maxConcurrent"]
df = pd.read_csv('SteamTop100.csv', names=header_list)
df.head(100)
col_one_list = df.head(100)['steamAppID'].tolist()

# please make a folder on your drive named game_headers and it will download the header to that location

save_location = "game_headers"

base_url = "http://store.steampowered.com/api/appdetails/?appids=%s&filters=basic"

header_images = []
full_path = os.path.abspath(save_location)

for x in col_one_list:
    r = requests.get(base_url % (x)).json()
    try:
        header_images.append((x, r[str(x)]['data']['header_image']))
    except KeyError:
        print("AppID {} => Did not return data".format(x))

# Download the images

for i in header_images:
    print("Downloading header image for AppID {}".format(i[0]))
    r = requests.get(i[1], stream=True)
    if r.status_code == 200:
        with open(os.path.join(full_path, "{}_header.jpg".format(str(i[0]))), 'wb') as f:
            for chunk in r.iter_content():
                f.write(chunk)