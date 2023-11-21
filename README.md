# Monitoring, Scaling and Automation

1. Web Application Deployment: 

 - Use `boto3` to: 

 - Create an S3 bucket to store your web application's static files. 

 - Launch an EC2 instance and configure it as a web server (e.g., Apache, Nginx).  - Deploy the web application onto the EC2 instance. 

 ```
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
```

2. Load Balancing with ELB: 

 - Deploy an Application Load Balancer (ALB) using `boto3`. 

 - Register the EC2 instance(s) with the ALB. 

 ```
 import boto3, response, time
from EC2 import create_EC2_instance

#AWS Credentials and region
aws_access_key_id = 'AKIAUJRYN7IHD7ODEYPH'
aws_secret_access_key = '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'
region = 'ap-south-1'

#Importing instanced ID from EC2.py
instanced_id_list = list(create_EC2_instance())

time.sleep(200)

#Create an application load balancer
def create_load_balancer():
    elb_client = boto3.client('elbv2', aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key, region_name=region)
    
    response = elb_client.create_load_balancer(
        Name = 'Grp-11-ALB',
        Subnets=['subnet-054d138c719f3f355','subnet-0ea24e054cba9cad2','subnet-0ea185273ead71a27'],
        SecurityGroups=['sg-0103a917e74448c29'],
        Scheme='internet-facing',
        Tags=[{
            'Key':'Name',
            'Value':'Grp-11-ALB'
        },],
        Type='application',
        IpAddressType='ipv4'
    )

    #Get the ARN of newly created application load balancer
    load_balancer_arn = response['LoadBalancers'][0]['LoadBalancerArn']
    print(f"Application Load Balancer with ARN {load_balancer_arn} has been created.")

    #Create Target Group
    response = elb_client.create_target_group(
        Name='Grp-11-TG',
        Protocol='HTTP',
        Port=80,
        VpcId='vpc-0c5a8881cff1146d8',
        TargetType='instance',  # Set to 'ip' if you are using IP addresses as targets
        HealthCheckProtocol='HTTP', # Health check protocol, can be 'HTTP', 'HTTPS', 'TCP', or 'UDP'
        HealthCheckPort='80', # Port used for health checks
        HealthCheckPath='/', # Path used for health checks
        HealthCheckIntervalSeconds=30, # Interval between health checks
        HealthCheckTimeoutSeconds=5, # Timeout for health checks
        HealthyThresholdCount=2, # Number of consecutive successful health checks required
        UnhealthyThresholdCount=2,  # Number of consecutive failed health checks required
        Matcher={
            'HttpCode': '200'
        },
    )

    # Get the ARN of the newly created Target Group
    target_group_arn = response['TargetGroups'][0]['TargetGroupArn']
    print(f"Target Group with ARN {target_group_arn} has been created.")

    # Register a target (EC2 instance) with the Target Group
    # response = elb_client.register_targets(
    #     TargetGroupArn=target_group_arn,
    #     Targets=[
    #         {
    #             'Id': instanced_id_1,
    #             'Port': 80,
    #         },
    #     ]
    # )

    # Register a target (EC2 instance) with the Target Group
    instance_ids = instanced_id_list
    targets = [{'Id': i} for i in instance_ids]
    response = elb_client.register_targets(
        TargetGroupArn=target_group_arn,
        Targets=targets
    )

    # Create a listener for the Load Balancer that forwards HTTP traffic to the Target Group
    response = elb_client.create_listener(
        LoadBalancerArn=load_balancer_arn,
        Protocol='HTTP',
        Port=80,
        DefaultActions=[
            {
                'Type': 'forward',
                'TargetGroupArn': target_group_arn,
            },
        ]
    )

create_load_balancer()
 
 ```

3. Auto Scaling Group (ASG) Configuration: 

 - Using `boto3`, create an ASG with the deployed EC2 instance as a template. 

 - Configure scaling policies to scale in/out based on metrics like CPU utilization or network traffic. 

 ```
 
 import boto3, response
# from ALB import instanced_id_list

#AWS Credentials and region
aws_access_key_id = 'AKIAUJRYN7IHD7ODEYPH'
aws_secret_access_key = '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'
region = 'ap-south-1'

instance_id = 'i-01bd1d1583a830800'

#Create an Auto scaling group
def create_auto_scaling_group():
    autoscaling = boto3.client('autoscaling', aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key, region_name=region)
    
# Create launch configuration
    autoscaling.create_launch_configuration(
        LaunchConfigurationName='Grp11LaunchTemplate',
        InstanceId=instance_id,
    )
    print("Lauch Template created successfully.")

# Create auto scaling group
    autoscaling.create_auto_scaling_group(
        AutoScalingGroupName='Gpr11ASG',
        LaunchConfigurationName='Grp11LaunchTemplate',
        MinSize=2,
        MaxSize=3,
        DesiredCapacity=2,
        VPCZoneIdentifier='subnet-054d138c719f3f355, subnet-0ea24e054cba9cad2, subnet-0ea185273ead71a27',
    )
    print("ASG created successfully.")

# Create scale out policy
    scale_out_policy = autoscaling.put_scaling_policy(
        AutoScalingGroupName='Gpr11ASG',
        PolicyName='Grp11_SCALE_OUT_POLICY',
        PolicyType='TargetTrackingScaling',
        TargetTrackingConfiguration={
            'PredefinedMetricSpecification': {
               'PredefinedMetricType': 'ASGAverageCPUUtilization',
            },
            'TargetValue': 60.0,
            # 'ScaleOutCooldown': 60,
            # 'ScaleInCooldown': 300,
        }
    )
    print("Scale OUT policy created successfully.")

# Create scale in policy
    # scale_in_policy = autoscaling.put_scaling_policy(
    #     AutoScalingGroupName='Gpr11ASG',
    #     PolicyName='Grp11_SCALE_IN_POLICY',
    #     PolicyType='TargetTrackingScaling',
    #     TargetTrackingConfiguration={
    #         'PredefinedMetricSpecification': {
    #             'PredefinedMetricType': 'ASGAverageCPUUtilization',
    #         },
    #         'TargetValue': 10.0,
    #         # 'ScaleOutCooldown': 300,
    #         # 'ScaleInCooldown': 60,
    #     }
    # )
    # print("Scale IN policy created successfully.")

create_auto_scaling_group()
 
 ```

4. Lambda-based Health Checks & Management: 

 - Develop a Lambda function to periodically check the health of the web application  (through the ALB). 

 - If the health check fails consistently, the Lambda function should: 

 - Capture a snapshot of the failing instance for debugging purposes.

 - Terminate the problematic instance, allowing the ASG to replace it.  - Send a notification through SNS to the administrators. 

```
import boto3
sns_client = boto3.client('sns', region_name='ap-south-1') 

topic_name = 'rams-sns'

response = sns_client.create_topic(Name=topic_name)

topic_arn = response['TopicArn']
print(f'Topic created: {topic_arn}')

protocol = 'email'
endpoint = '24ram46r@gmail.com'

sns_client.subscribe(
    TopicArn=topic_arn,
    Protocol=protocol,
    Endpoint=endpoint
 )
```

topic_arn='arn:aws:sns:ap-south-1:295390363791:rams-sns'

```
import boto3

client = boto3.client('lambda' , region_name='ap-south-1')

with open('code.zip', 'rb') as file:
    zip_contents = file.read()
response = client.create_function(
    Code={
        'ZipFile': zip_contents  
    },
    FunctionName='rk-temp',
    Handler='index.handler',
    MemorySize=256,
    Publish=True,
    Role='arn:aws:iam::295390363791:role/rk-temp',
    Runtime='python3.11',
    # Tags={
    #     'DEPARTMENT': 'Assets',
    # },
    Timeout=15,
    TracingConfig={
        'Mode': 'Active',
    },
)
```
* yourlambdafunctionarn='arn:aws:lambda:ap-south-1:295390363791:function:rk-temp'

```
function_name = 'rk-temp'
sns_topic_arn = 'arn:aws:sns:ap-south-1:295390363791:rk-temp'

policy = {
    'Version': '2012-10-17',
    'Statement': [
        {
            'Effect': 'Allow',
            'Principal': {
                'Service': 'lambda.amazonaws.com'
            },
            'Action': 'lambda:InvokeFunction',
            'Resource': yourlambdafunctionarn,
            'Condition': {
                'ArnLike': {
                    'AWS:SourceArn': sns_topic_arn
                }
            }
        }
    ]
}

response = client.add_permission(
    FunctionName=function_name,
    StatementId='sns-permission',
    Action='lambda:InvokeFunction',
    Principal='sns.amazonaws.com',
    SourceArn='arn:aws:sns:ap-south-1:295390363791:rams-sns',
    SourceAccount='295390363791'  
)

print(response)
```

5. S3 Logging & Monitoring: 

 - Configure the ALB to send access logs to the S3 bucket. 

 - Create a Lambda function that triggers when a new log is added to the S3 bucket. This function can analyze the log for suspicious activities (like potential DDoS attacks) or just high traffic. 

 - If any predefined criteria are met during the log analysis, the Lambda function sends a  notification via SNS. 

```
 import boto3
 import csv
 s3_client = boto3.client('s3')
 region='ap-south-1'
 bucket_name = 'rams-s3'
 location = {'LocationConstraint': region}
 s3_client.create_bucket(Bucket=bucket_name, CreateBucketConfiguration=location)
 response = s3_client.get_bucket_location(Bucket=bucket_name)
 bucket_location = response['LocationConstraint']
 s3_bucket = f'arn:aws:s3:::{bucket_name}'

```

```
import boto3

elbv2_client = boto3.client('elbv2', region_name='ap-south-1')

alb_arn = 'arn:aws:elasticloadbalancing:ap-south-1:295390363791:loadbalancer/app/rams-alb/5a90975daf5cef5c'

s3_bucket_name = 'rams-s3'  

elbv2_client.modify_load_balancer_attributes(
    LoadBalancerArn=alb_arn,
    Attributes=[
        {
            'Key': 'access_logs.s3.enabled',
            'Value': 'true'
        },
        {
            'Key': 'access_logs.s3.bucket',
            'Value': s3_bucket_name
        }
    ]
)
```
{
  "Id": "Policy1699339671246",
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "Stmt1699339659619",
      "Action": ["s3:*", "autoscaling-plans:*", "ec2:*", "elasticloadbalancing:*"],
      "Effect": "Allow",
      "Resource": "arn:aws:s3:::rams-s3",
      "Principal": "*"
    }
  ]
}


6. SNS Notifications: 

 - Set up different SNS topics for different alerts (e.g., health issues, scaling events, high traffic). 

 - Integrate SNS with Lambda so that administrators receive SMS or email notifications. 

 ##### Successfully set up AWS SNS topics for various alerts, such as health issues, scaling events, and high traffic. These alerts are seamlessly integrated with AWS Lambda, ensuring that administrators receive timely notifications via SMS or email. Your system is now equipped to provide proactive monitoring and alerting, enhancing its overall operational efficiency  


7. Infrastructure Automation: 

 - Create a single script using `boto3` that: 

 - Deploys the entire infrastructure. 

 - Updates any component as required. 

 - Tears down everything when the application is no longer needed. 

 #####  Successfully created a versatile and efficient infrastructure management script using boto3 that empowers you to deploy, update, and tear down your entire application infrastructure effortlessly.