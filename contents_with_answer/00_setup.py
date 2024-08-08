# Databricks notebook source
# MAGIC %md
# MAGIC ## カタログを作成
# MAGIC
# MAGIC ※ TEAM 用のカタログを作成した場合には、チームメンバーに対して`ALL PRIVILEGES`権限を付与してください。
# MAGIC
# MAGIC - [Unity Catalog の特権の管理 - Azure Databricks | Microsoft Learn](https://learn.microsoft.com/ja-jp/azure/databricks/data-governance/unity-catalog/manage-privileges/#grant-permissions-on-objects-in-a-unity-catalog-metastore)
# MAGIC

# COMMAND ----------

# MAGIC %run ./00_config

# COMMAND ----------

create_catalog_ddl = f"""
CREATE CATALOG IF NOT EXISTS {catalog_name}
"""
print(create_catalog_ddl)
spark.sql(create_catalog_ddl)

# COMMAND ----------

# MAGIC %md
# MAGIC ## End
