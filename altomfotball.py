import os
from dotenv import load_dotenv
import smtplib
import ssl
import pandas as pd
import requests
import time
import datetime as dt
from bs4 import BeautifulSoup
from email.message import EmailMessage

load_dotenv(".env")

username = os.environ.get('USERNAME')
password = os.environ.get('PASSWORD')
print(username, password)

response = requests.get("https://www.altomfotball.no/elementsCommonAjax.do?cmd=fixturesContent&seasonId=344&teamId=732&month=all&useFullUrl=false")
# response = requests.get("https://www.altomfotball.no/elementsCommonAjax.do?cmd=fixturesContent&tournamentId=230&month=all&useFullUrl=false")
if response.status_code != 200:
	print("Error fetching page")
	exit()
else:
	content = response.content
soup = BeautifulSoup(response.content, 'html.parser')


all_dates = soup.select('td:nth-child(1) > span')
dates = [r.text.split(' ')[0] for r in all_dates]
dates = [dt.datetime.strptime(r, '%d.%m.%Y') for r in dates]
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



email_sender = username; email_password = password
email_receiver = 'm.gjestrud@gmail.com'


def send_email():

	subject = 'Altomfotball'
	body = """
	Hei!
	Dette er en test av å sende epost fra Python.
	Mvh
	Marius"""

	em = EmailMessage()
	em['From'] = email_sender
	em['To'] = email_receiver
	em['Subject'] = subject
	em.set_content(body)

	context = ssl.create_default_context()

	with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
		smtp.login(email_sender, email_password)
		smtp.sendmail(email_sender, email_receiver, em.as_string())

send_time = dt.datetime(2023,1,22,19,52,0) # set your sending time in UTC
# send_email()



current_date = dt.datetime.date(dt.datetime.now())
print(current_date)