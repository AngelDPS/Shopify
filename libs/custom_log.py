import logging
import logging.config
import sys, os

LOG_DIRECTORY = "logs"
LOG_FILE = "SHOPIFY.log"
if not os.path.exists(LOG_DIRECTORY):
    os.makedirs(LOG_DIRECTORY)

CONFIG = {
   'version': 1,
   'formatters': {
      'brief': {
         'format': '%(message)s'
      },
      'precise': {
         'format': '%(asctime)s;%(name)-15s;%(levelname)-8s;%(message)s'
      }
   },
   'handlers': {
      'console': {
         'class': 'logging.StreamHandler',
         'level': 'WARNING',
         'formatter': 'brief',
         'stream': sys.stdout
      },
      'file': {
         'class': 'logging.handlers.TimedRotatingFileHandler',
         'formatter': 'precise',
         'level': 'DEBUG',
         'filename': os.path.join(LOG_DIRECTORY, LOG_FILE),
         'when': 'midnight',
         'interval': 1,
         'backupCount': 5
      }
   },
   'loggers': {
      'Shopify': {
         'level': 'DEBUG',
         'propagate': True,
         'handlers': ['console', 'file']
      }
   }
}


def getLogger(name: str = None) -> logging.Logger:
   logging.config.dictConfig(CONFIG)
   return logging.getLogger(name)