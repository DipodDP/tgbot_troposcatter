import asyncio
# from threading import Thread

from flask import Flask

from bot import main, logger

app = Flask('Background')


@app.route('/')
def home():
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.warning("Bot stopped!")
    except RuntimeError as e:
        print(f'{e}')
    main()
    return ('Bot is alive!')


if __name__ == '__main__':
    app.run()

# def run():
#     app.run(host='0.0.0.0', port=80)
#
#
# def keep_alive():
#     t = Thread(target=run)
#     t.start()
