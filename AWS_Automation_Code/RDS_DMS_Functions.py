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
    #since there is no waiter function implimentation for replciaiton instance in boto3
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





def test_connection_for_endpoint(replication_instance_arn, endpoint_arn):
    response = dmsclient.test_connection(
        ReplicationInstanceArn=replication_instance_arn,
        EndpointArn=endpoint_arn
    )
    # since there is no waiter function implementation for replication instance in bot3
    # we need to write custom code to wait for connection to be available.
    time.sleep(5)
    while 1:
        time.sleep(10)
        response = dmsclient.describe_connections(
            Filters=[
                {
                    'Name': 'endpoint-arn',
                    'Values': [
                        endpoint_arn,
                    ]
                },
            ]

        )

        if response['Connections'][0]['Status'].lower() == 'successful':
            return response

    return response





def refresh_schema(endpoint_arn, replicaiton_instance_arn):
    response = dmsclient.refresh_schemas(
        EndpointArn=endpoint_arn,
        ReplicationInstanceArn=replicaiton_instance_arn
    )
    # since there is no waiter function implementation for replication instance in boto3
    # we need to write custom code to wait for endpoint to fetch source DB schema.
    while 1:
        time.sleep(5)
        response = dmsclient.describe_refresh_schemas_status(
            EndpointArn=endpoint_arn
        )

        if response['RefreshSchemasStatus']['Status'].lower() == 'successful':
            return response





def create_dms_replicaiton_task(task_name, source_arn, target_arn, repliaction_insatance_arn, table_mapping):
    response = dmsclient.create_replication_task\
    (
        ReplicationTaskIdentifier=task_name,
        SourceEndpointArn=source_arn,
        TargetEndpointArn=target_arn,
        ReplicationInstanceArn=repliaction_insatance_arn,
        MigrationType='full-load',
        TableMappings=json.dumps(table_mapping),

    )
    # since there is no waiter function implementation for replication task in boto3
    # we need to write custom code to wait for replication task to up and running
    time.sleep(5)
    while 1:
        time.sleep(10)
        response = dmsclient.describe_replication_tasks(
            Filters=[
                {
                    'Name': 'replication-task-id',
                    'Values': [
                        task_name,
                    ]
                },
            ],

        )

        replication_task_arn = response['ReplicationTasks'][0]['ReplicationTaskArn']

        #Start replication task to migrate data once it is ready.
        if response['ReplicationTasks'][0]['Status'].lower() == 'ready':
            dmsclient.start_replication_task(
                ReplicationTaskArn=replication_task_arn,
                StartReplicationTaskType='start-replication')
            return response
    return response


