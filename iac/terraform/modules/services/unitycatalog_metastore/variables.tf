# ---------------------------------------------------------------------------------------------------------------------
# REQUIRED PARAMETERS
# You must provide a value for each of these parameters.
# ---------------------------------------------------------------------------------------------------------------------
variable "rg_name" {
  type        = string
  description = "Name of resource group manually created before terraform init"
}

variable "location" {
  type        = string
  description = "Region where datalake will be provisioned"
}


variable "connector_name" {
  type = string
}

variable "metastore_container_name" {
  type = string 
}
variable "metastore_account_name" {
  type = string 
}

variable databricks_account_id {
  type = string
}