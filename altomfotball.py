import os
from dotenv import load_dotenv
import smtplib
import ssl
import pandas as pd
import requests
import datetime as dt
import schedule
import time
from bs4 import BeautifulSoup
from email.message import EmailMessage

load_dotenv(".env")

email_sender = os.environ.get('USERNAME')
email_password = os.environ.get('PASSWORD')
email_receiver = 'm.gjestrud@gmail.com'

# response = requests.get("https://www.altomfotball.no/elementsCommonAjax.do?cmd=fixturesContent&seasonId=344&teamId=732&month=all&useFullUrl=false")
response = requests.get("https://www.altomfotball.no/elementsCommonAjax.do?cmd=fixturesContent&tournamentId=230&month=all&useFullUrl=false")
if response.status_code != 200:
	print("Error fetching page")
	exit()
else:
	content = response.content
soup = BeautifulSoup(response.content, 'html.parser')

all_dates = soup.select('td:nth-child(1) > span')
def format_dates(all_dates):
	dates = []
	current = None

	for r in all_dates:	
		try:
			dates.append(dt.datetime.strptime(r.text.split(' ')[0], '%d.%m.%Y'))
			current = r.text.split(' ')[0]
		except:
			dates.append(dt.datetime.strptime(current, '%d.%m.%Y'))
	return dates
dates = format_dates(all_dates)

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

# print(data)

def get_week():
	week = pd.DataFrame()
	for i in range(len(data)):
		if data['Date'][i] >= dt.datetime.date(dt.datetime.now()) and data['Date'][i] <= dt.datetime.date(dt.datetime.now() + dt.timedelta(days=14)):
			week = week.append(data.iloc[i])
	week = week.reset_index(drop=True)
	return week
week = get_week()
# print(week)

def get_aston_villa(week):
	av = pd.DataFrame()
	astonvilla = 'Aston' + chr(160) + 'Villa'  # For some reason the name is Aston + non-breaking space + Villa
	
	for i in range(len(week)):
		if week['Home'][i] == astonvilla or week['Away'][i] == astonvilla:
			av = av.append(week.iloc[i])
	av = av.reset_index(drop=True)
	return av
av = get_aston_villa(week)
# print(av)

def get_free(week):
	free = pd.DataFrame()
	for i in range(len(week)):
		if week['Channel'][i] == 'TV3+':
			free = free.append(week.iloc[i])
	free = free.reset_index(drop=True)
	return free
free = get_free(week)
# print(free)


def send_email(email_receiver, subject, body):
	em = EmailMessage()
	em['From'] = email_sender
	em['To'] = email_receiver
	em['Subject'] = subject
	em.set_content(body)

	context = ssl.create_default_context()

	with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
		smtp.login(email_sender, email_password)
		smtp.sendmail(email_sender, email_receiver, em.as_string())




subject = 'Ukens kamper'
body = f"""
Her er ukens kamper for Aston Villa:

{av}

Ukens kamper på TV3+:

{free}

"""
# print(body)

no_games = """
Det er ingen kamper denne uken.
"""

av_games = f"""
Her er ukens kamper for Aston Villa:

{av}
"""

free_games = f"""
Ukens kamper på TV3+:

{free}
"""

# if len(av) == 0 and len(free) == 0:
# 	send_email(email_receiver, subject, no_games)

# elif len(free) == 0:
# 	send_email(email_receiver, subject, av_games)

# elif len(av) == 0:
# 	send_email(email_receiver, subject, free_games)

# else:
# 	send_email(email_receiver, subject, body)