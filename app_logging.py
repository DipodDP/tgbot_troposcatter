import logging
import logging.config
import sys

from tgbot.config import Config


def setup_logging(config: Config):
    """
    Set up logging configuration for the application.
    """
    log_level = config.tg_bot.log_level

    logging_config = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'default': {
                'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            },
            'json': {
                '()': 'pythonjsonlogger.jsonlogger.JsonFormatter',
                'format': '%(asctime)s %(name)s %(levelname)s %(message)s',
            },
        },
        'handlers': {
            'default': {
                'class': 'logging.StreamHandler',
                'formatter': 'default',
                'level': log_level,
                'stream': sys.stdout,
            },
        },
        'root': {'handlers': ['default'], 'level': log_level},
        'loggers': {
            'gunicorn.error': {
                'level': log_level,
                'handlers': ['default'],
                'propagate': False,
            },
            'gunicorn.access': {
                'level': log_level,
                'handlers': ['default'],
                'propagate': False,
            },
        },
    }

    logging.config.dictConfig(logging_config)
    logging.getLogger('httpx').setLevel(logging.WARNING)
    logging.getLogger('aiogram').setLevel(log_level)
