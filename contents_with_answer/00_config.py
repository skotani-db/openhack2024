# Databricks notebook source
# チーム名、あるいは、ユーザー名を設定
user_name = "team_01" # or "FirstName_LastName"
print(f"user_name: `{user_name}`")

# 利用するカタログ名を設定
catalog_name = f"openhachason_{user_name}"
print(f"catalog_name: `{catalog_name}`")

# COMMAND ----------

# ソースファイルを配置する Volume 名を設定
src_volume_name = "src_data"
src_schema_name = "default"
src_folder_name = "sample_data_01"
