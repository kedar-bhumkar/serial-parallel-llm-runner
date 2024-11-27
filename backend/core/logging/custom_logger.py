import logging
import logging.config


# Example logging configuration as a dictionary
logging_config = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'standard',
        },
    },
    'loggers': {
        '': {  # root logger
            'handlers': ['console'],
            'level': 'WARNING',
            'propagate': False
        },
        'my_module': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False
        },
    }
}

def setup_logging():
    logging.config.dictConfig(logging_config)
    # Disabling logging for a specific level
    


setup_logging()
# Create a logger instance
logger = logging.getLogger('my_application')
logger.setLevel(logging.ERROR)