resource "databricks_sql_endpoint" "this" {
    name = "openhack_sql_serverless"
    cluster_size     = "Small"
    max_num_clusters = 1
    enable_serverless_compute = true
    auto_stop_mins = 60
    depends_on = [
        azurerm_databricks_workspace.this
    ]
}
