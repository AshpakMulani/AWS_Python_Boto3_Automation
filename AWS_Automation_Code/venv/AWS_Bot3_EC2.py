### not tested at all###
import boto3

ec2client = boto3.client('ec2')

ec2client=



waiter = ec2client.get_waiter('instance_running')

waiter.wait(
    Filters=[
        {
            'Name': 'string',
            'Values': [
                'string',
            ]
        },
    ],
    InstanceIds=[
        'string',
    ],

    WaiterConfig={
        'Delay': 10,
        'MaxAttempts': 123
    }
)