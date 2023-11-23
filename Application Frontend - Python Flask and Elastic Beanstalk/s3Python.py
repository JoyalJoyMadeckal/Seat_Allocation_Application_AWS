from datetime import datetime
import boto3 
import logging
from botocore.exceptions import ClientError
from botocore.config import Config

# my_config = Config(
#     region_name = 'us-east-1',
#     # signature_version = 'v4',
#     retries = {
#         'max_attempts': 10,
#         'mode': 'standard'
#     }
#     )

# client = boto3.client('kinesis', config=my_config)


def create_bucket(bucket_name, region=None):
    """Create an S3 bucket in a specified region
    If a region is not specified, the bucket is created in the S3 default
    region (us-east-1).
    :param bucket_name: Bucket to create
    :param region: String region to create bucket in, e.g., 'us-west-2'
    :return: True if bucket created, else False
    """
    # Create bucket
    try:
        if region is None:
            s3_client = boto3.client('s3')
            s3_client.create_bucket(Bucket=bucket_name)
        else:
            s3_client = boto3.client('s3', region_name=region)
            location = {'LocationConstraint': region}
            s3_client.create_bucket(Bucket=bucket_name,
            CreateBucketConfiguration=location)
    except ClientError as e:
        logging.error(e)
        return False
    return True

def upload_file(file_name, bucket, object_name=None):
    """Upload a file to an S3 bucket
    :param file_name: File to upload
    :param bucket: Bucket to upload to
    :param object_name: S3 object name. If not specified then file_name is used
    :return: True if file was uploaded, else False
    """
    # If S3 object_name was not specified, use file_name
    if object_name is None:
        object_name = file_name
        # Upload the file
        s3_client = boto3.client('s3')
    try:
        se = s3_client.upload_file(file_name, bucket, object_name)
    except ClientError as e:
        logging.error(e)
        return False
    return True

# bucket_created = create_bucket("joyaluidmadeckaltesting")
# print(f"Succesfully created bucket joyal_uid_madeckal_testing" if bucket_created else "Failed to create bucket")

s3 = boto3.client('s3')

# with open("New Text Document.txt", "rb") as t:
#     s3.upload_fileobj(t, "joyaluidmadeckaltesting", 'mykey')

print(datetime.now())
# response = s3.list_buckets()
# # Output the bucket names
# print('Existing buckets:')
# for bucket in response['Buckets']:
#     print(f' {bucket["Name"]}')