'''import pypyodbc

cnxn = pypyodbc.connect("Driver={SQL Server Native Client 11.0};"
                        "Server=gapsql01.c53u7d8l6zis.us-east-1.rds.amazonaws.com,1433;"
                        "Database=master;"
                        "uid=sa;pwd=Password12")
cursor = cnxn.cursor()
cursor.execute('select * from spt_monitor')

for row in cursor:
    print('row = %r' % (row,))
'''
import boto3
import json
import time
from botocore.exceptions import ClientError



ec2client = boto3.client('ec2')
rdsclient = boto3.client('rds')
iamclient = boto3.client('iam')
s3client = boto3.client('s3')
bucketname='Fasas'

def createbucket(bucketname):
    s3client.create_bucket \
    (
        ACL='public-read-write',
        Bucket=bucketname
    )



def function_runner(f, purpose):
    try:
        function_result = f()
    except ClientError as e:
        function_result = 0
        print("Error occurred while " + purpose + " : " + e.response['Error']['Message'])

    return function_result

  
function_runner(createbucket(bucketname),'creating bucket')
