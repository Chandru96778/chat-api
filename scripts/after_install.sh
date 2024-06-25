#!/bin/bash

set -e

# Start new ECS task 
ecs-cli compose --project-name trc-chat-api-service service up --cluster-config trc-chat-api-cluster@us-east-1
