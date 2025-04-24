import json
import boto3
import logging

from botocore.exceptions import ClientError
logging.getLogger().setLevel(logging.INFO)

def create_presigned_url_expanded(client_method_name, method_parameters=None,
                                  expiration=300):
    # Generate a presigned URL for the S3 client method
    s3_client = boto3.client('s3')
    try:
        response = s3_client.generate_presigned_url(ClientMethod=client_method_name,
                                                    Params=method_parameters,
                                                    ExpiresIn=expiration)
    except ClientError as e:
        logging.error(e)
        return None

    # The response contains the presigned URL
    return response

#This function is designed to crash the Lambda, resulting in non-200 status code if no object.
def check_object_existence(bucket, key): 
    s3_client = boto3.client('s3')
    response = s3_client.head_object(Bucket=bucket,Key=key)

def lambda_handler(event, context):
    logging.info('got event{}'.format(event))
    client_action = "get_object"
    z = event["requestContext"]["httpMethod"]
    if z == "GET":
        try:
            paras = event["queryStringParameters"]
            myurl = create_presigned_url_expanded(client_method_name="get_object", 
                                                method_parameters= {"Bucket": paras["bucket"],"Key": paras["key"]})
            response = {
                        "statusCode": 200,
                        "body": myurl,
                        "headers": {
                            'Content-Type': 'text/html',
                            'Access-Control-Allow-Origin': "https://DHTMLLAMBDA.lambda-url.region.on.aws"
                        }
            }
            return(response)
        except Exception as E:
            print(E)
    elif z == "HEAD":
        paras = event["queryStringParameters"]
        temp = check_object_existence(bucket=paras["bucket"],key=paras["key"])
        response = {
            "statusCode": 200,
            "headers": {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': "https://DHTMLLAMBDA.lambda-url.region.on.aws"
                }
            }
        return(response)