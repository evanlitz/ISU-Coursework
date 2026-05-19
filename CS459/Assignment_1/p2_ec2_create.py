import sys
import boto3
from botocore.exceptions import ClientError, NoCredentialsError, NoRegionError

"""
Part 2 implementation for COM S 459 Assignment 1.

@author Evan Litzer
2/9/2026

"""


"""
Prompt the user for string input for the fields. Strip whitespace and checks for empty values that are handled
accordingly. 
"""
def prompt(label: str) -> str:
    val = input(label).strip()
    if not val:
        print(f"Error: '{label.strip()}' cannot be empty.")
        sys.exit(1)
    return val

# Main function
def main():
    # Execution logic for collecting input from the user for the necesscary fields. 
    # Includes region, instance type, ami id, security group id, and key pair name.
    region = prompt("AWS region (us-east-2): ")
    instance_type = prompt("EC2 instance type (t2.micro): ")
    ami_id = prompt("AMI ID (ami-...): ")
    security_group_id = prompt("Security group ID (sg-...): ")
    key_pair_name = prompt("Key pair name: ")

    # Create EC2 API client for the user's region so that EC2 resources work correctly.
    try:
        ec2 = boto3.client("ec2", region_name=region)

        # Launch one EC2 instance enforced by min and max count.
        # SecurityGroupIds takes in list as input.
        resp = ec2.run_instances(
            ImageId=ami_id,
            InstanceType=instance_type,
            SecurityGroupIds=[security_group_id],
            KeyName=key_pair_name,
            MinCount=1,
            MaxCount=1,
        )
        
        # run_intances responde contains list of launched instances
        # Prints instance ID
        instance_id = resp["Instances"][0]["InstanceId"]
        print(instance_id)  
    
    # Error handling for any credential related error.
    except NoCredentialsError:
        print("AWS credential error")
        sys.exit(2)
    
    # Error handling for any region related errors, mostly pertaining to when a user types in either the wrong one or mistypes it.
    except NoRegionError:
        print("AWS region error")
        sys.exit(3)
    
    # AWS responds with service error, formatted string tells me what is wrong so I debug. VERY HELPFUL
    except ClientError as e:
        print(f"AWS error: {e.response.get('Error', {}).get('Code')}: {e.response.get('Error', {}).get('Message')}")
        sys.exit(4)

# Main runs when file is executed.
if __name__ == "__main__":
    main()
