import asyncio
import logging
from multiprocessing import Process
from time import sleep

import requests
from environs import Env
from flask import Flask, request

from aiogram import Bot, Dispatcher, types

from bot import WEBHOOK_PATH, build_dispatcher, on_startup
from tgbot.config import load_config

_env = Env()
_env.read_env('.env')

STARTUP_PATH = '/start'
INTERVAL = 60 * 30  # Time interval in seconds (e.g., every 30 minutes)

logger = logging.getLogger(__name__)

app = Flask(__name__)

# Build the aiogram Dispatcher once, in-process, and keep a dedicated event
# loop to run coroutines on. On PythonAnywhere only the WSGI web app can accept
# inbound connections; a bot subprocess binds but is unreachable. So Flask must
# own the Dispatcher and handle updates itself instead of proxying to a separate
# process.
config = load_config('.env')
dp: Dispatcher = build_dispatcher(config)
loop = asyncio.new_event_loop()


def _run(coro):
    """Run a coroutine on the module-wide loop with aiogram context set."""
    Bot.set_current(dp.bot)
    Dispatcher.set_current(dp)
    return loop.run_until_complete(coro)


def setup_webhook(url):
    """Register ``url`` as the Telegram webhook host and run bot startup.

    Called from the WSGI configuration file with the app's public URL (the same
    URL used for the self-ping), so the webhook host has a single source. The
    ``/webhook`` path is appended by ``on_startup`` via ``set_webhook``.
    """
    dp.bot.get('config').tg_bot.webhook_host = url
    try:
        _run(on_startup(dp))
    except Exception:  # pragma: no cover - set_webhook/notify best-effort
        logger.exception('on_startup failed')


def request_startup_url(url):
    """Function to make a startup requests"""
    try:
        response = requests.get(url)
        status_code = response.status_code

        print(f'Requested {url}, status code: {status_code}')

        sleep(5)

        if status_code not in (200, 302):
            request_startup_url(url)

    except Exception as e:
        print(f'Error while requesting {url}: {e}')


def request_url_periodically(url, interval):
    """Function to make a periodic startup requests"""
    request_startup_url(url)
    while True:
        try:
            sleep(interval)
            response = requests.get(url)
            print(f'Requested {url}, status code: {response.status_code}')

        except Exception as e:
            print(f'Error while requesting {url}: {e}')


def start_requester_process(url):
    """
    For Pythonanywhere you need to put this into your WSGI configuration file to run background start process::

    import sys


    # add your project directory to the sys.path
    project_home = '/home/<your_pythonanywhere_username>/<your_project_directory>'
    if project_home not in sys.path:
        sys.path = [project_home] + sys.path

    # import flask app but need to call it "application" for WSGI to work
    from background import app as application  # noqa
    from background import setup_webhook, start_requester_process

    url = 'https://' + '.'.join(__name__.split('_')[:-2]) + '.com'
    print('URL is: ', url)
    setup_webhook(url)            # register the Telegram webhook at <url>/webhook
    start_requester_process(url)  # keep the free-tier app awake with a self-ping
    """

    # Create the background requester process. This periodic self-ping keeps the
    # free-tier web app awake; Telegram webhook POSTs also wake it on demand.
    requester_process = Process(
        target=request_url_periodically,
        args=(url + STARTUP_PATH, INTERVAL),
    )
    requester_process.start()  # Start the process


@app.route('/')
def home():
    return '<h1>Bot is alive! :)</h1>'


@app.route(STARTUP_PATH)
def start():
    """Lightweight health/keep-alive endpoint for the self-pinger.

    The bot no longer runs as a subprocess, so there is nothing to spawn here;
    a request to any route already wakes the sleeping web app.
    """
    return '<h1>Bot is alive! :)</h1>'


@app.route(WEBHOOK_PATH, methods=['POST'])
def webhook_handler():
    """Feed the incoming Telegram update straight into the Dispatcher.

    No proxy hop to a bot subprocess (unreachable on PythonAnywhere) and no
    aiogram IP-allowlist check (which 403s behind a proxy) - the update is
    handled in this same process and replies go out via the bot API.
    """
    update = types.Update(**request.get_json(force=True))
    _run(dp.process_update(update))
    return '', 200


if __name__ == '__main__':
    app.run()
