# CS459 Assignment 5: IAM & Logging

**Course**: ComS/CprE 459/559 – Introduction to Cloud Computing Security, Iowa State University

## Overview

Two labs covering AWS identity and access management and network-level logging. The assignment is entirely AWS console/CLI work; the deliverable is a PDF report with screenshots.

## Lab 1 – Fine-Grained IAM and Role-Based Access

### Part A: Fine-Grained Policy
Creates IAM policy **P1** with least-privilege permissions:
- Allow `s3:ListAllMyBuckets`
- Allow `s3:GetObject` only for objects in bucket `securebucketx`
- Explicitly deny `s3:GetObject` on all other S3 objects
- Allow read-only EC2 access (`ec2:Describe*`)

Policy is attached to IAM user **AuditorUser**. Access is verified both for allowed operations (list buckets, read `securebucketx`, describe EC2) and denied operations (read other buckets, start/stop EC2 instances).

### Part B: Role-Based Access
Creates IAM role **AppRole** with policy P1 and a trust policy allowing the EC2 service to assume the role. An EC2 instance is launched with AppRole attached as an instance profile. The same access verification is performed from the instance using the AWS CLI (credentials are provided automatically via the instance metadata service).

## Lab 2 – VPC Flow Logs and Traffic Analysis

Configures network-level visibility for a default VPC:

1. Launch an EC2 instance running a Python HTTP server on port 80.
2. Create a CloudWatch Log Group (`defaultVPCLogs`).
3. Create IAM role **VPCFlowLogsRole** with a trust policy for `vpc-flow-logs.amazonaws.com` and permissions to write to CloudWatch Logs.
4. Enable VPC Flow Logs on the default VPC (filter: ALL, destination: CloudWatch).
5. Generate allowed traffic (HTTP to port 80) and rejected traffic (connection to a closed port).
6. Analyze CloudWatch log streams to identify `ACCEPT` and `REJECT` entries and explain why each occurred.

## Deliverable

`HW5_Report.pdf` — screenshots of IAM policies, roles, trust relationships, VPC Flow Logs configuration, CloudWatch log streams, and ACCEPT/REJECT log entries with explanations.
