"""
Container/Server must have AWS CLI set up to account:
https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-install.html

Use this file to run as Daemon.

Required environment variables when establishing server:
STREAM_NAME: Name of Kinesis stream
PRODUCER_NAME: Name of the producer (current application)
TWITTER_KEYWORDS: comma separated string to use as filters
"""

import datetime as dt
import os
import logging
import yaml

# Use custom logger settings
from extras.logger import configure_logger

from daemon import DaemonContext
from send_to_kinesis import TweetsCollector

logger = configure_logger(name='daemon')

# For testing purposes load enviromnet variables from settings file ---------
import settings

def configs_loader():
    settings_path = os.path.realpath(os.path.dirname(settings.__file__))
    configs_file = os.path.join(settings_path, 'configs.yml')
    try:
        with open(configs_file, 'r') as f:
            configs = yaml.load(f, Loader=yaml.BaseLoader)
            return configs
    except IOError:
        logger.error('No configs.yml found')

configs = configs_loader()
os.environ['STREAM_NAME'] = configs.get('aws', {}).get('stream_name')
os.environ['PRODUCER_NAME'] = configs.get('twitter', {}).get('app_name')
os.environ['TWITTER_KEYWORDS'] = "coveo,Coveo"
# testing ended -------------------------------------------------------------


def run_daemon(logger):
    """
    Function to run TweetsCollector as a Daemon process.
    """
    context = DaemonContext()

    with context:
        logger.info('Started at %s', dt.datetime.now())

        stream_name = os.environ['STREAM_NAME']
        producer_name = os.environ['PRODUCER_NAME']
        keywords = os.environ['TWITTER_KEYWORDS'].split(',')

        logger.info(keywords)
        TweetsCollector(
            stream_name=stream_name,
            producer=producer_name,
            keywords=keywords
        )


if __name__ == '__main__':
    run_daemon(logger=logger)
