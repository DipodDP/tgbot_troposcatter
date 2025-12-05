# tgbot_troposcatter

## Troposcatter trace calculator

Bot is available as Troposcatter_bot in Telegram

Bot is running on free server https://eu.pythonanywhere.com/, so it may work slowly sometimes.
Bot has minimal Flask interface to check status, start or restart if it's down with scheduled task, like:
```shell
curl http://bot_name.eu.pythonanywhere.com/start
```

This telegram bot was created for calculating troposcatter trace parameters, but, mostly, as education project (that's my first experience in Python).
It's useful for guidance station antennas at two sites on azimuth between them. Also, bot calculate horizon close angle (HCA) and trace profile between sites.

For tropo station Groza-1.5 it calculates losses and estimated median speed on trace.

Bot supports almost any input formats for sites coordinates like decimal or "ddd_mm_ss.s".

By default N-latitude and E-longitude are used, if S-latitude or W-longitude are not defined.

And watch your language, please. Bot may be a little pique.

## Configuration

The project includes two new files for configuration: `paths.py` and `logging.py`. The `paths.py` file defines all the relevant paths for the project, while the `logging.py` file configures all the logging settings.

To run the bot, you need to create a `.env` file in the root of the project. You can do this by copying the `.env.dist` file and renaming it to `.env`.

```shell
cp .env.dist .env
```

Then, you need to fill in the required environment variables in the `.env` file. The following variables are required:

- `BOT_TOKEN`: Your Telegram bot token.
- `ADMINS`: A comma-separated list of Telegram user IDs that should have admin access to the bot.
- `ELEVATION_API_URL`: The URL for the elevation API.
- `ELEVATION_API_KEY`: The API key for the elevation API.
- `DECLINATION_API_URL`: The URL for the declination API.
- `DECLINATION_API_KEY`: The API key for the declination API.
```
