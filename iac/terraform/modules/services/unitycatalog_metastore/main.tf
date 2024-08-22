resource "databricks_metastore" "this" {
  provider      = databricks.accounts
  name = "primary"
  storage_root = format("abfss://%s@%s.dfs.core.windows.net/",
  azurerm_storage_container.metastore_container.name  ,
  azurerm_storage_account.metastore_account.name)
  # force_destroy = true
  # default_data_access_config_id = var.access_connector_id
}


resource "databricks_metastore_data_access" "first" {
  metastore_id = databricks_metastore.this.id
  name         = "mi_dac"
  azure_managed_identity {
    access_connector_id = azurerm_databricks_access_connector.unity.id
  }
  is_default = true
}

resource "azurerm_databricks_access_connector" "unity" {
  name                = var.connector_name
  resource_group_name = var.rg_name
  identity {
    type = "SystemAssigned"
  }
  location = var.location
}


resource "azurerm_storage_account" "metastore_account" {
  name                            = var.metastore_account_name
  resource_group_name             = var.rg_name
  location                        = var.location
  account_tier                    = "Standard"
  account_replication_type        = "ZRS"
  account_kind                    = "StorageV2"
  is_hns_enabled                  = "true"
  min_tls_version                 = "TLS1_2"
  allow_nested_items_to_be_public = false
  blob_properties {
    container_delete_retention_policy {
      days = 7
    }
  }
  tags = {
    "iac" = "terraform"
  }
}

resource "azurerm_storage_container" "metastore_container" {
  name                  = var.metastore_container_name
  storage_account_name  = azurerm_storage_account.metastore_account.name
  container_access_type = "private"
}

resource "azurerm_role_assignment" "databrikcsConnector_BlobDataContributor" {
  role_definition_name = "Storage Blob Data Contributor"
  scope                = azurerm_storage_account.metastore_account.id
  principal_id         = azurerm_databricks_access_connector.unity.identity[0].principal_id
  lifecycle {
    ignore_changes = [
      name
    ]
  }
}