import os
import json
import sys
import time
import urllib.request

from bs4 import BeautifulSoup


CONFIG_FILE_NAME = "WebChecker_config.json"
DEFAULT_CONFIG = {
	"target_websites": [],
	"webchecker_email_address": "",
	"webchecker_email_password": "",
	"alert_email_addresses": [],
	"check_interval": 3600.0
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

if len(config["webchecker_email_address"]) == 0:
	print(f"ERROR: WebChecker email address not provided in {CONFIG_FILE_NAME}")
	sys.exit(1)

if len(config["webchecker_email_password"]) == 0:
	print(f"ERROR: WebChecker email password not provided in {CONFIG_FILE_NAME}")
	sys.exit(1)

if len(config["alert_email_addresses"]) == 0:
	print(f"ERROR: Zero alert email addresses provided in {CONFIG_FILE_NAME}")
	sys.exit(1)


# TODO: Login to email server via config["webchecker_email_address"] + config["webchecker_email_password"]


while True:
	for target_website in config["target_websites"]:
		try: uo = urllib.request.urlopen(target_website)
		except:
			print(f"ERROR: Failed to fetch HTML from {target_website}")
			for alert_email_address in config["alert_email_addresses"]:
				pass # TODO: EMAIL
			continue
		
		soup = BeautifulSoup(uo.read(), features="html.parser")
		for elem in soup(["script", "style"]): elem.decompose()

		# TODO: `soup.get_text()` -> check with AI, e-mail if undesireable content

	time.sleep(config["check_interval"])