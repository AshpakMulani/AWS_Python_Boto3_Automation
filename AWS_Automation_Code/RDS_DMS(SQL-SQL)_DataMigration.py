'''
==================== Data migration SQL-SQL using DMS ====================================
1. Create a DMS service role and attach a policy to enable access to
    VPC  This policy helps DMS service to add resources in VPC like replicaiton instance, endpoints, replciaiton task
2. Create a replication instance
3. Create and configure source and replication endpoints
4. Create a replication task and start the task using source and target endpoint.

Before running script, source and target SQL DB has to be in running state.

'''

import RDS_DMS_Functions as function
from botocore.exceptions import ClientError


# ======================================================================
# Initialization section
# ======================================================================
dms_role = 'dms-vpc-role-test'
replication_instance_name = 'myreplciaitoninstance'
replication_task_name = 'myreplicaitontask'
source_name='gapsql01.c53u7d8l6zis.us-east-1.rds.amazonaws.com'
target_name='ec2-52-90-193-243.compute-1.amazonaws.com\AWSGAPSQL01'
source_endpoint = 'sourceendpoint'
target_endpoint = 'targetendpoint'
db_name='gapsql01'
db_user='sa'
db_password='Password12'

policy_arn = 'arn:aws:iam::aws:policy/service-role/AmazonDMSVPCManagementRole'
policy_document = \
{
    "Version":"2012-10-17",
    "Statement":[
      {
         "Effect":"Allow",
         "Principal":{
            "Service":"dms.amazonaws.com"
         },
         "Action":"sts:AssumeRole"
      }
   ]
}


table_mapping = \
{
    "rules":
    [
        {
            "rule-type": "selection",
            "rule-id": "1",
            "rule-name": "1",
            "object-locator": {
                "schema-name": "dbo",
                "table-name": "%projectdeliveries%"
            },
            "rule-action": "include"
}
    ]
}

# =============================================================================
#  Create a DMS service role which will provide access for DMS service on VPC
# =============================================================================
try:
    print("Crating DMS VPC role...")
    function.create_dms_vpc_role(dms_role, policy_document)
    print("DMS VPC Role created successfully ")
except ClientError as e:
    print("Error occurred while crating DMS service role : " + e.response['Error']['Message'])

# =============================================================================
#  Attach policy to role created above. This will enable DMS to access VPC
# =============================================================================
try:
    print("Attaching VPC access policy to DMS VPS Role...")
    function.attach_policy_role(dms_role, policy_arn)
    print("Policy attached successfully ")
except ClientError as e:
    print("Error occurred while attaching policy to role : " + e.response['Error']['Message'])



# =============================================================================
#  Create a replication instance
# =============================================================================
try:
    print("Creating Replication Instance... ")
    response = function.create_replicaiton_instance(replication_instance_name)
    replicaiton_instance_arn = response['ReplicationInstances'][0]['ReplicationInstanceArn']
    print("Replication Instance created and is in Ready state.")
    #AWS documentation is incorrect,  it says create_replciaiton_instance returns Dictionary of name 'ReplicaitonInstance'
    #but in reality it returns Disctionary 'ReplciationIstances' with child disctionary containing
    #status of every replciaiton instance. Hence we are choosing [0] which is first instance what we created.
except ClientError as e:
    print("Error occurred while attaching policy to role : " + e.response['Error']['Message'])


# =============================================================================
#  Create source and target endpoints
# =============================================================================
try:
    print("Creating Source endpoint... ")
    response = function.create_dms_endpoint(source_endpoint, 'source', source_name, db_name, db_user, db_password)
    source_arn = response['Endpoint']['EndpointArn']
    # This is really important step (check connection & refresh schema)before creating
    # replication task. This ensures source endpoint can speak to DB and fetches DB schema beforehand.
    # If we create replication task before testing connection, it wont be able
    # to fetch schema details from DB and will Fail during migration.
    print("Source endpoint connection test in progress... ")
    response = function.test_connection_for_endpoint(replicaiton_instance_arn, source_arn)
    print("Source endpoint schema refresh in progress... ")
    response = function.refresh_schema(source_arn, replicaiton_instance_arn)
    print('Source endpoint is created successfully.')
except ClientError as e:
    print("Error occurred while creating and testing source endpoint: " + e.response['Error']['Message'])

try:
    print("Creating target endpoint... ")
    response = function.create_dms_endpoint(target_endpoint, 'target', target_name, db_name, db_user, db_password)
    target_arn = response['Endpoint']['EndpointArn']
    print('target endpoint is created successfully.')
    # No need to test connection for target unlike source, because replication task
    # does not fetch schema of target while moving data.
except ClientError as e:
    print("Error occurred while creating target endpoint: " + e.response['Error']['Message'])



# =============================================================================
# Create replication task. This will start data migration.
# =============================================================================
try:
    print('Creating Replication task....')
    response = function.create_dms_replicaiton_task(replication_task_name, source_arn, target_arn, replicaiton_instance_arn, table_mapping)
    print('Replication task created and data migration has been started.')
except ClientError as e:
    print("Error occurred while creating replication task: " + e.response['Error']['Message'])

