# Databricks notebook source
# MAGIC %md
# MAGIC ## Delta Live Tables によるデータエンジニアリング

# COMMAND ----------

# MAGIC %md 
# MAGIC ### 本ノートブックの目的：Delta Live Tablesによってパイプライン構築がモダナイズされることを実感する
# MAGIC
# MAGIC Q1. Delta Live Tablesのセッティングを行なってください<br>
# MAGIC Q2. パイプラインを実行する（Run a Pipeline）<br>
# MAGIC Q3. DAGを調べる（Exploring the DAG）

# COMMAND ----------

# MAGIC %md
# MAGIC ## 事前準備

# COMMAND ----------

# MAGIC %run ./00_config

# COMMAND ----------

# 本ノートブックで利用するスキーマを作成
schema_name = f"02_data_engineering_for_{user_name}"
print(f"schema_name: `{schema_name}`")
spark.sql(
    f"""
    CREATE SCHEMA IF NOT EXISTS {catalog_name}.{schema_name}
    """
)

# COMMAND ----------

# 本ノートブックで利用する Volume を作成
volume_name = "src_file_volume_01"
print(f"volume_name: `{volume_name}`")
spark.sql(
    f"""
    CREATE VOLUME IF NOT EXISTS {catalog_name}.{schema_name}.{volume_name}
    """
)

# COMMAND ----------

# 本ノートブックで利用するソースファイルを Volume に移動
import os

current_dir = os.getcwd()
file_dir = f"file:{current_dir}/includes/00_data/sample_data_01"
volume_dir = f"/Volumes/{catalog_name}/{schema_name}/{volume_name}"

dbutils.fs.cp(file_dir, volume_dir, recurse=True)
display(dbutils.fs.ls(volume_dir))

# COMMAND ----------

# MAGIC %md
# MAGIC
# MAGIC ### Q1. Delta Live Tablesのセッティングを行なってください

# COMMAND ----------

# MAGIC %md
# MAGIC
# MAGIC このセクションでは、コースウェアに付属しているノートブックを使って、今までのセクションで構築したメダリオンアーキテクチャのパイプラインを構築します。 　<br>
# MAGIC 次のレッスンでは、ノートブックの内容について見ていきます。　<br>
# MAGIC 　<br>
# MAGIC 1. サイドバーの**Workflows**ボタンをクリックします。
# MAGIC 1. **Delta Live Tables**タブを選択します。
# MAGIC 1. **Create Pipeline**をクリックします。
# MAGIC 1. **Pipeline name**を入力します。これらの名前は一意である必要があるため、上記のセルに記載されている **`pipeline_name`** を使用することをおすすめします。
# MAGIC 1. **Product Edition**は**Advanced**のままにします。
# MAGIC 1. **Pipeline mode**では、**Trigger**を選択します。
# MAGIC    * このフィールドでは、パイプラインの実行方法を指定します。
# MAGIC    * **Trigger**パイプラインは一度だけ実行され、次の手動またはスケジュールされた更新まではシャットダウンします。
# MAGIC    * **Continuous**パイプラインは継続的に実行され、新しいデータが到着するとそのデータを取り込みます。 レイテンシとコスト要件に基づいてモードを選択してください。
# MAGIC 1. **Source code**では、ナビゲーターを使って**02_delta_live_table_conf**という付録のノートブックを探して選択します。
# MAGIC    * このドキュメントは標準のDatabricksノートブックですが、SQL構文はDLTテーブル宣言に特化しています。
# MAGIC    * 次のエクササイズでは、構文について見ていきます。
# MAGIC 1. **Destination**フィールドに、**`Storage options`**にて**`Unity Catalog`**をチェックし、下記のセルで **`catalog_name`**と**`schema_name`** の隣に表示されているカタログ名スキーマ名を指定します。
# MAGIC    * このフィールドは任意です。指定しなかった場合、テーブルはメタストアに登録されませんが、引き続きDBFSでは使用できます。 このオプションに関して詳しく知りたい場合は、こちらの<a href="https://learn.microsoft.com/ja-jp/azure/databricks/delta-live-tables/publish-data" target="_blank">ドキュメント</a>を参考にしてください。
# MAGIC 1. **Cluster mode**を**Fixed size**に設定し、ワーカーの数を **`1`** （1つ）に設定します。
# MAGIC    * **Enable Auto Scaling**、**Min workers**、**Max workers**はパイプラインをクラスタ処理する際の基盤となるワーカー構成を制御します。 
# MAGIC 1. **Configuratione**にて**Add configuration**を選択して下記の 3 つを設定します。
# MAGIC    * **Key**に**mypipeline.catalog_name**を、Value にその key に相当する下記セルの値を設定
# MAGIC    * **Key**に**mypipeline.schema_name**を、Value にその key に相当する下記セルの値を設定
# MAGIC 1. **Create**をクリックします。

# COMMAND ----------

print("-- Pipeline name")
pipeline_name = f"dlt_pipe_by_{user_name}"
print(f"pipeline_name: {pipeline_name}")
print("")
print("-- Configuration")
print(f"mypipeline.catalog_name: {catalog_name}")
print(f"mypipeline.schema_name: {schema_name}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Q2. パイプラインを実行する（Run a Pipeline）
# MAGIC
# MAGIC パイプラインを構築したら、そのパイプラインを実行します。
# MAGIC
# MAGIC 1. **Development**を選択し、Developmentモードでパイプラインを実行します。
# MAGIC 2. **Start**をクリックします。
# MAGIC

# COMMAND ----------

# MAGIC %md
# MAGIC
# MAGIC ## Q3. DAGを調べる（Exploring the DAG）
# MAGIC
# MAGIC パイプラインが完了すると、実行フローがグラフ化されます。
# MAGIC
# MAGIC テーブルを選択すると詳細を確認できます。

# COMMAND ----------

# MAGIC %md
# MAGIC
# MAGIC ## Q4. パイプラインの修正
# MAGIC
# MAGIC `02_delta_live_table_conf`ノートブックに記載されている ToDo を実施してパイプラインを修正してください。修正後、下記の手順で DAG が変更されます。
# MAGIC
# MAGIC 1. **Development**を選択し、Developmentモードでパイプラインを実行します。
# MAGIC 2. **Start**、あるいは、**Full refresh all**をクリックします。
# MAGIC 3. 修正内容に応じて DAG が変更されることを確認します。

# COMMAND ----------

# MAGIC %md
# MAGIC ## End
