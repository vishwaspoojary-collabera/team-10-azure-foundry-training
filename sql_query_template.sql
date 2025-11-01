-- SQL Query Template for checkWarranty Function
-- This query joins ProductCatalog and WarrantyRecords tables
-- to retrieve warranty status based on ProductID and CustomerName

-- Input Parameters:
--   @ProductID: Product identifier
--   @CustomerName: Customer name

-- Output:
--   Warranty Status (Active, Expired, Not Found, etc.)

SELECT 
    wr.[Status] AS WarrantyStatus,
    wr.[ExpiryDate],
    wr.[WarrantyID],
    wr.[PurchaseDate],
    pc.[ProductName],
    pc.[ProductID],
    pc.[WarrantyYears],
    pc.[Category],
    pc.[Model]
FROM [dbo].[WarrantyRecords] wr
INNER JOIN [dbo].[ProductCatalog] pc ON wr.[ProductID] = pc.[ProductID]
WHERE wr.[ProductID] = @ProductID 
    AND wr.[CustomerName] = @CustomerName
ORDER BY wr.[PurchaseDate] DESC;

-- Alternative: Query to check if warranty is expired based on ExpiryDate
-- Status Logic:
--   - If ExpiryDate < Current Date: "Expired"
--   - If ExpiryDate >= Current Date: "Active" (or use Status column value)
--   - If no record found: "Not Found"

-- Example usage in stored procedure format:
/*
CREATE PROCEDURE GetWarrantyStatus
    @ProductID VARCHAR(50),
    @CustomerName VARCHAR(100)
AS
BEGIN
    SELECT 
        CASE 
            WHEN wr.[ExpiryDate] < GETDATE() THEN 'Expired'
            WHEN wr.[Status] IS NOT NULL THEN wr.[Status]
            ELSE 'Active'
        END AS WarrantyStatus,
        wr.[ExpiryDate],
        wr.[WarrantyID],
        pc.[ProductName]
    FROM [dbo].[WarrantyRecords] wr
    INNER JOIN [dbo].[ProductCatalog] pc ON wr.[ProductID] = pc.[ProductID]
    WHERE wr.[ProductID] = @ProductID 
        AND wr.[CustomerName] = @CustomerName
    ORDER BY wr.[PurchaseDate] DESC;
END
*/
