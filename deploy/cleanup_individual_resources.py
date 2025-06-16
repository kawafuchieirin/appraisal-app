#!/usr/bin/env python3
"""
Individual AWS Resources Cleanup Script
Real Estate Appraisal Application

This script provides more granular control over resource deletion
and can handle edge cases where CloudFormation deletion fails.
"""

import boto3
import sys
import time
from botocore.exceptions import ClientError, NoCredentialsError


class AWSResourceCleanup:
    def __init__(self, region='ap-northeast-1'):
        self.region = region
        self.stack_name = 'satei-app-v2'
        self.ecr_repositories = ['satei-django', 'satei-fastapi']
        
        try:
            self.cloudformation = boto3.client('cloudformation', region_name=region)
            self.ecr = boto3.client('ecr', region_name=region)
            self.ecs = boto3.client('ecs', region_name=region)
            self.elbv2 = boto3.client('elbv2', region_name=region)
            self.ec2 = boto3.client('ec2', region_name=region)
            self.logs = boto3.client('logs', region_name=region)
        except NoCredentialsError:
            print("❌ AWS credentials not found. Please configure AWS CLI first.")
            sys.exit(1)
    
    def print_status(self, message):
        print(f"🔵 [INFO] {message}")
    
    def print_success(self, message):
        print(f"✅ [SUCCESS] {message}")
    
    def print_warning(self, message):
        print(f"⚠️  [WARNING] {message}")
    
    def print_error(self, message):
        print(f"❌ [ERROR] {message}")
    
    def delete_cloudformation_stack(self):
        """Delete CloudFormation stack"""
        self.print_status(f"Checking CloudFormation stack: {self.stack_name}")
        
        try:
            # Check if stack exists
            self.cloudformation.describe_stacks(StackName=self.stack_name)
            
            self.print_status(f"Deleting CloudFormation stack: {self.stack_name}")
            self.cloudformation.delete_stack(StackName=self.stack_name)
            
            self.print_status("Waiting for stack deletion to complete...")
            waiter = self.cloudformation.get_waiter('stack_delete_complete')
            waiter.wait(
                StackName=self.stack_name,
                WaiterConfig={'Delay': 30, 'MaxAttempts': 40}
            )
            
            self.print_success("CloudFormation stack deleted successfully")
            return True
            
        except ClientError as e:
            if 'does not exist' in str(e):
                self.print_warning(f"CloudFormation stack '{self.stack_name}' not found")
                return True
            else:
                self.print_error(f"Failed to delete CloudFormation stack: {e}")
                return False
    
    def delete_ecr_repositories(self):
        """Delete ECR repositories and all images"""
        self.print_status("Deleting ECR repositories")
        
        for repo_name in self.ecr_repositories:
            try:
                # Check if repository exists
                self.ecr.describe_repositories(repositoryNames=[repo_name])
                
                self.print_status(f"Deleting ECR repository: {repo_name}")
                self.ecr.delete_repository(
                    repositoryName=repo_name,
                    force=True  # This deletes all images in the repository
                )
                self.print_success(f"ECR repository '{repo_name}' deleted successfully")
                
            except ClientError as e:
                if 'RepositoryNotFoundException' in str(e):
                    self.print_warning(f"ECR repository '{repo_name}' not found")
                else:
                    self.print_error(f"Failed to delete ECR repository '{repo_name}': {e}")
    
    def delete_ecs_services(self):
        """Delete ECS services that might be orphaned"""
        self.print_status("Checking for ECS services")
        
        try:
            cluster_name = f"{self.stack_name}-cluster"
            
            # List services in the cluster
            services_response = self.ecs.list_services(cluster=cluster_name)
            
            if services_response['serviceArns']:
                for service_arn in services_response['serviceArns']:
                    service_name = service_arn.split('/')[-1]
                    self.print_status(f"Updating ECS service to 0 desired count: {service_name}")
                    
                    # Scale down to 0
                    self.ecs.update_service(
                        cluster=cluster_name,
                        service=service_name,
                        desiredCount=0
                    )
                    
                    # Wait for tasks to stop
                    time.sleep(30)
                    
                    # Delete service
                    self.print_status(f"Deleting ECS service: {service_name}")
                    self.ecs.delete_service(
                        cluster=cluster_name,
                        service=service_name
                    )
                    
                self.print_success("ECS services deleted successfully")
            else:
                self.print_warning("No ECS services found")
                
        except ClientError as e:
            if 'ClusterNotFoundException' in str(e):
                self.print_warning(f"ECS cluster '{cluster_name}' not found")
            else:
                self.print_error(f"Failed to delete ECS services: {e}")
    
    def delete_load_balancers(self):
        """Delete Application Load Balancers"""
        self.print_status("Checking for Load Balancers")
        
        try:
            # List all load balancers
            response = self.elbv2.describe_load_balancers()
            
            for lb in response['LoadBalancers']:
                if self.stack_name in lb['LoadBalancerName']:
                    self.print_status(f"Deleting Load Balancer: {lb['LoadBalancerName']}")
                    self.elbv2.delete_load_balancer(LoadBalancerArn=lb['LoadBalancerArn'])
                    self.print_success(f"Load Balancer '{lb['LoadBalancerName']}' deleted")
                    
        except ClientError as e:
            self.print_error(f"Failed to delete Load Balancers: {e}")
    
    def delete_target_groups(self):
        """Delete Target Groups"""
        self.print_status("Checking for Target Groups")
        
        try:
            # List all target groups
            response = self.elbv2.describe_target_groups()
            
            for tg in response['TargetGroups']:
                if self.stack_name in tg['TargetGroupName']:
                    self.print_status(f"Deleting Target Group: {tg['TargetGroupName']}")
                    self.elbv2.delete_target_group(TargetGroupArn=tg['TargetGroupArn'])
                    self.print_success(f"Target Group '{tg['TargetGroupName']}' deleted")
                    
        except ClientError as e:
            self.print_error(f"Failed to delete Target Groups: {e}")
    
    def delete_log_groups(self):
        """Delete CloudWatch Log Groups"""
        self.print_status("Checking for CloudWatch Log Groups")
        
        try:
            log_group_name = '/ecs/satei-app'
            
            # Check if log group exists
            response = self.logs.describe_log_groups(logGroupNamePrefix=log_group_name)
            
            for log_group in response['logGroups']:
                if log_group['logGroupName'] == log_group_name:
                    self.print_status(f"Deleting Log Group: {log_group_name}")
                    self.logs.delete_log_group(logGroupName=log_group_name)
                    self.print_success(f"Log Group '{log_group_name}' deleted")
                    
        except ClientError as e:
            if 'ResourceNotFoundException' in str(e):
                self.print_warning("Log Group not found")
            else:
                self.print_error(f"Failed to delete Log Groups: {e}")
    
    def cleanup_all(self):
        """Perform complete cleanup"""
        print("=" * 60)
        print("AWS Resources Individual Cleanup")
        print("Real Estate Appraisal Application")
        print("=" * 60)
        print()
        
        # Get user confirmation
        response = input("⚠️  This will DELETE AWS resources. Are you sure? (yes/no): ")
        if response.lower() != 'yes':
            self.print_warning("Cleanup cancelled by user")
            return
        
        print()
        self.print_status("Starting individual resource cleanup...")
        print()
        
        # Delete in specific order to avoid dependency issues
        self.delete_ecs_services()
        print()
        
        self.delete_load_balancers()
        print()
        
        # Wait a bit for load balancers to be deleted
        time.sleep(30)
        
        self.delete_target_groups()
        print()
        
        self.delete_cloudformation_stack()
        print()
        
        self.delete_ecr_repositories()
        print()
        
        self.delete_log_groups()
        print()
        
        print("=" * 60)
        print("Individual Resource Cleanup Summary")
        print("=" * 60)
        print(f"Region: {self.region}")
        print(f"Stack Name: {self.stack_name}")
        print(f"ECR Repositories: {', '.join(self.ecr_repositories)}")
        print()
        self.print_success("Individual cleanup process completed!")
        print()
        self.print_warning("Please verify in AWS Console that all resources have been deleted")


def main():
    if len(sys.argv) > 1 and sys.argv[1] in ['-h', '--help']:
        print("""
Individual AWS Resources Cleanup Script

Usage: python3 cleanup_individual_resources.py [REGION]

Arguments:
  REGION    AWS region (default: ap-northeast-1)

This script provides granular control over resource deletion and can handle
cases where CloudFormation stack deletion fails.

Resources that will be deleted:
  - ECS Services and Clusters
  - Application Load Balancers
  - Target Groups
  - CloudFormation Stack
  - ECR Repositories
  - CloudWatch Log Groups
        """)
        return
    
    region = sys.argv[1] if len(sys.argv) > 1 else 'ap-northeast-1'
    
    cleanup = AWSResourceCleanup(region)
    cleanup.cleanup_all()


if __name__ == "__main__":
    main()