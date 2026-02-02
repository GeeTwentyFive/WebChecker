import os
import json
import sys
import time
import smtplib
import ssl
import urllib.request

from bs4 import BeautifulSoup
from openai import OpenAI


CONFIG_FILE_NAME = "WebChecker_config.json"
DEFAULT_CONFIG = {
	"target_websites": [],
	"webchecker_email_server": "smtp.gmail.com",
	"webchecker_email_server_port": 465,
	"webchecker_email_address": "",
	"webchecker_email_password": "",
	"alert_email_addresses": [],
	"openai_api_key": "",
	"per_website_check_interval": 60.0,
	"all_checks_interval": 3600.0
}


if not os.path.isfile(CONFIG_FILE_NAME):
	print(f"Config file ({CONFIG_FILE_NAME}) not found, creating...")
	with open(CONFIG_FILE_NAME, "w") as f:
		f.write(json.dumps(DEFAULT_CONFIG, indent=4))
	print(f"Populate '{CONFIG_FILE_NAME}' then start program again")
	sys.exit()


config = {}

with open(CONFIG_FILE_NAME) as f:
	config = json.loads(f.read())

if len(config["target_websites"]) == 0:
	print(f"ERROR: Zero target websites provided in {CONFIG_FILE_NAME}")
	sys.exit(1)

if len(config["alert_email_addresses"]) == 0:
	print(f"ERROR: Zero alert email addresses provided in {CONFIG_FILE_NAME}")
	sys.exit(1)


print("Logging in to mailserver...")
email_server = smtplib.SMTP_SSL(
	config["webchecker_email_server"],
	config["webchecker_email_server_port"],
	context=ssl.create_default_context()
)
email_server.login(config["webchecker_email_address"], config["webchecker_email_password"])

print("Requesting OpenAI session...")
openai_client = OpenAI(api_key=config["openai_api_key"])

print("Running")
while True:
	for target_website in config["target_websites"]:
		try: uo = urllib.request.urlopen(target_website)
		except Exception as e:
			print(f"ERROR: Failed to fetch HTML from {target_website}\n{str(e)}")
			try: email_server.sendmail(
				config["webchecker_email_address"],
				config["alert_email_addresses"],
				f"Website '{target_website}' might be down"
			)
			except Exception as e: print(f"ERROR: Failed to send down alert email\n{str(e)}")
			continue

		soup = BeautifulSoup(uo.read(), features="html.parser")
		for elem in soup(["script", "style"]): elem.decompose()

		try: response = openai_client.moderations.create(
			model="omni-moderation-latest",
			input=soup.get_text()
		)
		except Exception as e:
			print(f"ERROR: Failed to get response from OpenAI\n{str(e)}")
			continue

		for result in response["results"]:
			if result["flagged"] == True:
				try: email_server.sendmail(
					config["webchecker_email_address"],
					config["alert_email_addresses"],
					f"Potentially inappropriate content found on '{target_website}':\n{json.dumps(result)}"
				)
				except Exception as e: print(f"ERROR: Failed to send potential inappropriate content alert email\n{str(e)}")
		
		time.sleep(config["per_website_check_interval"])

	time.sleep(config["all_checks_interval"])