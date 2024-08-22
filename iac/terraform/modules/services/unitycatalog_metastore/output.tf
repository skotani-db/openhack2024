output "dl_connection_string" {
  value       = azurerm_storage_account.metastore_account.primary_connection_string
  description = "Connection string of storage account to be used in Secret Keyvault"
  sensitive   = true
}

output "storage_endpoint" {
  value       = azurerm_storage_account.metastore_account.primary_blob_endpoint
  description = "Azure Storage endpoint uri"
}

output "storage_id" {
  value = azurerm_storage_account.metastore_account.id
}

output "access_connector_id" {
  value = azurerm_databricks_access_connector.unity.id
}

output "metastore_id" {
  value = databricks_metastore.this.id
}