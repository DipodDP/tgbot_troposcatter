import asyncio
from threading import Thread

from flask import Flask

from bot import main, logger

app = Flask('Background')


def run():
    try:
        asyncio.run(main())
        return 'Bot is alive!'
    except (KeyboardInterrupt, SystemExit):
        logger.warning("Bot stopped!")
    except RuntimeError as e:
        print(f'{e}')


def keep_alive():
    t = Thread(target=run)
    t.start()


@app.route('/')
def home():
    keep_alive()
    return 'Bot is alive!'


if __name__ == '__main__':
    app.run()
