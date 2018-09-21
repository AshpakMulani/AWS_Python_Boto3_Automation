import traceback
import Boto3ClassCollection as B3CC


rdspolicydocument = \
    {
        "Version": "2012-10-17",
        "Statement":
            [
                {
                    "Effect": "Allow",
                    "Principal":
                        {
                            "Service": "rds.amazonaws.com"
                        },
                    "Action": "sts:AssumeRole"
                }
            ]
    }

rds_s3bucket_access_policydocument = \
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

dbinstancename = 'gapsql01'
rdsecuritygroup = 'RDSLiftnShift'
rdsvpcrole = 'rds-vpc-role'
rds_s3bucket_access_policy = 'RDS_S3_Access_Policy'
vpc_id = 'vpc-8bfe36f1'
bucket_name = 'gapsqldbbucket'
backup_path = 'C:/Users/ashfaque_mulani/Desktop/APR_2018-08-15_13-00.bak'



def main():

    ec2 = B3CC.EC2Class()
    s3 = B3CC.S3Class()
    iam = B3CC.IAMClass()
    rds = B3CC.RDSClass()

    # STEP 1 create bucket
    s3.create_bucket(bucket_name)
'''
    # STEP 2 Upload DB backup file to s3 bucket created in previous step.
    s3.upload_file_bucket(backup_path, bucket_name, 'apr.bak')

    # STEP 3 Create security group to allow communication on port 1433 for SQL instance.
    security_group_id = ec2.create_security_group(rdsecuritygroup, vpc_id)['GroupId']

    # STEP 4 Create a service role for RDS service. This role will be used to allow access on S3 bucket created
    # in step 1.
    role_arn = iam.create_role(rolename=rdsvpcrole, policydocument=rdspolicydocument)['Role']['Arn']

    # STEP 5 create a policy to allow RDS service access S3 bucket.
    policy_arn = iam.create_policy(policyname=rds_s3bucket_access_policy, description='RDS bucket access policy',\
                                   policydocument=rds_s3bucket_access_policydocument)['Policy']['Arn']

    # STEP 6 attach role and policy created in step 4 and step 5, to enable RDS and S3 communication
    iam.attach_policy_to_role(policyARN=policy_arn, rolename=rdsvpcrole)

    # STEP 7 create configuration group for SQL instance to have S3 as backup source
    rds.create_and_configure_optiongroup(dbinstancename, role_arn)

    # STEP 8 create SQL instance
    rds.create_sql_instance(instance_name, security_group_id)
'''
if __name__ == '__main__':
    try:
        main()
    except:
        print(traceback.format_exc())
        print('Error occurred..!!')
