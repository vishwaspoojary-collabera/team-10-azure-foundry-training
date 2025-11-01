import azure.functions as func
import logging
from typing import Dict, Any
import json
import os
import pyodbc
from datetime import datetime

app = func.FunctionApp()

# Hardcoded SQL connection string
# Replace with your actual Azure SQL connection string
SQL_CONNECTION_STRING = "Driver={ODBC Driver 18 for SQL Server};Server=tcp:foundryallmembers.database.windows.net,1433;Database=ContosoDB;Uid=sqladmin;Pwd=Pa55w.rd1234;Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;"

@app.route(route="checkWarranty", methods=["POST", "GET"], auth_level=func.AuthLevel.FUNCTION)
def check_warranty(req: func.HttpRequest) -> func.HttpResponse:
    """
    Azure Function to check warranty status for a product and customer.
    
    Input (JSON):
    {
        "ProductID": "string",
        "CustomerName": "string"
    }
    
    Output (JSON):
    {
        "ProductID": "string",
        "CustomerName": "string",
        "WarrantyStatus": "string"
    }
    """
    logging.info('checkWarranty function processed a request.')
    
    try:
        # Get request data
        if req.method == "GET":
            product_id = req.params.get('ProductID')
            customer_name = req.params.get('CustomerName')
        else:
            try:
                req_body = req.get_json()
                product_id = req_body.get('ProductID')
                customer_name = req_body.get('CustomerName')
            except ValueError:
                return func.HttpResponse(
                    "Invalid JSON in request body",
                    status_code=400
                )
        
        # Validate input
        if not product_id or not customer_name:
            return func.HttpResponse(
                json.dumps({"error": "ProductID and CustomerName are required"}),
                status_code=400,
                mimetype="application/json"
            )
        
        # Get warranty status from Azure SQL Database
        warranty_status = get_warranty_status(product_id, customer_name)
        
        # Prepare response
        response_data = {
            "ProductID": product_id,
            "CustomerName": customer_name,
            "WarrantyStatus": warranty_status
        }
        
        return func.HttpResponse(
            json.dumps(response_data),
            status_code=200,
            mimetype="application/json"
        )
    
    except Exception as e:
        logging.error(f"Error processing request: {str(e)}")
        return func.HttpResponse(
            json.dumps({"error": f"Internal server error: {str(e)}"}),
            status_code=500,
            mimetype="application/json"
        )


def get_sql_connection_string() -> str:
    """
    Get SQL connection string (hardcoded or from environment variable).
    
    Returns:
        SQL connection string
    """
    # Check if connection string is set in environment variable first
    # If not, use the hardcoded value
    connection_string = os.environ.get("SQL_CONNECTION_STRING", SQL_CONNECTION_STRING)
    return connection_string


def get_warranty_status(product_id: str, customer_name: str) -> str:
    """
    Get warranty status for a product and customer from Azure SQL Database.
    
    Query joins ProductCatalog and WarrantyRecords tables to determine warranty status:
    - Checks if warranty record exists
    - Compares ExpiryDate with current date
    - Returns appropriate status
    
    Args:
        product_id: The product identifier
        customer_name: The customer name
        
    Returns:
        Warranty status string: "Active", "Expired", "Not Found", or "Error"
    """
    logging.info(f"Checking warranty for ProductID: {product_id}, Customer: {customer_name}")
    
    if not product_id or not customer_name:
        return "Invalid Request"
    
    connection = None
    cursor = None
    
    try:
        # Get connection string
        connection_string = get_sql_connection_string()
        
        # Establish connection using pyodbc
        logging.info("Establishing connection to Azure SQL Database")
        connection = pyodbc.connect(connection_string)
        cursor = connection.cursor()
        
        # SQL Query Template
        # This query joins ProductCatalog and WarrantyRecords tables
        # to find the warranty record matching ProductID and CustomerName
        sql_query = """
        SELECT 
            wr.[Status] AS WarrantyStatus,
            wr.[ExpiryDate],
            wr.[WarrantyID],
            pc.[ProductName],
            pc.[WarrantyYears]
        FROM [dbo].[WarrantyRecords] wr
        INNER JOIN [dbo].[ProductCatalog] pc ON wr.[ProductID] = pc.[ProductID]
        WHERE wr.[ProductID] = ? 
            AND wr.[CustomerName] = ?
        ORDER BY wr.[PurchaseDate] DESC
        """
        
        logging.info(f"Executing SQL query for ProductID: {product_id}, CustomerName: {customer_name}")
        cursor.execute(sql_query, (product_id, customer_name))
        
        row = cursor.fetchone()
        
        if row is None:
            logging.info("No warranty record found")
            return "Not Found"
        
        # Extract warranty status and expiry date
        warranty_status = row[0]  # Status from WarrantyRecords table
        expiry_date = row[1]  # ExpiryDate
        
        # Check if warranty has expired based on ExpiryDate
        if expiry_date:
            # Handle different date formats from SQL Server
            if isinstance(expiry_date, datetime):
                expiry_date_obj = expiry_date
            elif isinstance(expiry_date, str):
                try:
                    # Try parsing common SQL Server date formats
                    expiry_date_obj = datetime.strptime(expiry_date.split('.')[0], "%Y-%m-%d %H:%M:%S")
                except ValueError:
                    try:
                        expiry_date_obj = datetime.strptime(expiry_date, "%Y-%m-%d")
                    except ValueError:
                        logging.warning(f"Unable to parse expiry date: {expiry_date}")
                        expiry_date_obj = None
            else:
                expiry_date_obj = expiry_date
            
            if expiry_date_obj:
                current_date = datetime.now().date()
                if expiry_date_obj < current_date:
                    logging.info(f"Warranty expired on {expiry_date_obj}")
                    return "Expired"
        
        # Return the status from the database
        # If Status column contains values like "Active", "Expired", etc., return that
        # Otherwise, determine based on expiry date
        if warranty_status:
            status = str(warranty_status).strip()
            # If status is already "Expired" or "Active", return as is
            if status.lower() in ["active", "expired", "pending", "cancelled"]:
                return status
        
        # Default: if not expired and status exists, consider it Active
        return "Active"
    
    except pyodbc.Error as e:
        logging.error(f"SQL Database error: {str(e)}")
        return "Error"
    except Exception as e:
        logging.error(f"Error checking warranty status: {str(e)}")
        return "Error"
    finally:
        # Close database connections
        if cursor:
            cursor.close()
        if connection:
            connection.close()
            logging.info("Database connection closed")
