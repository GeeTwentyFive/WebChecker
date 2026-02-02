# Dependencies

`pip install beautifulsoup4 openai`


# Usage

`python WebChecker.py`

(if it is your first time running, edit generated config file after running and then run again)


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
    "per_website_check_interval": 60.0,
    "all_checks_interval": 3600.0
}
```