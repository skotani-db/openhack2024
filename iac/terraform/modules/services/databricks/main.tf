

resource "azurerm_databricks_workspace" "this" {
  name                = var.name
  location            = var.location
  resource_group_name = var.rg_name
  sku                 = var.sku
  public_network_access_enabled        = true
  tags = {
    "iac" = "terraform"
  }
}

data "databricks_current_user" "me" {
  depends_on = [azurerm_databricks_workspace.this]
}

resource "databricks_metastore_assignment" "this" {
  metastore_id = var.metastore_id
  workspace_id = azurerm_databricks_workspace.this.workspace_id
}

resource "databricks_catalog" "this" {
  name    = var.catalog_name
  metastore_id = var.metastore_id
  comment = "Openhack Team 用"
  depends_on = [databricks_metastore_assignment.this]
}

resource "databricks_grants" "grants" {
  catalog = databricks_catalog.this.name
  grant {
    principal  = "account users"
    privileges = ["ALL_PRIVILEGES"]
  }
}

resource "databricks_schema" "things" {
  catalog_name = databricks_catalog.this.id
  name        = "default" 
}

resource "databricks_default_namespace_setting" "this" {
  namespace {
    value = databricks_catalog.this.name
  }
}