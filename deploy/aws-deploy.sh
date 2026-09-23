#!/usr/bin/env bash
# =============================================================================
# Rivet AWS Deployment Helper
# WeMakeDevs x AWS Hackathon 2026 - Ship It Track
# =============================================================================
set -euo pipefail

STACK_NAME="rivet-platform"
REGION="${AWS_REGION:-us-east-1}"

echo "=========================================================="
echo "🚀 Deploying Rivet to AWS Cloud (Ship It Track)"
echo "Region: ${REGION}"
echo "Stack:  ${STACK_NAME}"
echo "=========================================================="

# 1. Deploy CloudFormation Stack (S3 + IAM)
echo "📦 Step 1: Deploying CloudFormation infrastructure..."
aws cloudformation deploy \
  --template-file deploy/cloudformation.yaml \
  --stack-name "${STACK_NAME}" \
  --capabilities CAPABILITY_NAMED_IAM \
  --region "${REGION}"

# 2. Extract S3 Bucket Name
BUCKET_NAME=$(aws cloudformation describe-stacks \
  --stack-name "${STACK_NAME}" \
  --query "Stacks[0].Outputs[?OutputKey=='AuditBucketName'].OutputValue" \
  --output text \
  --region "${REGION}")

echo "✅ Infrastructure provisioned! Audit S3 Bucket: ${BUCKET_NAME}"

# 3. Build & Run locally or push to ECR
echo ""
echo "To run with Docker locally using this S3 bucket:"
echo "  export AWS_S3_BUCKET=${BUCKET_NAME}"
echo "  docker compose up --build"
echo ""
echo "To deploy container to AWS App Runner / ECS:"
echo "  1. aws ecr create-repository --repository-name rivet"
echo "  2. docker tag rivet:latest <account-id>.dkr.ecr.${REGION}.amazonaws.com/rivet:latest"
echo "  3. docker push <account-id>.dkr.ecr.${REGION}.amazonaws.com/rivet:latest"
echo "=========================================================="
