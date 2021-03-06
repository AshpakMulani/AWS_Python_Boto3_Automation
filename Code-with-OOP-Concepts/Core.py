
import boto3
import time

from botocore.exceptions import ClientError

ec2client = boto3.client('ec2')
rdsclient = boto3.client('rds')
iamclient = boto3.client('iam')
s3client = boto3.client('s3')
dmsclient = boto3.client('dms')



class CoreWaiter():
    class dms_instance_available_waiter():
        def wait(self, **kwargs):
            while 1:
                time.sleep(10)
                response = dmsclient.describe_replication_instances(
                    Filters=[
                        {
                            'Name': 'replication-instance-id',
                            'Values': [
                                kwargs['instance'],
                            ]
                        },
                    ],

                )

                if response['ReplicationInstances'][0]['ReplicationInstanceStatus'].lower() == 'available':
                    return response

    class dms_test_endpoint_connection_waiter():
        def wait(self, **kwargs):
            while 1:
                time.sleep(10)
                response = dmsclient.describe_connections(
                    Filters=[
                        {
                            'Name': 'endpoint-arn',
                            'Values': [
                                kwargs['endpointarn'],
                            ]
                        },
                    ]

                )

                if response['Connections'][0]['Status'].lower() == 'successful':
                    return response

    class dms_refresh_schema_waiter():
        def wait(self, **kwargs):
            while 1:
                time.sleep(5)
                response = dmsclient.describe_refresh_schemas_status(
                    EndpointArn=kwargs['endpointarn']
                )

                if response['RefreshSchemasStatus']['Status'].lower() == 'successful':
                    return response

    class dms_replicaiton_task_ready_waiter():
        def wait(self, **kwargs):
            while 1:
                time.sleep(5)
                while 1:
                    time.sleep(10)
                    response = dmsclient.describe_replication_tasks(
                        Filters=[
                            {
                                'Name': 'replication-task-id',
                                'Values': [
                                    kwargs['replication_task_id'],
                                ]
                            },
                        ],

                    )
                    if response['ReplicationTasks'][0]['Status'].lower() == 'ready':
                        return response


class Core():
    def error_handler_decorator(function_to_decorate):
        def func_with_error_handler(*args, **kwargs):

            try:
                return function_to_decorate(*args, **kwargs)
            except ClientError as e:
                print(f"There was error in function - {function_to_decorate.__name__} : {e.response['Error']['Message']}")

        # assigning function name and docstring to decorator function, because if help is called on main function,
        # it should not return name and docstring of decorator function due to use of decorator,
        func_with_error_handler.__name__ = function_to_decorate.__name__
        func_with_error_handler.__doc__ = function_to_decorate.__doc__
        return func_with_error_handler



    def get_waiter(self, *args):
        # checking type of calling object and mapping it to respective waiter class from CoreWaiterClass
        if str(type(self) == str(type(boto3.client('dms')))):
            return getattr(CoreWaiter, 'dms_' + str(args[0]).lower() + '_waiter')()
            # getattr only returns attribute of class, in this case waiter class name, so we need to put ' () '
            # at the end to make ir return a class object.






'''
Creating dummy/unused main() function in this library because we do not want library to execute on import statement
in other scripts. With this approach sice this script is not getting executed during import, referring script 
will not throw error during import in case if there is any error in this script.
Respective classes and functions will be directly called only when triggered by referencing script.
'''

def main():
    pass

if __name__ == '__main__':
    main()
