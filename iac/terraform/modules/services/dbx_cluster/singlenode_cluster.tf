
data "databricks_spark_version" "unity_ml" {
  ml = true
  latest = true
  long_term_support = true
  depends_on = [
    azurerm_databricks_workspace.this
  ]
}


resource "databricks_cluster" "openhack_ML_UnityCatalog" {
  count=6
  
  num_workers = 0
  cluster_name = "single_openhack_ML_UnityCatalog_${count.index+1}"
  #   spark_version = "11.3.x-scala2.12"
  spark_version = data.databricks_spark_version.unity_ml.id
  spark_conf = {
    "spark.master":"local[*, 4]"
    "spark.databricks.cluster.profile":"singleNode"
    "spark.databricks.dataLineage.enabled" : "true",
    "spark.databricks.delta.preview.enabled" : "true"
  }
  azure_attributes {
    first_on_demand    = 1
    availability       = "SPOT_WITH_FALLBACK_AZURE"
    spot_bid_max_price = -1
  }
  node_type_id            = "Standard_DS3_v2"
  driver_node_type_id     = "Standard_DS3_v2"
  ssh_public_keys         = []
  custom_tags             = {
    "ResourceClass": "SingleNode"
  }
  spark_env_vars          = {}
  autotermination_minutes = 30
  enable_elastic_disk     = true
  data_security_mode      = "SINGLE_USER"
  runtime_engine          = "STANDARD"
  depends_on = [
    azurerm_databricks_workspace.this
  ]
}