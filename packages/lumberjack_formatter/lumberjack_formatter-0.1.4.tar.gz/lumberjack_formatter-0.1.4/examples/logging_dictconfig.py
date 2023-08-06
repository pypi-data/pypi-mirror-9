import logging
import logging.config

# make a logging configuration
config = {
    'version':  1,
    'formatters': {
        'lumberjack': {
            '()': 'lumberjack_formatter.LumberjackFormatter',
            # instead of using the all_fields option below, we could explicitly specify the fields
            # 'format': [
            #     'isocreated',
            #     'relativeCreated',
            #     'levelname',
            #     'message',
            # ],
            'all_standard_fields': True,
            'all_extra_fields': True,
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'lumberjack',
            'stream': 'ext://sys.stdout',
        }
    },
    'root': {
        'level': 'DEBUG',
        'handlers': ['console'],
    },
}

# note that the configuration could have been read in from a file of equivalent json
import sys
import json
print '  json logging configuration:'
json.dump(config, sys.stdout, indent=2)
print '\n*******'

# .. or equivalent yaml
import yaml
print '  yaml logging configuration:'
yaml.dump(config, sys.stdout)
print '*******'

# load the configuration into logging
logging.config.dictConfig(config)

# create a logger
log = logging.getLogger()

# log examples
log.debug('debug message')
log.info('info message')
log.warn('warn message')
log.error('error message')
log.critical('critical message')