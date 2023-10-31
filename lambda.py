import json
import logging
import os

import boto3

logging.basicConfig(
    level=os.environ.get('LOG_LEVEL', 'INFO'),
    format='%(levelname)-8s %(message)s'
)

session = boto3.session.Session()
glue = session.client('glue')
cloudwatch = session.client('cloudwatch')

DIMENSIONS = []
if os.environ.get('DIMENSIONS', '') != '':
    DIMENSIONS = os.environ['DIMENSIONS'].split(',')


def handler(event, context):  # pylint: disable=unused-argument
    """
    Entry point for AWS Lambda
    """

    logging.info(json.dumps(event))
    job_run = job_run_details(event)
    logging.info(job_run)

    dimensions = [
        {
            'Name': 'JobName',
            'Value': job_run['JobName']
        },
        *[
            {
                'Name': dimension,
                'Value': job_run['Tags'].get(dimension, 'Unknown')
            }
            for dimension in DIMENSIONS
        ]
    ]

    metrics_data = [
        {
            'MetricName': 'Started',
            'Dimensions': dimensions,
            'Timestamp': job_run['StartedOn'],
            'Value': 1,
            'Unit': 'Count'
        },
        {
            'MetricName': job_run['JobRunState'].capitalize(),
            'Dimensions': dimensions,
            'Timestamp': job_run['CompletedOn'],
            'Value': 1,
            'Unit': 'Count'
        },
        {
            'MetricName': 'Duration',
            'Dimensions': dimensions,
            'Timestamp': job_run['CompletedOn'],
            'Value': job_run['ExecutionTime'],
            'Unit': 'Seconds'
        }
    ]

    cloudwatch.put_metric_data(
        Namespace='Glue',
        MetricData=metrics_data
    )


def job_run_details(event):
    """
    Get details of the job run
    """

    job_name = event['detail']['jobName']
    job_arn = f'arn:aws:glue:{event["region"]}:{event["account"]}:job/{job_name}'

    response = glue.get_job_run(JobName=job_name, RunId=event['detail']['jobRunId'])
    job_run = response['JobRun']
    response = glue.get_tags(ResourceArn=job_arn)
    job_run['Tags'] = response['Tags']

    return job_run
