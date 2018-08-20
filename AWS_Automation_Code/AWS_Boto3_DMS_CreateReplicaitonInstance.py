import boto3
import time
dms = boto3.client('dms')

response = dms.create_replication_instance(
    ReplicationInstanceIdentifier='MyReplicationInstance',
    AllocatedStorage=5,
    ReplicationInstanceClass='dms.t2.micro',
    AvailabilityZone='us-east-1d',
    MultiAZ=False,
    Tags=[
        {
            'Key': 'Category',
            'Value': 'Testing'
        },
    ],
    PubliclyAccessible=True
)


while 1 :
   time.sleep(10)
   response = dms.describe_replication_instances(
        Filters=[
            {
                'Name': 'replication-instance-id',
                'Values': [
                    'myreplicationinstance',
                ]
            },
        ],

    )
   if response['ReplicationInstances'][0]['ReplicationInstanceStatus'].lower() == 'available':
    break


print('Instance is now available')