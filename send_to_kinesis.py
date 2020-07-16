"""
Run as main to run test stream using reddit as keyword.
"""

import datetime as dt
import json
import logging
import os
import pytz
import yaml
from dateutil.parser import parse

# Use custom logger settings
from extras.logger import configure_logger

import boto3
from botocore.client import Config

from tweepy import OAuthHandler, Stream, StreamListener

import settings

logger = configure_logger(name='sender')

class TweetsCollector:
    """
    Streaming using Tweepy:
    http://docs.tweepy.org/en/latest/streaming_how_to.html
    """

    def __init__(self, stream_name, producer, keywords, test=None):
        self.stream_name = stream_name
        self.producer = producer
        self.keywords = keywords
        configs = self.configs_loader()
        try:
            twitter_auth = configs['twitter']
            aws_auth = configs['aws']
        except TypeError:
            logger.error('configs.yml file is empty or does not exist.')
        except KeyError:
            logger.error('configs.yml file does not contain credentials for twitter.')

        # set aws credentials
        self.aws_credentials = {
            "aws_access_key_id": aws_auth.get("aws_access_key"),
            "aws_secret_access_key": aws_auth.get("aws_secret_access_key"),
            "region_name": aws_auth.get("default_region")
        }
        # set twitter auth
        self.auth = OAuthHandler(twitter_auth['consumer_key'], twitter_auth['consumer_secret'])
        self.auth.set_access_token(twitter_auth['access_token'], twitter_auth['access_secret'])

        # set a standard stdout print listener for testing
        if test:
            listener = StdOutListener()
        else:
            listener = SendTweetsToKinesis(
                stream_name=self.stream_name,
                producer=self.producer,
                keywords=self.keywords,
                aws_credentials=self.aws_credentials
            )

        # Establish Tweepy stream
        self.twitter_stream = Stream(
            auth=self.auth,
            listener=listener
        )
        logger.info(self.keywords)
        self.twitter_stream.filter(
            track=self.keywords,
        )

    @staticmethod
    def configs_loader():
        settings_path = os.path.realpath(os.path.dirname(settings.__file__))
        configs_file = os.path.join(settings_path, 'configs.yml')
        try:
            with open(configs_file, 'r') as f:
                configs = yaml.load(f, Loader=yaml.BaseLoader)
                return configs
        except IOError:
            logger.error('No configs.yml found')


class SendTweetsToKinesis(StreamListener):
    """
    Use Boto3 to send tweets to AWS Kinesis
    """

    def __init__(self, stream_name, producer, keywords, aws_credentials):
        super().__init__()
        session = boto3.Session(**aws_credentials)
        self.kinesis = session.client(
            'kinesis', 
            config=Config(
                connect_timeout=5,
                retries={'max_attempts': 0}
            ),
        )
        self.stream_name = stream_name
        self.producer = producer
        self.keywords = keywords

    def on_data(self, raw_data):
        tweet = json.loads(raw_data)
        tweet_to_send = self.create_tweet_for_kinesis(
            name='twitter',
            tweet=tweet,
            keywords=self.keywords,
            producer=self.producer
        )
        logger.info(tweet_to_send)
        res = self.put_tweet_to_kinesis(
            stream_name=self.stream_name,
            tweet=tweet_to_send
        )
        logger.info(res)

    def on_error(self, status):
        logger.error(status)
        return True

    @staticmethod
    def create_tweet_for_kinesis(tweet, keywords, name='twitter', producer='stream_to_stream'):
        def get_user_created(user_created, time_zone):
            matched_tz = [a for a in set(pytz.all_timezones_set) if time_zone in a]
            parsed_time = parse(user_created)
            parsed_time = parsed_time.replace(tzinfo=None)
            if len(matched_tz) > 0:
                user_created_tz = pytz.timezone(matched_tz[0])
                user_created_time = user_created_tz.localize(parsed_time, is_dst=None)
            else:
                user_created_time = parsed_time.isoformat()

            return user_created_time

        def __clean_tweet(tweet_to_clean):
            attrs = ['created_at', 'lang', 'geo', 'coordinates', 'place', 'retweeted', 'source',
                     'text', 'timestamp_ms']
            user_attrs = ['name', 'screen_name', 'location', 'url', 'description',
                          'followers_count', 'created_at', 'utc_offset', 'time_zone', 'lang']
            clean = {a: tweet_to_clean[a] for a in attrs}
            created_at = dt.datetime.fromtimestamp(int(clean['timestamp_ms'])/1000)
            # setup UTC timezone, needed if the producer is not UTC time
            created_at = created_at.astimezone(pytz.utc)
            clean['created_at'] = created_at.isoformat()
            clean['user'] = {a: tweet_to_clean['user'][a] for a in user_attrs}
            clean['user']['created_at'] = get_user_created(
                clean['user']['created_at'],
                clean['user']['time_zone']
            )
            logger.debug(f'User created time {clean["user"]["created_at"]}')
            clean['hashtags'] = [el['text'] for el in tweet_to_clean['entities']['hashtags']]

            return clean

        record = __clean_tweet(tweet)
        record['name'] = name
        record['meta'] = {'created_at': dt.datetime.utcnow().isoformat(), 'producer': producer,
                          'keywords': ','.join(keywords)}

        if 'created_at' not in record.keys():
            record['created_at'] = record['meta']['created_at']

        return record

    def put_tweet_to_kinesis(self, stream_name, tweet, partition_key='created_at'):
        res = self.kinesis.put_record(
            StreamName=stream_name,
            Data=json.dumps(tweet),
            PartitionKey=partition_key
        )

        return res

class StdOutListener(StreamListener):
    """ 
    A listener handles tweets that are received from the stream.
    This is a basic listener that just prints received tweets to stdout.
    Used only for testing.
    """
    def on_data(self, data):
        print(data)
        return True

    def on_error(self, status):
        print(status)


if __name__ == '__main__':
    logger.info('Starting --------------------------------------------------------------------------------------------')
    TweetsCollector(stream_name='TestStream01', producer='stream_test_001', keywords=['reddit'], test=None)