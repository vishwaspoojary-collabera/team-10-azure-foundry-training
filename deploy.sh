#!/bin/bash
# Azure Function Deployment Script (Linux/Mac)
# Prerequisites: Azure CLI must be installed and logged in

# Configuration - Update these values
RESOURCE_GROUP="team-10"
FUNCTION_APP_NAME="ascendion-team10"
LOCATION="eastus"
STORAGE_ACCOUNT="team10blobstorage"
PYTHON_VERSION="3.11"

echo "Starting Azure Function Deployment..."

# Step 1: Check if logged in
echo -e "\nChecking Azure login..."
if ! az account show &>/dev/null; then
    echo "Not logged in. Please login..."
    az login
fi

# Step 2: Create Resource Group (if not exists)
echo -e "\nChecking/Creating Resource Group..."
az group create --name $RESOURCE_GROUP --location $LOCATION --output none

# Step 3: Create Storage Account (if not exists)
echo -e "\nChecking/Creating Storage Account..."
az storage account create \
    --name $STORAGE_ACCOUNT \
    --location $LOCATION \
    --resource-group $RESOURCE_GROUP \
    --sku Standard_LRS \
    --output none

# Step 4: Create Function App (if not exists)
echo -e "\nChecking/Creating Function App..."
az functionapp create \
    --resource-group $RESOURCE_GROUP \
    --consumption-plan-location $LOCATION \
    --runtime python \
    --runtime-version $PYTHON_VERSION \
    --functions-version 4 \
    --name $FUNCTION_APP_NAME \
    --storage-account $STORAGE_ACCOUNT \
    --output none

# Step 5: Deploy using Azure Functions Core Tools
echo -e "\nDeploying function code..."
func azure functionapp publish $FUNCTION_APP_NAME

echo -e "\nDeployment completed!"
echo "Function URL: ascendion-team10-b2d7aha6cscqhtfv.eastus-01.azurewebsites.net"

