'''
Script can be used for preparing AWS for SQL DB restore from .bak file.
Requirements :  AWS automation User should be added to Admin group for IAM, EC2 and RDS, S3.
                Create a s3 bucket with name gapsqlbucket.

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
'''

import RDS_LiftnShift_Functions as function
from botocore.exceptions import ClientError
import boto3

# ======================================================================
# Initialization section
# ======================================================================
rdsclient = boto3.client('rds')
dbinstancename =  'gapsql01'
rdsecuritygroup='RDSLiftnShift'
rdsvpcrole='rds-vpc-role'
rds_s3bucket_access_policy = 'RDS_S3_Access_Policy'
vpc_id = 'vpc-8bfe36f1'
bucket_name = 'gapsqldbbucket'
backup_path='C:/Users/ashfaque_mulani/Desktop/APR_2018-08-15_13-00.bak'

# ======================================================================
#  Create S3 bucket and uplaod DB backup file to bucket.
# ======================================================================
try:
    function.create_bucket(bucket_name)
except ClientError as e:
    print("Error occurred while crating s3 bucket : " + e.response['Error']['Message'])


try:
    function.uplaod_file_bucket(backup_path, bucket_name, 'apr.bak')
except ClientError as e:
    print("Error occurred while uploading file to s3 bucket : " + e.response['Error']['Message'])



# ======================================================================
# Create a security group for RDS instance.
# and open port 1433 to allow SQL DB using management studio.
# This security group will be used while creating SQL instance.
# ======================================================================

try:
    rds_security_groupid = function.create_security_group(rdsecuritygroup,vpc_id)['GroupId']
except ClientError as e:
    print("Error occurred while crating security group : " + e.response['Error']['Message'])




# ======================================================================
# Add Rule for security group to allow only DB traffic for DB instance.
# ======================================================================
try:
    function.security_group_ingress(rds_security_groupid, 1433, 'TCP', '0.0.0.0/0')
    function.security_group_ingress(rds_security_groupid, 1433, 'TCP', '0.0.0.0/0')
except ClientError as e:
    print("Error occurred while crating security group : " + e.response['Error']['Message'])


# ======================================================================
# Create IAM Role to allow RDS to access S3
# ======================================================================
rdspolicydocument=\
{
    "Version":"2012-10-17",
    "Statement":
    [
      {
         "Effect":"Allow",
         "Principal":
        {
            "Service":"rds.amazonaws.com"
        },
         "Action":"sts:AssumeRole"
      }
    ]
}


rds_s3bucket_access_policydocument=\
{
    "Version": "2012-10-17",
    "Statement":
    [
        {
            "Effect": "Allow",
            "Action":
            [
                "s3:ListBucket",
                "s3:GetBucketLocation"
            ],
            "Resource":
            [
                "arn:aws:s3:::gapsqldbbucket"
            ]
        },
        {
            "Effect": "Allow",
            "Action":
            [
                "s3:GetObjectMetaData",
                "s3:GetObject",
                "s3:PutObject",
                "s3:ListMultipartUploadParts",
                "s3:AbortMultipartUpload"
            ],
            "Resource":
            [
                 "arn:aws:s3:::gapsqldbbucket/*"
            ]
        }
    ]
}

try:
    role_arn = function.create_role(rdsvpcrole, rdspolicydocument)['Role']['Arn']
except ClientError as e:
    print("Error occurred while crating vpc role : " + e.response['Error']['Message'])



try:
    policy_arn = function.create_policy(rds_s3bucket_access_policy,rds_s3bucket_access_policydocument)['Policy']['Arn']
except ClientError as e:
    print("Error occurred while crating policy : " + e.response['Error']['Message'])



try:
   function.attach_policy_to_role(rdsvpcrole,policy_arn)
except ClientError as e:
    print("Error occurred while attaching policy to role : " + e.response['Error']['Message'])


try:
    function.create_and_configure_optiongroup(dbinstancename, role_arn)
except ClientError as e:
    print("Error occurred while creating and configuring option group : " + e.response['Error']['Message'])

# ======================================================================
# Create DB instance and wait until AWS process the request.
# ======================================================================

try:
    function.create_SQL_instance(dbinstancename,rds_security_groupid)
except ClientError as e:
    print("Error occurred while creating DB instance : " + e.response['Error']['Message'])


#Wait for DB instance to be provisioned.
rdswaiter = rdsclient.get_waiter('db_instance_available')

rdswaiter.wait\
(
    DBInstanceIdentifier = dbinstancename,
    WaiterConfig=
    {
        'Delay': 10,
        'MaxAttempts': 500
    }
)

print('DB instance Created..!!')
