variable "rg_name" {
  type    = string
  # default = "Hands-On-Master"
}

variable "resource_group_location" {
  type        = string
  default     = "eastus"
  description = "Location of the resource group."
}

variable "tags" {
  type = object({
    project = string
  })
  default = {
    project : "openhack-lakehouse"
  }
}

variable "prefix" {
  type    = string
  default = "oph-lh"
}

variable "metastore_id" {
  description = "metastore id"
}