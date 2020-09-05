#!/usr/local/bin/python3

from anomaly_detectors import Checker
import boto3
import time
import datetime
import json
import constants
import pandas as pd


class Kinesis_RRCF(Checker):
    def __init__(self, aws_region, aws_access_key_id, secret_access_key, input_stream, output_stream, disk_group):
        self.aws_region = aws_region  # The AWS region where your Kinesis Analytics application is configured.
        self.aws_access_key_id = aws_access_key_id  # Your AWS Access Key ID
        self.secret_access_key = secret_access_key  # Your AWS Secret Access Key
        self.input_stream = input_stream
        self.output_stream = output_stream
        self._last_record_sequence_number = None
        self._num_record_being_read = 0
        self._disk_group = disk_group
        self._anomaly_df = pd.DataFrame(columns=['days', 'cum_afr', 'anomaly'])
        self._iloc_num = 0
        self.kinesis_analytics_client = boto3.client('kinesisanalytics', region_name=aws_region,
                                                     aws_access_key_id=aws_access_key_id,
                                                     aws_secret_access_key=secret_access_key)
        self.kinesis_client = boto3.client('kinesis', region_name=aws_region, aws_access_key_id=aws_access_key_id,
                                           aws_secret_access_key=secret_access_key)

        self.kinesis_client.create_stream(StreamName=self.input_stream, ShardCount=1)
        self.wait_for_stream(self.kinesis_client, self.input_stream)
        self.kinesis_client.create_stream(StreamName=self.output_stream, ShardCount=1)
        self.wait_for_stream(self.kinesis_client, self.output_stream)

        self.kinesis_application_name = 'CALCULATE_HDD_AFR_ANOMALIES'
        # 'CALCULATE_DISK_AFR_ANOMALIES' 'CALCULATE_HDD_AFR_ANOMALIES'
        response = self.kinesis_analytics_client.describe_application(
            ApplicationName=self.kinesis_application_name
        )
        input_desc_arr = (response.get('ApplicationDetail')).get('InputDescription s')
        input_id = input_desc_arr[0].get('InputId')

        self.kinesis_analytics_client.start_application(
            ApplicationName=self.kinesis_application_name,
            InputConfigurations=[
                {
                    'Id': input_id,
                    'InputStartingPositionConfiguration': {
                        'InputStartingPosition': 'NOW'
                    }
                },
            ]
        )

        while True:
            response = self.kinesis_analytics_client.describe_application(
                ApplicationName=self.kinesis_application_name
            )
            status = (response.get('ApplicationDetail')).get('ApplicationStatus')
            if status == 'RUNNING':
                print("Application " + self.kinesis_application_name + " is running!")
                break
            print("Sleeping because " + self.kinesis_application_name + " is not yet ready.")
            time.sleep(constants.SLEEP_TIME_BETWEEN_KINESIS_STAGES)

        Checker.__init__(self, "Robust random cut forest")

    def __del__(self):
        self._anomaly_df.to_csv("results/2018-09-25/t-0.5/anomalies/" + self._disk_group + "_anomaly_scores.csv")
        self.kinesis_analytics_client.stop_application(
            ApplicationName=self.kinesis_application_name
        )

        while True:
            response = self.kinesis_analytics_client.describe_application(
                ApplicationName=self.kinesis_application_name
            )
            status = (response.get('ApplicationDetail')).get('ApplicationStatus')
            if status == 'READY':
                print("Application " + self.kinesis_application_name + " has been stopped.")
                break
            print("Sleeping because " + self.kinesis_application_name + " is still running.")
            time.sleep(constants.SLEEP_TIME_BETWEEN_KINESIS_STAGES)

        self.kinesis_client.delete_stream(StreamName=self.input_stream, EnforceConsumerDeletion=True)
        time.sleep(1)
        self.kinesis_client.delete_stream(StreamName=self.output_stream, EnforceConsumerDeletion=True)
        print("Waiting 60 secs. to make sure streams are deleted.")
        time.sleep(constants.SLEEP_TIME_BETWEEN_KINESIS_STAGES)  # can be done in a better way.
        time.sleep(constants.SLEEP_TIME_BETWEEN_KINESIS_STAGES)  # can be done in a better way.
        time.sleep(constants.SLEEP_TIME_BETWEEN_KINESIS_STAGES)  # can be done in a better way.
        time.sleep(constants.SLEEP_TIME_BETWEEN_KINESIS_STAGES)  # can be done in a better way.
        time.sleep(constants.SLEEP_TIME_BETWEEN_KINESIS_STAGES)  # can be done in a better way.
        time.sleep(constants.SLEEP_TIME_BETWEEN_KINESIS_STAGES)  # can be done in a better way.

    def get_stream_status(self, conn, stream_name):
        """Query this provided connection object for the provided stream's status.
        :type conn: boto.kinesis.layer1.KinesisConnection
        :param conn: A connection to Amazon Kinesis
        :type stream_name: str
        :param stream_name: The name of a stream.
        :rtype: str
        :return: The stream's status"""
        r = conn.describe_stream(StreamName=stream_name)
        description = r.get('StreamDescription')
        return description.get('StreamStatus')

    def wait_for_stream(self, conn, stream_name):
        """Wait for the provided stream to become active.
        :type conn: boto.kinesis.layer1.KinesisConnection
        :param conn: A connection to Amazon Kinesis
        :type stream_name: str
        :param stream_name: The name of a stream."""
        status = self.get_stream_status(conn, stream_name)
        while status != 'ACTIVE':
            print('{stream_name} has status: {status}, sleeping for {secs} seconds'.format(
                stream_name=stream_name,
                status=status,
                secs=constants.SLEEP_TIME_BETWEEN_KINESIS_STAGES))
            time.sleep(constants.SLEEP_TIME_BETWEEN_KINESIS_STAGES)
            status = self.get_stream_status(conn, stream_name)

    def get_anomaly_score(self, days, data, key):
        timestamp = datetime.datetime.utcnow()
        # time.sleep(1)
        # for index, row in data.iterrows():
        #     payload = {
        #         'age': int(row['days']),
        #         'afr': float(data),
        #         # 'afr': float(row['cum_afr']),
        #         'key': key
        #     }

        payload = {
            'age': days,
            'afr': float(data),
            # 'afr': float(row['cum_afr']),
            'key': key
        }

        self.kinesis_client.put_record(StreamName=self.input_stream, Data=json.dumps(payload),
                                       PartitionKey='cum_afr')
        #
        # print("Inserted " + str(len(data)) + " records into Kinesis.")
        # print("Waiting 10 secs. to make sure records are inserted.")
        # time.sleep(constants.SLEEP_TIME_BETWEEN_KINESIS_STAGES / 2)
        #
        # shard_iterator = self.kinesis_client.get_shard_iterator(StreamName=self.output_stream,
        #                                                         ShardId="shardId-000000000000",
        #                                                         ShardIteratorType="AT_TIMESTAMP",
        #                                                         Timestamp=timestamp)
        # results_json = self.kinesis_client.get_records(ShardIterator=shard_iterator["ShardIterator"])
        # records = results_json["Records"]
        # FIXME: get a way to issue anomaly tests on a daily basis
        backoff = 1
        while True:
            time.sleep(0.3 * backoff)
            if self._last_record_sequence_number is None:
                shard_iterator = self.kinesis_client.get_shard_iterator(StreamName=self.output_stream,
                                                                        ShardId="shardId-000000000000",
                                                                        ShardIteratorType="TRIM_HORIZON")
                                                                        # Timestamp=timestamp)
            else:
                shard_iterator = self.kinesis_client.get_shard_iterator(StreamName=self.output_stream,
                                                                        ShardId="shardId-000000000000",
                                                                        ShardIteratorType="AFTER_SEQUENCE_NUMBER",
                                                                        StartingSequenceNumber=self._last_record_sequence_number)

            # shard_iterator = self.kinesis_client.get_shard_iterator(StreamName=self.output_stream,
            #                                                         ShardId="shardId-000000000000",
            #                                                         ShardIteratorType="LATEST")

            results_json = self.kinesis_client.get_records(ShardIterator=shard_iterator["ShardIterator"], Limit=1)
            records = results_json["Records"]
            if len(records) == 1:
                break
            backoff += 1
        data_vs_anomalies = []
        print("Fetched " + str(len(records)) + " records from Kinesis.")
        i = 0
        for r in records:
            split_results = r["Data"].decode("utf-8").rstrip().split(",")
            self._last_record_sequence_number = r["SequenceNumber"]
            self._anomaly_df.loc[self._iloc_num] = [days, data, float(split_results[1])]
            self._iloc_num += 1
            print([days, data, float(split_results[1])])
            if float(split_results[1]) > constants.ANOMALY_SCORE_SENSITIVITY:
                # we have found an anomaly, flag it!
                # data_vs_anomalies.append((int(data.iloc[i]['days']), float(split_results[1])))
                data_vs_anomalies.append((int(days), float(split_results[1])))
            i += 1

        return data_vs_anomalies
