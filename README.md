# Dependencies

`pip install beautifulsoup4 openai bottle`


# Usage

If it is your first time running: Run `python WebChecker.py` then edit the generated config file.

Config:
- `"target_websites"` = list of websites to check
- `"webchecker_email_server"` - mailserver to use for sending alert emails
- `"webchecker_email_server_port"` - port to use for mailserver communication
- `"webchecker_email_address"` - email address for WebChecker on mailserver
- `"webchecker_email_password"` - password for WebChecker's account on mailserver
- `"alert_email_addresses"` - list of email addresses to alert
- `"openai_api_key"` - OpenAI API key
- `"check_interval"` = how frequently to check websites in provided `"target_websites"` list (in seconds)

Then, and for all subsequent usages, run: `python WebChecker.py`

It is recommended to use a minimum tier 2 OpenAI account due to there being no daily rate limits for the moderation API
(to see OpenAI API limits for your account's tier: https://platform.openai.com/settings/organization/limits)


# Example config

```json
{
    "target_websites": [
        "https://www.example.com",
        "https://www.google.com"
    ],
    "webchecker_email_server": "smtp.gmail.com",
    "webchecker_email_server_port": 465,
    "webchecker_email_address": "example@gmail.com",
    "webchecker_email_password": "example123",
    "alert_email_addresses": [
        "target1@example.com",
        "target2@example.com"
    ],
    "openai_api_key": "sk-proj-EXAMPLE",
    "check_interval": 3600.0
}
```