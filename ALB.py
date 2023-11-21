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
