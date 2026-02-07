import os
import json
import sys
import time
import smtplib
import ssl
import urllib.request
import urllib.error
from threading import Thread, Lock

from bs4 import BeautifulSoup
from openai import OpenAI
import bottle


CONFIG_FILE_NAME = "WebChecker_config.json"
DEFAULT_CONFIG = {
	"target_websites": [],
	"webchecker_email_server": "smtp.gmail.com",
	"webchecker_email_server_port": 465,
	"webchecker_email_address": "",
	"webchecker_email_password": "",
	"alert_email_addresses": [],
	"openai_api_key": "",
	"check_interval": 3600.0,
	"web_gui_port": 50000
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

def send_alert_emails(msg: str) -> None:
	try: email_server.sendmail(
		config["webchecker_email_address"],
		config["alert_email_addresses"],
		msg
	)
	except Exception as e: print(f"ERROR: Failed to send alert email\n{str(e)}")

print("Requesting OpenAI session...")
openai_client = OpenAI(api_key=config["openai_api_key"])

website_states = {}
website_states_lock = Lock()
def update_website_state(name, state=""):
	if name not in config["target_websites"]: raise IndexError

	global website_states
	with website_states_lock:
		website_states[name] = state

def checker_loop():
	while True:
		for target_website in config["target_websites"]:
			if target_website not in website_states.keys():
				update_website_state(target_website)

			print(f"Checking '{target_website}' ...")

			error_msg = None
			try: uo = urllib.request.urlopen(target_website)
			except urllib.error.URLError as e:
				error_msg = f"URLError encountered for '{target_website}'\nReason -> {str(e.reason)}"
			except urllib.error.HTTPError as e:
				error_msg = f"HTTPError encountered for '{target_website}'\nHTTP code -> {str(e.code)}\nReason -> {str(e.reason)}"
			except Exception as e:
				error_msg = f"Unexpected exception encountered for '{target_website}'\n{str(e)}"
			if error_msg:
				print(error_msg)
				send_alert_emails(error_msg)
				update_website_state(target_website, error_msg)
				continue

			soup = BeautifulSoup(uo.read(), features="html.parser")
			for elem in soup(["script", "style"]): elem.decompose()

			def chunks(lst: list, chunk_size: int):
				for i in range(0, len(lst), chunk_size):
					yield lst[i:i+chunk_size]

			for chunk in chunks(soup.get_text(separator="\n", strip=True), 1000):
				try: response = openai_client.moderations.create(
					model="omni-moderation-latest",
					input=chunk
				)
				except Exception as e:
					if "429" in str(e):
						print("OpenAI API token rate limit reached, waiting for reset...")
						time.sleep(361.0) # takes 6 minutes to reset token rate limit on OpenAI API
					else: print(f"ERROR: Failed to get response from OpenAI\n{str(e)}")
					continue
				
				for result in response.results:
					if result.flagged == True:
						msg = (
							f"Potentially inappropriate content found on '{target_website}'\n"
							f"\nCategories -> \n{str(result.categories).replace(" ", "\n")}\n"
							f"\nWithin input -> \n{chunk}\n"
						)
						print(msg)
						send_alert_emails(msg)
						update_website_state(target_website, msg)
				
				time.sleep(2.01) # because omni-moderation-latest Requests-Per-Minute rate limit = 500 RPM (on tiers 1 & 2)

		print(f"Finished checking target websites, sleeping for {str(config["check_interval"])} seconds...")
		time.sleep(config["check_interval"])

print("Running checker...")
Thread(target=checker_loop, daemon=True).start()


@bottle.route("/")
def web_gui():
	html = (
		"<style>"
		"table {width: 100%; border-collapse: collapse;}"
		"td, th {border: 1px solid #dddddd; text-align: left; padding: 8px;}"
		"</style>"

		"<script>"
		"setInterval(function(){location.reload(true)}, 10000)"
		"</script>"

		"<table>"
		"<tr>"
		"<th>" "Name" "</th>"
		"<th>" "State" "</th>"
		"</tr>"
	)

	with website_states_lock:
		for name, state in website_states.items():
			html += "<tr>"

			if state != "": html += '<td style="background-color: #ff0000;">'
			else: html += "<td>"
			html += name + "</td>"

			html += "<td>" + (state if (state != "") else "OK") + "</td>"

			html += "</tr>"

	html += "</table>"

	return html

bottle.run(host="0.0.0.0", port=config["web_gui_port"])
