[![search gitflow](https://github.com/kirill-shershen/tg_search/actions/workflows/main.yml/badge.svg)](https://github.com/kirill-shershen/tg_search/actions/workflows/main.yml)
# tg_search

Another one telegram bot that can search for specified open groups. The result is given in one message with a links to the source. Django admin panel for managing.


## Environment Variables

To run this project, you will need to add the following environment variables.

`TELEGRAM_BOT_API_KEY`

`TELEGRAM_API_ID`

`TELEGRAM_API_HASH`

## Run Locally

Clone the project and install virtual env

```bash
  git clone https://github.com/kirill-shershen/tg_search.git
  cd tg_search
  virtualenv .venv
  cd src
  python3 manage.py createsuperuser
  python3 manage.py runserver
```

## Run Locally in docker compose
```bash
  git clone https://github.com/kirill-shershen/tg_search.git
  cd tg_search
  docker-compose up -d
  docker-compose exec web python manage.py createsuperuser
```

Next step you have to run django admin panel to authorize in telegram.
In the login model page we need to fill phone number in both records and bot token only for **bot**

After that you have to execute **send request code** action and save received code to each record.
Then execute **login** action on each record.

Now bot will work
```bash
  cd src
  python3 run_bot.py
```
or
```bash
  docker-compose restart bot
```

## Demo

You can try it [here](https://t.me/kxebot)
