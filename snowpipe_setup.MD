## Create snowpipe in snowflake to auto-ingest new tweet data

### First create staging area 
```sql
CREATE OR REPLACE STAGE LANDING_ZONE.TWITTER.TWEETS_STAGE
URL = S3://coveo-twitter-test/
CREDENTIALS = (AWS_KEY_ID = 'KEY' AWS_SECRET_KEY = 'SECRET_KEY');
```
### Then create table to add data to
This table uses an incremental integer RECID column to record order tweets were added and to troubleshoot any duplicates or other issues that may arrise. It also includes a LOADED_AT_UTC column to show the load timestamp for the data to track and SLA issues.
```sql
CREATE OR REPLACE TABLE LANDING_ZONE.TWITTER.TWEETS
(
    JSONBODY VARIANT
  , RECID INT NOT NULL IDENTITY
  , LOADED_AT_UTC TIMESTAMP_NTZ NOT NULL SYSDATE()
);
```
Finally create the snowpipe which will load the data into snowflake. Be sure to capture the AWS ARN to set up your S3 notifications settings properly.
```sql
CREATE OR REPLACE PIPE LANDING_ZONE.TWITTER.TWEETS_PIPE AUTO_INGEST=TRUE AS
    COPY INTO LANDING_ZONE.TWITTER.TWEETS
    FROM @LANDING_ZONE.TWITTER.TWEETS_STAGE
    FILE_FORMAT = (TYPE = 'JSON');
```

If you need to see your created pipes or stages use:
```SQL
SHOW PIPES;
SHOW STAGES;
```