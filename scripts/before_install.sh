#!/bin/bash

set -e

# Stop existing ECS task (example assuming using ECS CLI)
ecs-cli compose --project-name <your-project-name> service down --cluster-config <your-cluster-config>
