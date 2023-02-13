import os
from dotenv import load_dotenv
import smtplib
import ssl
import pandas as pd
import requests
import datetime as dt
from bs4 import BeautifulSoup
from email.message import EmailMessage

load_dotenv("Documents/Prosjekter/fotballkalender/.env")

email_sender = os.environ.get('USERNAME')
email_password = os.environ.get('PASSWORD')
email_receiver = 'm.gjestrud@gmail.com'

# from decouple import config

# username = config('USERNAME', default='')
# password = config('PASSQORD', default='')

# print(email_sender, email_password)

# response = requests.get("https://www.altomfotball.no/elementsCommonAjax.do?cmd=fixturesContent&seasonId=344&teamId=732&month=all&useFullUrl=false")

def cook(link):
	response = requests.get(link)
	if response.status_code != 200:
		print("Error fetching page")
		exit()
	else:
		content = response.content
	soup = BeautifulSoup(response.content, 'html.parser')
	return soup

team1 = cook("https://www.altomfotball.no/elementsCommonAjax.do?cmd=fixturesContent&tournamentId=230&month=all&useFullUrl=false")
team2 = cook("https://www.altomfotball.no/elementsCommonAjax.do?cmd=fixturesContent&seasonId=344&teamId=1182&month=all&useFullUrl=false")


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

team1_dates = team1.select('td:nth-child(1) > span')
dates1 = format_dates(team1_dates)
team2_dates = team2.select('td:nth-child(1) > span')
dates2 = format_dates(team2_dates)

def build_data(soup, dates, name):
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
	return data

	# week = get_week(data)
	# match = get_team(week, name)
	# free = get_free(week)
	# team = [match, free]



data1 = build_data(team1, dates1, 'Aston Villa')
data2 = build_data(team2, dates2, 'Borussia Mönchengladbach')
# print(data)

def get_week(data):
	week = pd.DataFrame()
	for i in range(len(data)):
		if data['Date'][i] >= dt.datetime.date(dt.datetime.now()) and data['Date'][i] <= dt.datetime.date(dt.datetime.now() + dt.timedelta(days=14)):
			week = week.append(data.iloc[i])
	week = week.reset_index(drop=True)
	return week

week1 = get_week(data1)
week2 = get_week(data2)
# print(week)

def get_team(week, name):
	name.replace(' ', chr(160))    
	team = pd.DataFrame()
	for i in range(len(week)):
		if week['Home'][i] == name or week['Away'][i] == name:		# Only necessary for Aston Villa, since we look at the whole league
			team = team.append(week.iloc[i])
	team = team.reset_index(drop=True)
	return team
	
av = get_team(week1, 'Aston' + chr(160) + 'Villa')		# For some reason we have to use non-breaking space instead of space
bmg = get_team(week2, "M'gladbach")

def get_free(week):
	free = pd.DataFrame()
	for i in range(len(week)):
		if week['Channel'][i] == 'TV3+':
			free = free.append(week.iloc[i])
	free = free.reset_index(drop=True)
	return free
free = get_free(week1)
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




subject = 'Kamper de neste 14 dagene'
body = f"""
Her er Kamper de neste 14 dagene for Aston Villa:

{av}

Kamper de neste 14 dagene på TV3+:

{free}

Kamper de neste 14 dagene for Borussia Mönchengladbach:

{bmg}

"""
# print(body)

no_games = """
Det er ingen kamper å vise.
"""

av_games = f"""
Her er Kamper de neste 14 dagene for Aston Villa:

{av}

"""

free_games = f"""
Kamper de neste 14 dagene på TV3+:

{free}

"""

bmg_games = f"""
Kamper de neste 14 dagene for Borussia Mönchengladbach:

{bmg}

"""

def mail(email_receiver, subject, body, av, free, bmg):
	if len(av) == 0 and len(free) == 0 and len(bmg) == 0:
		send_email(email_receiver, subject, no_games)

	elif len(free) == 0 and len(bmg) == 0:
		send_email(email_receiver, subject, av_games)

	elif len(av) == 0 and len(bmg) == 0:
		print(1)
		send_email(email_receiver, subject, free_games)

	elif len(av) == 0 and len(free) == 0:
		send_email(email_receiver, subject, bmg_games)

	elif len(av) == 0:
		send_email(email_receiver, subject, free_games + bmg_games)

	elif len(free) == 0:
		send_email(email_receiver, subject, av_games + bmg_games)

	elif len(bmg) == 0:
		send_email(email_receiver, subject, av_games + free_games)

	else:
		send_email(email_receiver, subject, body)

mail(email_receiver, subject, body, av, free, bmg)