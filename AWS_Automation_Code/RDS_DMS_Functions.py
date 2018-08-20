import time
import boto3
import json

iamclient = boto3.client('iam')
dmsclient = boto3.client('dms')


def create_dms_vpc_role(role_name, policy_document):
    response = iamclient.create_role\
    (
        RoleName=role_name,
        AssumeRolePolicyDocument=json.dumps(policy_document)
    )

def attach_policy_role(role_name, policy_arn):
   response = iamclient.attach_role_policy\
    (
        PolicyArn=policy_arn,
        RoleName=role_name,
    )



def create_replicaiton_instance(instance_name):
    response = dmsclient.create_replication_instance(
        ReplicationInstanceIdentifier= instance_name,
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
    #since there is no waiter function implimentation for replciaiton instance in bot3
    # we need to write custom code to wait for instance to be available.
    time.sleep(5)
    while 1:
        time.sleep(10)
        response = dmsclient.describe_replication_instances(
            Filters=[
                {
                    'Name': 'replication-instance-id',
                    'Values': [
                        instance_name,
                    ]
                },
            ],

        )
        print(response['ReplicationInstances'][0]['ReplicationInstanceStatus'].lower())
        if response['ReplicationInstances'][0]['ReplicationInstanceStatus'].lower() == 'available':
            return response
    return response


def create_dms_endpoint(endpoint_name, type, server_name, db_name, user_name, password):
    response = dmsclient.create_endpoint\
    (
        EndpointIdentifier=endpoint_name,
        EndpointType=type,
        EngineName='sqlserver',
        Username=user_name,
        Password=password,
        ServerName=server_name,
        Port=1433,
        DatabaseName=db_name
    )
    return response


def create_dms_replicaiton_task(task_name, source_arn, target_arn, repliaction_insatance_arn, table_mapping):
    response = dmsclient.create_replication_task\
    (
        ReplicationTaskIdentifier=task_name,
        SourceEndpointArn=source_arn,
        TargetEndpointArn=target_arn,
        ReplicationInstanceArn=repliaction_insatance_arn,
        MigrationType='full-load-and-cdc',
        TableMappings=table_mapping,

    )
    return response
