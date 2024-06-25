set -e

# Stop existing ECS task 
ecs-cli compose --project-name trc-chat-api-service service down --cluster-config trc-chat-api-cluster@us-east-1
