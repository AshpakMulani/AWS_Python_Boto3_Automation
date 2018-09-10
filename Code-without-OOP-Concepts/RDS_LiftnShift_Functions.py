import boto3
import json
import time




ec2client = boto3.client('ec2')
rdsclient = boto3.client('rds')
iamclient = boto3.client('iam')
s3client = boto3.client('s3')



def create_security_group(security_group_name,vpc_id):
    response = ec2client.create_security_group\
    (
        Description='Security Group for RDS instance created for Lift and Shit migration.',
        GroupName= security_group_name,
        VpcId=vpc_id,
        DryRun=False
    )
    return response



def security_group_ingress(security_group_id,port,protocol,cidr_block):
    response = ec2client.authorize_security_group_ingress\
    (
    GroupId=security_group_id,
    IpPermissions=
        [
            {
                'FromPort': port,
                'ToPort': port,
                'IpProtocol': protocol,
                'IpRanges':
                [
                     {
                     'CidrIp': cidr_block,
                     'Description': 'Allow all traffic for SQL'
                     }
                ]
            }
        ]
    )
    return response




def create_role(rolename,policydocument):
    response = iamclient.create_role\
        (
            RoleName=rolename,
            AssumeRolePolicyDocument=json.dumps(policydocument)
        )
    time.sleep(30)  # this wait is necessary, because even though role gets created immediately, it takes some time for
                    # AWS to make it available for other resourcecs.
    return response



def create_policy(policyname, policydocument):
    response = iamclient.create_policy\
    (
        PolicyName= policyname,
        PolicyDocument=json.dumps(policydocument),
        Description='policy to allow RDS service access S3. This policy will be used in option group for RDS instance'
    )
    return response



def attach_policy_to_role(rolename,policy_arn):
    response = iamclient.attach_role_policy\
    (
        RoleName= rolename,
        PolicyArn=policy_arn
    )
    return response



def create_and_configure_optiongroup(option_group_name,role_arn):
    option_group = rdsclient.create_option_group \
        (
            OptionGroupName=option_group_name + '-ex',
            EngineName='sqlserver-ex',
            MajorEngineVersion='14.00',
            OptionGroupDescription='option group for S3 backup restore automated'
        )
    # Modify Option group to have SQLSERVER_BACKUP_RESTORE referring to IAM role providing RDS access to S3.
    response = rdsclient.modify_option_group \
            (
            OptionGroupName=option_group_name + '-ex',
            OptionsToInclude=
            [
                {
                    'OptionName': 'SQLSERVER_BACKUP_RESTORE',
                    'OptionSettings':
                        [
                            {
                                'Name': 'IAM_ROLE_ARN',
                                'Value': role_arn,
                            },
                        ]
                },
            ],
            ApplyImmediately=True
        )
    return response

def create_SQL_instance(instance_name, security_group_id):
    response = rdsclient.create_db_instance\
    (
        DBInstanceIdentifier= instance_name,
        AllocatedStorage=20,
        DBInstanceClass='db.t2.micro',
        Engine='sqlserver-ex',
        MasterUsername='sa',
        MasterUserPassword='Password12',
        VpcSecurityGroupIds=
        [
            security_group_id
        ],
        AvailabilityZone='us-east-1d',
        DBSubnetGroupName='default',
        MultiAZ=False,
        EngineVersion='14.00.3015.40.v1',
        LicenseModel='license-included',
        StorageType='gp2',
        BackupRetentionPeriod=0,
        OptionGroupName=instance_name +'-ex'

    )
    return response


def create_bucket(bucketname):
    response = s3client.create_bucket \
    (
            ACL='public-read-write',
            Bucket= bucketname
    )
    waiter = s3client.get_waiter('bucket_exists')
    waiter.wait(Bucket=bucketname)
    return response



def uplaod_file_bucket(filepath, bucketname, filekey):
    response = s3client.upload_file(filepath, bucketname, filekey)
    waiter = s3client.get_waiter('object_exists')
    waiter.wait(Bucket=bucketname, Key=filekey)
    return response
