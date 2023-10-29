import importlib
from datetime import datetime
from unittest import mock


@mock.patch("boto3.session.Session")
def test_handler(mock_session_class):
    mock_session = mock.Mock()
    mock_session_class.return_value = mock_session
    mock_glue = mock.Mock()
    mock_glue.get_job_run.return_value = create_job_run()
    mock_glue.get_tags.return_value = create_tags()
    mock_cloudwatch = mock.Mock()
    mock_session.client.side_effect = [mock_glue, mock_cloudwatch]

    with mock.patch.dict('os.environ', {'TAGS': 'Environment'}):
        aws_lambda = importlib.import_module('lambda')
        aws_lambda.handler(create_event(), mock.Mock())

    mock_glue.get_job_run.assert_called_once_with(
        JobName='untitled-job',
        RunId='jr_5d92f3974644a042b9d382c165255fa8618b22708c6c098adc4cdba95553bd9e'
    )
    mock_glue.get_tags.assert_called_once_with(
        ResourceArn='arn:aws:glue:us-east-1:715737992409:job/untitled-job'
    )
    assert mock_cloudwatch.put_metric_data.call_args_list == [
        mock.call(
            Namespace='Glue',
            MetricData=[
                create_metric(
                    MetricName='Started',
                    Timestamp=datetime.fromisoformat('2020-09-30T18:29:03Z')),
                create_metric(
                    MetricName='Succeeded',
                    Timestamp=datetime.fromisoformat('2020-09-30T18:31:05Z')),
                create_metric(
                    MetricName='Duration',
                    Timestamp=datetime.fromisoformat('2020-09-30T18:31:05Z'),
                    Value=122, Unit='Seconds')
            ]
        )
    ]


def create_event(**kwargs):
    return {
        **{
            'version': '0',
            'id': '96e8a234-3c2d-5ce6-3acd-2b8f41ee9110',
            'detail-type': 'Glue Job State Change',
            'source': 'aws.glue',
            'account': '715737992409',
            'time': '2020-09-30T18:31:07Z',
            'region': 'us-east-1',
            'resources': [],
            'detail': {
                **{
                    'jobName': 'untitled-job',
                    'severity': 'INFO',
                    'state': 'SUCCEEDED',
                    'jobRunId': 'jr_5d92f3974644a042b9d382c165255fa8618b22708c6c098adc4cdba95553bd9e',
                    'message': 'Job run succeeded'
                },
                **kwargs.pop('detail', {})
            }
        },
        **kwargs
    }


def create_job_run(**kwargs):
    return {
        'JobRun': {
            **{
                'Id': 'jr_5d92f3974644a042b9d382c165255fa8618b22708c6c098adc4cdba95553bd9e',
                'Attempt': 0,
                'JobName': 'untitled-job',
                'StartedOn': datetime.fromisoformat('2020-09-30T18:29:03Z'),
                'LastModifiedOn': datetime.fromisoformat('2020-09-24T12:01:43Z'),
                'CompletedOn': datetime.fromisoformat('2020-09-30T18:31:05Z'),
                'JobRunState': 'SUCCEEDED',
                'PredecessorRuns': [],
                'AllocatedCapacity': 2,
                'ExecutionTime': 122,
                'Timeout': 5,
                'MaxCapacity': 2.0,
                'WorkerType': 'G.1X',
                'NumberOfWorkers': 2,
                'LogGroupName': '/aws-glue/jobs',
                'GlueVersion': '4.0',
                'ExecutionClass': 'STANDARD'
            },
            **kwargs
        }
    }


def create_tags(**kwargs):
    return {
        'Tags': {
            **{
                'Environment': 'dev',
                'CostCenter': 'data-platform',
                'Owner': 'james'
            },
            **kwargs
        }
    }


def create_metric(**kwargs):
    return {
        **{
            'MetricName': 'Started',
            'Dimensions': [
                {
                    'Name': 'JobName',
                    'Value': 'untitled-job'
                },
                {
                    'Name': 'Environment',
                    'Value': 'dev'
                }
            ],
            'Timestamp': datetime.fromisoformat('2020-09-30T18:31:05Z'),
            'Value': 1,
            'Unit': 'Count'
        },
        **kwargs
    }
