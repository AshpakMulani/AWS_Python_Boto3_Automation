
import boto3
import json

dms = boto3.client('iam')
Policydocument={
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

response = dms.create_role(

    RoleName='dms-vpc-role-test',
    AssumeRolePolicyDocument=json.dumps(Policydocument)

)

response = dms.attach_role_policy(
    PolicyArn='arn:aws:iam::aws:policy/service-role/AmazonDMSVPCManagementRole',
    RoleName='dms-vpc-role-test',
)