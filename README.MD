# Twitter Kinesis Stream Producer

A small producer application to grab tweets meeting a specific filter criteria and send them to AWS kinesis after some minor processing.

## To Use

Requires a config.yaml file to be created in the settings folder with your credentials (to be replaced by AWS Secret Manager in the future).

Example:
```yaml
twitter:
  app_name: 'tiwtter_amm_name'
  consumer_key: 'consumer_key'
  consumer_secret: 'consumer_secret'
  access_token: 'access_token'
  access_secret: 'access_secret'
aws:
  account_name: 'aws_account_name'
  aws_access_key: 'aws_access_key'
  aws_secret_access_key: 'aws_secret_access_key'
  stream_name: 'kinesis_stream_name'
  default_region: 'aws_default_region'
```

Once the credentials file is created simply run the send_to_kinsis file to enable your stream producer:
```bash
python send_to_kinesis.py
```

There's also an experimental tweet_daemon.py script to run the producer as a daemon on EC2 (or another cloud compute resource).

When running the producer will create a log directory in the same folder containing all of the retreived tweet logs.

## Snowpipe
To setup a snowpipe for data ingestion into Snowflake see the [Snowpipe readme](SNOWPIPE_SETUP.MD).