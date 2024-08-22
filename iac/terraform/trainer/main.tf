terraform {
  required_version = ">=0.14"
  required_providers {
    azurerm = {
      source = "hashicorp/azurerm"
    }
  }
}

provider "azurerm" {
  features {}
  skip_provider_registration = true  
}

locals {
  suffix                        = element(split("-", var.rg_name), length(split("-", var.rg_name)) - 1)
  databricksName                = format("%s-adb-%s", var.prefix, local.suffix)
  databricksAccessConnectorName = format("%s-unitycon-%s", var.prefix, local.suffix)
  datafactoryName               = format("%s-adf-%s", var.prefix, local.suffix)
  metastore_account_name                  = replace(lower(format("%smetastore%s", var.prefix, local.suffix)), "-", "")
  primary_metastore_name = replace(lower(format("metastore-%s", var.resource_group_location)), "-", "")
  catalog_name =  format("team_%s", lower(local.suffix))  
  }

# リソースグループが存在する場合はコメントアウト
# resource "azurerm_resource_group" "this" {
#   location = var.resource_group_location
#   name     = var.rg_name
#   tags     = var.tags
# }

# module "datafactory" {
#   source   = "./modules/services/datafactory"
#   name     = local.datafactoryName
#   location = var.resource_group_location
#   rg_name  = var.rg_name
#   tags     = var.tags
# }
module "databricks" {
  source   = "../modules/services/databricks"
  name     = local.databricksName
  location = var.resource_group_location
  rg_name  = var.rg_name
  metastore_id = module.unitycatalog_metastore.metastore_id
  catalog_name = local.catalog_name  
}

# trainer resources

module "unitycatalog_metastore" {
  source   = "../modules/services/unitycatalog_metastore"
  connector_name = local.databricksAccessConnectorName
  metastore_account_name = local.metastore_account_name
  metastore_container_name = local.primary_metastore_name
  location = var.resource_group_location
  rg_name  = var.rg_name
  databricks_account_id = var.databricks_account_id
}
