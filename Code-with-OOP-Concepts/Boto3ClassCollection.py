import abc
import boto3
import json
import time
import types
import Core as Core


ec2client = boto3.client('ec2')
rdsclient = boto3.client('rds')
iamclient = boto3.client('iam')
s3client = boto3.client('s3')
dmsclient = boto3.client('dms')





# Creating skeleton using abstract class for other classes related to IAM
class IAMCore(abc.ABC):

    @abc.abstractmethod
    def create_role(self, **kwargs):
        pass

    @abc.abstractmethod
    def create_policy(self, **kwargs):
        pass

    @abc.abstractmethod
    def attach_policy(self, **kwargs):
        pass


class IAMClass(IAMCore): #Inheriting from IAMCore class to enforce skeleton.

    @Core.error_handler_decorator
    def create_role(self, **kwargs):
        '''
        :description : Create IAM Role.
        :param kwargs: rolename=<role_name>, policydocument=<Policy JSON>
        :return: dict.
        For more information refer https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/iam.html#IAM.Client.create_role
        '''
        response = iamclient.create_role(
                RoleName=kwargs['rolename'],
                AssumeRolePolicyDocument=json.dumps(kwargs['policydocument'])
            )
        time.sleep(30)  # this wait is necessary, because even though role gets created immediately, it takes
                        #  some time for AWS to make it available for other resourcecs.
        return response


    @Core.error_handler_decorator
    def create_policy(self, **kwargs):
        '''
        :description : Create IAM Policy.
        :param kwargs: policyname=<policy name>, description=<policy description>, policydocument=<Policy JSON>
        :return: dict.
        For more information refer https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/iam.html#IAM.Client.create_policy
        '''
        return iamclient.create_policy(
                PolicyName=kwargs['policyname'],
                PolicyDocument=json.dumps(kwargs['policydocument']),
                Description=kwargs['description'])


    @Core.error_handler_decorator
    def attach_policy_to_role(self, **kwargs):
        '''
        :description : Attach IAM policy to IAM role.
        :param kwargs: policyarn=<policy ARN>, rolename=<role name to attach give policy>
        :return: dict.
        For more information refer https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/iam.html#IAM.Client.attach_role_policy
        '''
        response = iamclient.attach_role_policy(
                RoleName=kwargs['rolename'],
                PolicyArn=kwargs['policy_arn'])
        return response




# Creating base class for EC2 operations

class EC2Class():

    @Core.error_handler_decorator
    def create_security_group(self, security_group_name, vpc_id, description):
        '''
        :description : Create security group in specified VPC.
        :param : security_group_name, vpc_id, description
        :return: dict.
        For more information refer https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ec2.html#EC2.Client.create_security_group
        '''
        return ec2client.create_security_group (Description=description, GroupName=security_group_name, VpcId=vpc_id, DryRun=False)



    @Core.error_handler_decorator
    def create_security_group_ingress(self, security_group_id, port, protocol, cidr_block, description):
        '''
        :description : Add inbound rule to security group
        :param : security_group_id, port, protocol, cidr_block, description
        :return: dict.
        For more information refer https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ec2.html#EC2.Client.authorize_security_group_ingress
        '''

        response = ec2client.authorize_security_group_ingress \
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
                                    'Description': description
                                }
                            ]
                    }
                ]
            )
        return response






# Creating base class for s3 operations

class S3Class():

    @Core.error_handler_decorator
    def create_bucket(bucketname):
        '''
        :description : Create a new public bucket in default region N.virginia
        :param : bucket name
        :return: dict.
        For more information refer https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.Client.create_bucket
        '''
        response = s3client.create_bucket(
                ACL='public-read-write',
                Bucket=bucketname
            )

        #wait until bucket is ready to use after creation.
        waiter = s3client.get_waiter('bucket_exists')
        waiter.wait(Bucket=bucketname)
        return response

    @Core.error_handler_decorator
    def uplaod_file_bucket(filepath, bucketname, filekey):
        '''
        :description : upload file to bucket.
        :param : filepath, bucketname, filekey
        :return: dict.
        For more information refer  https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.Client.upload_file
        '''
        response = s3client.upload_file(filepath, bucketname, filekey)

        #wait until object finishes uplaod.
        waiter = s3client.get_waiter('object_exists')
        waiter.wait(Bucket=bucketname, Key=filekey)
        return response




# Creating base class for DB operations

class RDSClass():

    @Core.error_handler_decorator
    def create_SQL_instance(instance_name, security_group_id, dbinstanceclass='db.t2.micro', engine='sqlserver-ex'\
                            , masteruser='sa', masteruserpassword='Password12', availabilityzone='us-east-1d',\
                            engineversion='14.00.3015.40.v1', licensemodel='license-included'):
        '''
        :description : create a SQL instance.
        :param : instance_name, security_group_id, dbinstanceclass='db.t2.micro', engine='sqlserver-ex'
                        , masteruser='sa', masteruserpassword='Password12', availabilityzone='us-east-1d',
                        engineversion='14.00.3015.40.v1', licensemodel='license-included'
        :return: dict.
        For more information refer  https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/rds.html#RDS.Client.create_db_instance
        '''

        response = rdsclient.create_db_instance \
                (
                DBInstanceIdentifier=instance_name,
                AllocatedStorage=20,
                DBInstanceClass=dbinstanceclass,
                Engine=engine,
                MasterUsername=masteruser,
                MasterUserPassword=masteruserpassword,
                VpcSecurityGroupIds=
                [
                    security_group_id
                ],
                AvailabilityZone=availabilityzone,
                DBSubnetGroupName='default',
                MultiAZ=False,
                EngineVersion=engineversion,
                LicenseModel=licensemodel,
                StorageType='gp2',
                BackupRetentionPeriod=0,
                OptionGroupName=instance_name + '-ex'

            )
        return response

    @Core.error_handler_decorator
    def create_and_configure_optiongroup(option_group_name, role_arn, enginename='sqlserver-ex',\
                                         engineversion='14.00'):
        '''
        :description : create a option group for DB instance. Option group is important for SQL instance to have access
                        on S3 service to access DB backup file.
        :param : option_group_name, role_arn (allowing access to s3)
        :return: dict.
        For more information refer  https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/rds.html#RDS.Client.create_option_group
        '''
        option_group = rdsclient.create_option_group \
                (
                OptionGroupName=option_group_name + '-ex',
                EngineName=enginename,
                MajorEngineVersion=engineversion,
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





# Creating base class for Data Migration service
class DMSClass():

    @Core.error_handler_decorator
    def create_replication_instance(instance_name, instanceclass='dms.t2.micro', availabilityzone='us-east-1d'):
        '''
        :description : create a replication instance for data migration. Repplication instance helps communicate
                    DB source and targets using endpoints.
        :param : instance_name, instanceclass='dms.t2.micro', availabilityzone='us-east-1d'
        :return: dict.
        For more information refer  https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/dms.html#DatabaseMigrationService.Client.create_replication_instance
        '''

        response = dmsclient.create_replication_instance(
            ReplicationInstanceIdentifier=instance_name,
            AllocatedStorage=5,
            ReplicationInstanceClass=instanceclass,
            AvailabilityZone=availabilityzone,
            MultiAZ=False,
            Tags=[
                {
                    'Key': 'Category',
                    'Value': 'Testing'
                },
            ],
            PubliclyAccessible=True
        )
        # since there is no waiter function implementation for replication instance in boto3
        # we need to write custom code to wait for instance to be available.
        # At the time of witting this code there are no waiter functions implemented in Boto3.
        # we are using our own custom waiter from core class.

        dmsclient.get_waiter = types.MethodType(Core.get_waiter, dmsclient)

        waiter = dmsclient.get_waiter('instance_available')
        waiter.wait(instance=instance_name)

        '''time.sleep(5)
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
                return response'''
        return response



    @Core.error_handler_decorator
    def create_dms_endpoint(endpoint_name, type, server_name, db_name, user_name, password):
        '''
        :description : Function is for creating replication endpoint. For source and target we need to
                        create a separate replication endpoint. Replication task uses replication endpoints
                        to migrate data.
        :param : endpoint_name, type, server_name, db_name, user_name, password
        :return: dict.
        For more information refer  https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/dms.html#DatabaseMigrationService.Client.create_endpoint
        '''

        response = dmsclient.create_endpoint \
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



    @Core.error_handler_decorator
    def test_connection_for_endpoint(replication_instance_arn, endpoint_arn):
        '''
        :description : Once replicaiton endpoint is created we need to test connection for replication
                        endpoint before creating a replication task. This ensures replication endpoint
                        can speak to source/target DB. This is just a safety measure.
        :param kwargs: instance_name, instanceclass='dms.t2.micro', availabilityzone='us-east-1d'
        :return: dict.
        For more information refer  https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/dms.html#DatabaseMigrationService.Client.test_connection
        '''

        response = dmsclient.test_connection(
            ReplicationInstanceArn=replication_instance_arn,
            EndpointArn=endpoint_arn
        )
        # since there is no waiter function implementation for replication instance in boto3
        # we need to write custom code to wait for connection to be available.
        # At the time of witting this code there are no waiter functions implemented in Boto3.
        # we are using our own custom waiter from core class.

        dmsclient.get_waiter = types.MethodType(Core.get_waiter, dmsclient)

        waiter = dmsclient.get_waiter('test_endpoint_connection')
        waiter.wait(endpointarn=endpoint_arn)

        return response




    @Core.error_handler_decorator
    def refresh_schema(endpoint_arn, replicaiton_instance_arn):
        '''
        :description : Once replication endpoint connection is tested, we nee to refresh DB schema for endpoint.
                        This step is needed when we create replication endpoint programmatically otherwise
                        while creating replication task we get issues while selecting source schema in
                        configure DB schema section.
        :param kwargs: endpoint_arn, replicaiton_instance_arn
        :return: dict.
        For more information refer  https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/dms.html#DatabaseMigrationService.Client.refresh_schemas
        '''
        response = dmsclient.refresh_schemas(
            EndpointArn=endpoint_arn,
            ReplicationInstanceArn=replicaiton_instance_arn
        )
        # since there is no waiter function implementation for endpoint refresh schema.
        # we need to write custom code to wait for endpoint to fetch source DB schema.
        # At the time of witting this code there are no waiter functions implemented in Boto3.
        # we are using our own custom waiter from core class.

        dmsclient.get_waiter = types.MethodType(Core.get_waiter, dmsclient)

        waiter = dmsclient.get_waiter('refresh_schema')
        waiter.wait(endpointarn=endpoint_arn)

        return response



    @Core.error_handler_decorator
    def create_dms_replicaiton_task(task_name, source_arn, target_arn, repliaction_insatance_arn, table_mapping):
        '''
        :description : Final step is to create a replication task which uses source and target endpoints
                        and start data migration process.
        :param : task_name, source_arn, target_arn, repliaction_insatance_arn, table_mapping
        :return: dict.
        For more information refer  https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/dms.html#DatabaseMigrationService.Client.create_replication_task
        '''

        response = dmsclient.create_replication_task \
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
        # At the time of witting this code there are no waiter functions implemented in Boto3.
        # we are using our own custom waiter from core class.

        dmsclient.get_waiter = types.MethodType(Core.get_waiter, dmsclient)

        waiter = dmsclient.get_waiter('replication_task_ready')
        response = waiter.wait(replicaitontaskid=task_name)



        replication_task_arn = response['ReplicationTasks'][0]['ReplicationTaskArn']

        # Start replication task to migrate data once it is ready.
        response = dmsclient.start_replication_task(
                    ReplicationTaskArn=replication_task_arn,
                    StartReplicationTaskType='start-replication')

        return response









srdsclient = boto3.client('rds')
dbinstancename =  'gapsql01'
rdsecuritygroup='RDSLiftnShift'
rdsvpcrole='rds-vpc-role'
rds_s3bucket_access_policy = 'RDS_S3_Access_Policy'
vpc_id = 'vpc-8bfe36f1'
bucket_name = 'gapsqldbbucket'
backup_path='C:/Users/ashfaque_mulani/Desktop/APR_2018-08-15_13-00.bak'

ec2 = EC2Class()
ec2.create_security_group(rdsecuritygroup, vpc_id, 'test security group')
iam  = IAMClass()
help(iam.create_policy)

print('done..!!')
