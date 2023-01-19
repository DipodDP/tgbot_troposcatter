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
