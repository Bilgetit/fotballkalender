import pandas as pd
from bs4 import BeautifulSoup
import requests
from datetime import datetime
import os

username = os.environ.get('USERNAME')
password = os.environ.get('PASSWORD')
# print(username, password)

response = requests.get("https://www.altomfotball.no/elementsCommonAjax.do?cmd=fixturesContent&seasonId=344&teamId=732&month=all&useFullUrl=false")
# response = requests.get("https://www.altomfotball.no/elementsCommonAjax.do?cmd=fixturesContent&tournamentId=230&month=all&useFullUrl=false")
if response.status_code != 200:
	print("Error fetching page")
	exit()
else:
	content = response.content
soup = BeautifulSoup(response.content, 'html.parser')


# nb_links = len(soup.find_all('a'))
# print(soup.get_text())
# all_dates = soup.select('td:nth-child(1) > span:nth-child(1)')

all_dates = soup.select('td:nth-child(1) > span')
dates = [r.text.split(' ')[0] for r in all_dates]
dates = [datetime.strptime(r, '%d.%m.%Y') for r in dates]
# print(dates)

all_home = soup.select('td:nth-child(4) > a ')
home = [r.text.split(' ')[0].strip() for r in all_home]
# print(home)

all_times = soup.select('td:nth-child(5) > a ')
times = [r.text.split(' ')[0].strip() for r in all_times] 
# print(times)

all_away = soup.select('td:nth-child(6) > a ')
away = [r.text.split(' ')[0].strip() for r in all_away]
# print(away)

all_channels = soup.select('td:nth-child(7) ')
channels = [' '.join(r.text.split(' ')) for r in all_channels]
# print(channels)

data = pd.DataFrame()
data['Date'] = dates
data['Home'] = home
data['Time'] = times
data['Away'] = away
data['Channel'] = channels

print(data)

