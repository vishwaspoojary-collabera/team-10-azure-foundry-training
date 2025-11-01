# Azure Function Deployment Script (Windows/PowerShell)
# Prerequisites: Azure CLI must be installed and logged in

# Configuration - Update these values
$RESOURCE_GROUP = "team-10"
$FUNCTION_APP_NAME = "ascendion-team10"
$LOCATION = "eastus2"
$STORAGE_ACCOUNT = "team10blobstorage"
$PYTHON_VERSION = "3.11"
$SCM_DO_BUILD_DURING_DEPLOYMENT = "false"
Write-Host "Starting Azure Function Deployment..." -ForegroundColor Green

# Step 5: Deploy using Azure Functions Core Tools
Write-Host "`nDeploying function code..."
func azure functionapp publish $FUNCTION_APP_NAME --build remote

Write-Host "`nDeployment completed!" -ForegroundColor Green
Write-Host "Function URL: ascendion-team10-b2d7aha6cscqhtfv.eastus-01.azurewebsites.net"