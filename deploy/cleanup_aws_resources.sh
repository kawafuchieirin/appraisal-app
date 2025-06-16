#!/bin/bash

# =============================================================================
# AWS Resources Cleanup Script
# Real Estate Appraisal Application
# =============================================================================

set -e

# Configuration
REGION=${1:-ap-northeast-1}
STACK_NAME="satei-app-v2"
ECR_REPOSITORIES=("satei-django" "satei-fastapi")

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if AWS CLI is configured
check_aws_cli() {
    if ! command -v aws &> /dev/null; then
        print_error "AWS CLI is not installed. Please install it first."
        exit 1
    fi
    
    if ! aws sts get-caller-identity &> /dev/null; then
        print_error "AWS CLI is not configured. Please run 'aws configure' first."
        exit 1
    fi
    
    print_success "AWS CLI is configured and ready"
}

# Function to check if CloudFormation stack exists
check_stack_exists() {
    aws cloudformation describe-stacks --stack-name "$STACK_NAME" --region "$REGION" &> /dev/null
}

# Function to delete CloudFormation stack
delete_cloudformation_stack() {
    print_status "Checking CloudFormation stack: $STACK_NAME"
    
    if check_stack_exists; then
        print_status "Deleting CloudFormation stack: $STACK_NAME"
        aws cloudformation delete-stack --stack-name "$STACK_NAME" --region "$REGION"
        
        print_status "Waiting for stack deletion to complete..."
        aws cloudformation wait stack-delete-complete --stack-name "$STACK_NAME" --region "$REGION"
        
        if [ $? -eq 0 ]; then
            print_success "CloudFormation stack deleted successfully"
        else
            print_error "CloudFormation stack deletion failed or timed out"
            print_warning "Please check the AWS console for details"
        fi
    else
        print_warning "CloudFormation stack '$STACK_NAME' not found"
    fi
}

# Function to delete ECR repositories
delete_ecr_repositories() {
    print_status "Checking and deleting ECR repositories"
    
    for repo in "${ECR_REPOSITORIES[@]}"; do
        print_status "Checking ECR repository: $repo"
        
        if aws ecr describe-repositories --repository-names "$repo" --region "$REGION" &> /dev/null; then
            print_status "Deleting all images in repository: $repo"
            
            # Get all image tags
            image_tags=$(aws ecr list-images --repository-name "$repo" --region "$REGION" --query 'imageIds[*].imageTag' --output text 2>/dev/null || echo "")
            
            if [ -n "$image_tags" ] && [ "$image_tags" != "None" ]; then
                print_status "Found images with tags: $image_tags"
                aws ecr batch-delete-image --repository-name "$repo" --region "$REGION" --image-ids imageTag=latest imageTag=v1.0 2>/dev/null || true
            fi
            
            # Delete repository
            print_status "Deleting ECR repository: $repo"
            aws ecr delete-repository --repository-name "$repo" --region "$REGION" --force
            print_success "ECR repository '$repo' deleted successfully"
        else
            print_warning "ECR repository '$repo' not found"
        fi
    done
}

# Function to cleanup orphaned resources
cleanup_orphaned_resources() {
    print_status "Checking for orphaned resources..."
    
    # Check for ECS services
    print_status "Checking for ECS services..."
    services=$(aws ecs list-services --cluster "${STACK_NAME}-cluster" --region "$REGION" --query 'serviceArns' --output text 2>/dev/null || echo "")
    if [ -n "$services" ] && [ "$services" != "None" ]; then
        print_warning "Found ECS services that may need manual cleanup"
        echo "$services"
    fi
    
    # Check for Load Balancers
    print_status "Checking for Load Balancers..."
    albs=$(aws elbv2 describe-load-balancers --region "$REGION" --query "LoadBalancers[?contains(LoadBalancerName, '$STACK_NAME')].LoadBalancerArn" --output text 2>/dev/null || echo "")
    if [ -n "$albs" ] && [ "$albs" != "None" ]; then
        print_warning "Found Load Balancers that may need manual cleanup"
        echo "$albs"
    fi
    
    # Check for Security Groups
    print_status "Checking for Security Groups..."
    sgs=$(aws ec2 describe-security-groups --region "$REGION" --query "SecurityGroups[?contains(GroupName, '$STACK_NAME')].GroupId" --output text 2>/dev/null || echo "")
    if [ -n "$sgs" ] && [ "$sgs" != "None" ]; then
        print_warning "Found Security Groups that may need manual cleanup"
        echo "$sgs"
    fi
}

# Function to display cleanup summary
display_summary() {
    echo ""
    echo "=========================================="
    echo "AWS Resources Cleanup Summary"
    echo "=========================================="
    echo "Region: $REGION"
    echo "CloudFormation Stack: $STACK_NAME"
    echo "ECR Repositories: ${ECR_REPOSITORIES[*]}"
    echo ""
    print_success "Cleanup process completed!"
    echo ""
    print_warning "Please verify in AWS Console that all resources have been deleted:"
    echo "- CloudFormation: https://console.aws.amazon.com/cloudformation/"
    echo "- ECR: https://console.aws.amazon.com/ecr/"
    echo "- ECS: https://console.aws.amazon.com/ecs/"
    echo "- EC2 (Load Balancers): https://console.aws.amazon.com/ec2/"
}

# Main execution
main() {
    echo ""
    echo "=========================================="
    echo "AWS Resources Cleanup Script"
    echo "Real Estate Appraisal Application"
    echo "=========================================="
    echo ""
    
    # Confirmation prompt
    read -p "⚠️  This will DELETE all AWS resources for the Real Estate Appraisal App. Are you sure? (yes/no): " -r
    if [[ ! $REPLY =~ ^[Yy][Ee][Ss]$ ]]; then
        print_warning "Cleanup cancelled by user"
        exit 0
    fi
    
    echo ""
    print_status "Starting cleanup process..."
    echo ""
    
    # Check prerequisites
    check_aws_cli
    
    # Delete resources in order
    delete_cloudformation_stack
    echo ""
    
    delete_ecr_repositories
    echo ""
    
    cleanup_orphaned_resources
    echo ""
    
    display_summary
}

# Help function
show_help() {
    echo "Usage: $0 [REGION]"
    echo ""
    echo "Delete all AWS resources for the Real Estate Appraisal Application"
    echo ""
    echo "Arguments:"
    echo "  REGION    AWS region (default: ap-northeast-1)"
    echo ""
    echo "Examples:"
    echo "  $0                    # Use default region (ap-northeast-1)"
    echo "  $0 us-west-2         # Use us-west-2 region"
    echo ""
    echo "Resources that will be deleted:"
    echo "  - CloudFormation stack: $STACK_NAME"
    echo "  - ECR repositories: ${ECR_REPOSITORIES[*]}"
    echo "  - All associated resources (VPC, ALB, ECS, etc.)"
    echo ""
}

# Check for help flag
if [[ "$1" == "-h" || "$1" == "--help" ]]; then
    show_help
    exit 0
fi

# Run main function
main