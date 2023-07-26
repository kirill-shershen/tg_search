[![search gitflow](https://github.com/kirill-shershen/tg_search/actions/workflows/main.yml/badge.svg)](https://github.com/kirill-shershen/tg_search/actions/workflows/main.yml)
# tg_search

Another one telegram bot that can search for specified open groups. The result is given in one message with links to the source. Django admin panel for managing.


## Environment Variables

To run this project, you must add the following environment variables.

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

## Authorize
For using Telethon you should get your API ID. You can do this with this [guide](https://docs.telethon.dev/en/stable/basic/signing-in.html).

Basically, you need a telegram bot to interact with users. And you need a telegram account to search through open chats.
So you need to authorize to each of them.
1. To do this you should run the Django admin panel and open the Client session model.
2. We need to create records: 1 for the **bot** and 2 for the **account** with **login required** for both.
3. Then you should create login records.
   - For the **bot** you should select the bot client session, bot_token and phone number.
   - For the **account** you should select the account client session and phone number
4. Now select action **Send request code** for **account** and press Go. When you have received message from telegram you should save a code to **code** field.
5. Then select **login** action on both of the records and press Go.
6. In the client session model, all records become **Login Waiting For Telegram Client**

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
