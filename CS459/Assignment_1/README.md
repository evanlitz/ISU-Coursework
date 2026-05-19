# CS459 Assignment 1: AWS EC2 & S3 Basics

**Course**: ComS/CprE 459/559 – Introduction to Cloud Computing Security, Iowa State University

## Overview

Three-part introduction to core AWS services using the boto3 SDK: static website hosting on S3, programmatic EC2 instance creation, and file uploads to S3.

## Parts

### Part 1 – Static Website on S3
`index.html` is a simple HTML page deployed to an S3 bucket with static website hosting enabled. The bucket URL is recorded in `p1.txt`.

### Part 2 – Programmatic EC2 Instance Launch
`p2_ec2_create.py` uses boto3 to launch an EC2 instance. The script accepts configuration for region, AMI ID, instance type, and security group, then prints the resulting instance ID.

### Part 3 – File Upload to S3
`p3_s3_upload.py` uses boto3 to create an S3 bucket and upload a local file to it. Handles region-specific bucket creation constraints (`LocationConstraint` is omitted for `us-east-1`, required for all other regions).

## Files

| File | Description |
|------|-------------|
| `index.html` | Static HTML page deployed to S3 |
| `p1.txt` | S3 website URL for Part 1 |
| `p2_ec2_create.py` | boto3 script to programmatically launch an EC2 instance |
| `p3_s3_upload.py` | boto3 script to create an S3 bucket and upload a file |

## Dependencies

- Python 3
- `boto3`
- AWS credentials configured (via `aws configure` or environment variables)
