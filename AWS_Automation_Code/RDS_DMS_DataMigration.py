'''
Script perform below actions.
1.  Create S3 bucket and upload .bak file to s3.
2.  Create a security group for SQL instance with SQL 1433 port open.
    (SQL DB instance will sit behind this security group.)
3.  Create a service role for RDS service. This role wii be used to allow access on S3 bucket created in step 1.
4.  Create IAM policy for S3 bucket access and attach it to service role created in above step, to enable
    RDS service access S3 bucket.
5. Create Option Group for DB instance with  option setting SQLSERVER_BACKUP_RESTORE pointing to service role
    created in step 3.
6.  Create a DB instance and associate it with option group created in step 5.

Delete List : S3 Bucket, security group, role, policy, option group, DB instance
Restore command : exec msdb.dbo.rds_restore_database @restore_db_name='Gapsql01' @s3_arn_to_restore_from='arn:aws:s3:::gapsqldbbucket/apr.bak'
exec msdb.dbo.rds_task_status

git clone https://github.com/AshpakMulani/AWS_Python_Boto3_Automation.git
git status
git add <folder/file>
git commit
git push/pull
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
source_endpoint = 'source_endpoint'
target_endpoint = 'target_endpoint'
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
                "table-name": "%projectdeliveries"
            },
            "rule-action": "include"
}
    ]
}

# =============================================================================
#  Create a DMS service role which will provide access for DMS service on VPC
# =============================================================================
try:
    function.create_dms_vpc_role(dms_role, policy_document)
except ClientError as e:
    print("Error occurred while crating DMS service role : " + e.response['Error']['Message'])



# =============================================================================
#  Attach policy to role created above. This will enable DMS to access VPC
# =============================================================================
try:
    function.attach_policy_role(dms_role, policy_arn)
except ClientError as e:
    print("Error occurred while attaching policy to role : " + e.response['Error']['Message'])



# =============================================================================
#  Create a replciaiton instace
# =============================================================================
try:
    response = function.create_replicaiton_instance(replication_instance_name)
    replicaiton_instance_arn = response['ReplicationInstances'][0]['ReplicationInstanceArn']
    #documentation of AWs is wrong, it says it returns Dictionary of name 'ReplicaitonInstance'
    #but in reality it returns Disctionary 'ReplciationIstances' with child disctionary containing
    #status of every replciaiton instance. Hence we are choosing [0] which is first instance what we created.
except ClientError as e:
    print("Error occurred while attaching policy to role : " + e.response['Error']['Message'])
print('returned from replication instance creation..')

# =============================================================================
#  Create source and target endpoints
# =============================================================================
try:
    response = function.create_dms_endpoint(source_endpoint, 'source', source_name, db_name, db_user, db_password)
    source_arn = response['Endpoint']['EndpointArn']
except ClientError as e:
    print("Error occurred while creating source endpoint: " + e.response['Error']['Message'])

try:
    response = function.create_dms_endpoint(target_endpoint, 'target', target_name, db_name, db_user, db_password)
    target_arn = response['Endpoint']['EndpointArn']
except ClientError as e:
    print("Error occurred while creating target endpoint: " + e.response['Error']['Message'])




# =============================================================================
#  Create replication task
# =============================================================================
try:
    response = function.create_dms_replicaiton_task(replication_task_name, source_arn, target_arn, replicaiton_instance_arn, table_mapping)
except ClientError as e:
    print("Error occurred while creating replication task: " + e.response['Error']['Message'])






