import os
import sys
import boto3
from botocore.exceptions import ClientError, NoCredentialsError

"""
Part 3 implementation of assignment 1 for CS 459

@author Evan Litzer
2/9/2026
"""


"""
Prompt the user for input value that is nonempty. Strip whitespace and exit early is the user enters 
in an empty input.
"""
def prompt_nonempty(msg: str) -> str:
    val = input(msg).strip()
    if not val:
        print("ERROR: input cannot be empty.")
        sys.exit(1)
    return val

"""
Main method
"""
def main():
    # Collect the inputs needed for this part of assignment, including region, bucket name, and filepath.
    region = prompt_nonempty("AWS region: ")
    bucket_name = prompt_nonempty("S3 bucket name: ")
    file_path = prompt_nonempty("Local file path: ")

# Make sure local filepath exists before uploading it. Exit if it does not exist.
    if not os.path.isfile(file_path):
        print(f"ERROR: File not found: {file_path}")
        sys.exit(2)

# Create s3 client
    s3 = boto3.client("s3", region_name=region)

# This part ChatGPT helped me with. Apparently s3 buckets need to be created differently in us-east-1 vs all other regions
# So this try catch block handles this by enforcing a location constraint for all other regions besides us-east-1.
    try:
        if region == "us-east-1":
            s3.create_bucket(Bucket=bucket_name)
        else:
            s3.create_bucket(
                Bucket=bucket_name,
                CreateBucketConfiguration={"LocationConstraint": region},
            )

# File name is used as the object key in S3 and is uploaded to s3://bucket//key
        key = os.path.basename(file_path)
        s3.upload_file(file_path, bucket_name, key)

        print(f"Uploaded '{file_path}' to s3://{bucket_name}/{key}")

# AWS credential related errors when boto3 has trouble identifying them
    except NoCredentialsError:
        sys.exit(3)
# AWS service error handlling, formatted string prints the details for debugging.
    except ClientError as e:
        code = e.response.get("Error", {}).get("Code")
        msg = e.response.get("Error", {}).get("Message")
        print(f"AWS error: {code}: {msg}")
        sys.exit(4)

# When file is executed, main function runs.
if __name__ == "__main__":
    main()
