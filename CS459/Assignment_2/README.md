# CS459 Assignment 2: AWS Lambda Functions

**Course**: ComS/CprE 459/559 – Introduction to Cloud Computing Security, Iowa State University

## Overview

Two serverless Lambda functions deployed on AWS, accessed via Lambda Function URLs. Covers the core Lambda handler pattern, JSON request/response formatting, and cross-service access from Lambda (S3 via boto3).

## Parts

### Part 1 – Rectangle Calculator
`p1_rectangle_lf.py` implements a Lambda function that accepts a JSON body with `length` and `width` fields and returns the calculated area and perimeter. Returns HTTP 400 for missing fields and 500 for unexpected errors.

**Example request body:**
```json
{"length": 5, "width": 3}
```

**Example response:**
```json
{"area": 15, "perimeter": 16}
```

### Part 2 – S3 Bucket Lister
`p2_s3_lf.py` implements a Lambda function that calls `s3.list_buckets()` and returns the total number of S3 buckets in the account as a JSON response.

## Files

| File | Description |
|------|-------------|
| `p1_rectangle_lf.py` | Lambda handler: rectangle area and perimeter calculator |
| `p2_s3_lf.py` | Lambda handler: lists S3 buckets and returns count |

## Deployment Notes

Both functions are deployed directly in the AWS Lambda console. The AWS setup (Function URL configuration, IAM execution role with S3 read permissions for Part 2) was completed through the AWS Management Console.
