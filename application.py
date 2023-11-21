import boto3, response

region = 'ap-south-1'
Name='Dynamic-Web-App-backend-Grp-11'
instance_type = 't2.micro'
image_id = 'ami-0f5ee92e2d63afc18'  # Replace with the desired AMI ID
security_group_ids = ['sg-0103a917e74448c29']
key_name = 'ec2_ramkumar'
user_data = """#!/bin/bash
    sudo apt update -y
    sudo apt install nginx -y
    sudo systemctl start nginx
    sudo systemctl enable nginx
    touch index.html > var/www/html/"""

ec2 = boto3.resource('ec2', region_name=region)

# Create an EC2 instance
response = ec2.create_instances(ImageId=image_id,
    InstanceType=instance_type,
    SecurityGroupIds=security_group_ids,
    TagSpecifications=[ { 'ResourceType': 'instance', 'Tags': [ { 'Key': 'Name', 'Value': 'Grp-11-web-app-backend' }, ] }, ],
    KeyName=key_name,
    UserData=user_data,
    MinCount=1,
    MaxCount=1)

# Extract the instance ID
instance_id = response[0].id

# Print the instance ID
print(f"EC2 instance {instance_id} has been created.")
