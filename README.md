# AWS Glue Job Beacon

Introduced new Amazon CloudWatch metrics for AWS Glue that allow you immediate awareness of job completion, failure,
duration, etc. This is a simple solution that can be deployed in minutes and requires no changes to your existing Glue
Jobs.

![status](https://github.com/vitalibo/glue-beacon/actions/workflows/ci.yaml/badge.svg)

## Usage

Deploy the CloudFormation stack using the button below.

[![Launch Stack](https://s3.amazonaws.com/cloudformation-examples/cloudformation-launch-stack.png)](https://console.aws.amazon.com/cloudformation/home?#/stacks/new?templateURL=https://vitalibo-public-us-east-1.s3.amazonaws.com/glue-beacon/latest/stack.template)

Provide the following parameters:

- **Dimensions** - Comma separated list of dimensions to be added to the metrics. Values for each dimension will be
  extracted from the job tags. If the job does not have a tag with the specified name, the dimension will have `Unknown`
  value. This parameter is optional.

Once the stack is deployed, you will have a new CloudWatch namespace `Glue` with the following metrics:

Invocation metrics are binary indicators of the outcome invocation.

- **Started** - The number of times that you job started execution, including successful and unsuccessful invocations.
- **Succeeded** - The number of job executions that was successfully finished.
- **Failed** - The number of job executions that result is an error.
  To calculate the error rate, divide the value of **Failed** by sum values **Succeeded** and **Failed**.
- **Timeout** - The number of job executions that result in a timeout.
- **Stopped** - The number of job executions that was manually stopped.

Performance metrics provide performance details about a single run.

- **Duration** – The amount of time that your job was executed (in Seconds).

Note that the timestamp on all except **Started** the above metrics reflects when the job was completed, not when the
started.
