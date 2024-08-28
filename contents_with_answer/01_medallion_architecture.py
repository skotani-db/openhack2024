# Databricks notebook source
# MAGIC %md
# MAGIC ## 01. メダリオンアーキテクチャに基づいたデータエンジニアリング概要
# MAGIC
# MAGIC
# MAGIC

# COMMAND ----------

# MAGIC %md
# MAGIC ### 本ノートブックの目的：Databricksにおけるデータ処理の基礎と[メダリオンアーキテクチャ](https://www.databricks.com/jp/glossary/medallion-architecture)について理解を深める

# COMMAND ----------

# MAGIC %md
# MAGIC ![メダリオンアーキテクチャ](https://raw.githubusercontent.com/microsoft/openhack-for-lakehouse-japanese/main/images/day1_01__introduction/delta-lake-medallion-architecture-2.jpeg)

# COMMAND ----------

# MAGIC %md
# MAGIC ### メダリオンアーキテクチャとは
# MAGIC
# MAGIC データを、Bronze、Silver、Goldの３層の論理レイヤーで管理する手法です。Databricks では、すべてのレイヤーを Delta Lake 形式で保持することが推奨されています。
# MAGIC
# MAGIC | #    | データレイヤー | 概要                                                   | 類義語             |
# MAGIC | ---- | -------------- | ------------------------------------------------------ | ------------------ |
# MAGIC | 1    | Bronze         | 未加工データを保持するレイヤー                             | Raw     |
# MAGIC | 2    | Silver         | クレンジング・適合済みデータデータを保持するレイヤー | Enriched      |
# MAGIC | 3    | Gold           | ビジネスレベルのキュレート済みデータを保持するレイヤー   | Curated |
# MAGIC
# MAGIC
# MAGIC 参考リンク
# MAGIC
# MAGIC - [Medallion Architecture | Databricks](https://databricks.com/jp/glossary/medallion-architecture)
# MAGIC - [What's Data Lake ?](https://docs.google.com/presentation/d/1pViTuBmK4nDWg4n8_yGKbN4gOPbbFUTw/edit?usp=sharing&ouid=110902353658379996895&rtpof=true&sd=true)
# MAGIC
# MAGIC
# MAGIC 次のメリットがあります。
# MAGIC
# MAGIC - データレイヤーごとの役割分担が可能となること
# MAGIC - データレイクにてデータ品質が担保できるようなること
# MAGIC - ローデータから再度テーブルの再作成が容易となること
# MAGIC
# MAGIC
# MAGIC **Bronzeの特徴について**
# MAGIC - 取り込んだローデータのコピーを、スキーマ展開を許可するなど、そのまま保持。
# MAGIC - ロード日時などの監査列（システム列）を必要に応じて付加。
# MAGIC - データ型を文字型として保持するなどの対応によりデータ損失の発生を低減。
# MAGIC - データを削除する場合には、物理削除ではなく、論理削除が推奨。
# MAGIC
# MAGIC **Silverの特徴について**
# MAGIC - Bronze のデータに処理を行い、クレンジング・適合済みデータを保持。
# MAGIC - スキーマを適用し、dropDuplicates関数を利用した重複排除などによるデータ品質チェック処理を実施。
# MAGIC - 最小限、あるいは「適度な」変換およびデータクレンジングルールのみを適用。
# MAGIC - Bronze との関係性が、「1 対多」方式となることもある。
# MAGIC
# MAGIC **Goldの特徴について**
# MAGIC - 企業や部門のデータプロジェクトにおいてビジネス上の課題を解決するように編成・集計したデータを保持。
# MAGIC - アクセス制御リスト（ACL）や行レベルセキュリティ等のデータアクセス制御を考慮することが多い。
# MAGIC
# MAGIC **参考:データソースの種類について**
# MAGIC - [Unity Catalogにおける外部ロケーション](https://learn.microsoft.com/ja-jp/azure/databricks/spark/latest/spark-sql/language-manual/sql-ref-external-locations)

# COMMAND ----------

# MAGIC %md
# MAGIC ## 事前準備

# COMMAND ----------

# MAGIC %run ./00_config

# COMMAND ----------

# 本ノートブックで利用するスキーマを作成
schema_name = f"01_medallion_architecture_for_{user_name}"
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

checkpint_volume_name = "checkpint_volume_01"
print(f"checkpint_volume_name: `{checkpint_volume_name}`")
spark.sql(
    f"""
    CREATE VOLUME IF NOT EXISTS {catalog_name}.{schema_name}.{checkpint_volume_name}
    """
)

# COMMAND ----------

# 本ノートブックで利用するソースファイルを Volume に移動
file_dir = f"/Volumes/{catalog_name}/{src_schema_name}/{src_volume_name}/{src_folder_name}"
volume_dir = f"/Volumes/{catalog_name}/{schema_name}/{volume_name}"
checkpint_volume_dir = f"/Volumes/{catalog_name}/{schema_name}/{checkpint_volume_name}"

dbutils.fs.cp(file_dir, volume_dir, recurse=True)
display(dbutils.fs.ls(volume_dir))

# COMMAND ----------

# MAGIC %md
# MAGIC ## Q1. Bronzeテーブルのパイプラインを作成してください。
# MAGIC
# MAGIC 取り込み対象のデータについては、下記のオブジェクトと同等のものとなっております。
# MAGIC
# MAGIC - [Product2 | Salesforce プラットフォームのオブジェクトリファレンス | Salesforce Developers](https://developer.salesforce.com/docs/atlas.ja-jp.object_reference.meta/object_reference/sforce_api_objects_product2.htm)
# MAGIC - [PricebookEntry | Salesforce プラットフォームのオブジェクトリファレンス | Salesforce Developers](https://developer.salesforce.com/docs/atlas.ja-jp.object_reference.meta/object_reference/sforce_api_objects_pricebookentry.htm)

# COMMAND ----------

# MAGIC %md
# MAGIC ### 実践例

# COMMAND ----------

src_file_path__1_1_1 = f"{volume_dir}/Product2.csv"
tgt_table_name__1_1_1 = f"{catalog_name}.{schema_name}.product2__bronze"

# COMMAND ----------

# CSV の中身をチェック
data = dbutils.fs.head(src_file_path__1_1_1, 700)
print(data)

# COMMAND ----------

# `product2__bronze`テーブルを作成
create_tbl_ddl = f"""
CREATE OR REPLACE TABLE {tgt_table_name__1_1_1}
(
    `Id` STRING,
    `Name` STRING,
    `ProductCode` STRING,
    `Description` STRING,
    `IsActive` STRING,
    `CreatedDate` STRING,
    `CreatedById` STRING,
    `LastModifiedDate` STRING,
    `LastModifiedById` STRING,
    `SystemModstamp` STRING,
    `Family` STRING,
    `ExternalDataSourceId` STRING,
    `ExternalId` STRING,
    `DisplayUrl` STRING,
    `QuantityUnitOfMeasure` STRING,
    `IsDeleted` STRING,
    `IsArchived` STRING,
    `LastViewedDate` STRING,
    `LastReferencedDate` STRING,
    `StockKeepingUnit` STRING,
    _datasource STRING,
    _ingest_timestamp timestamp
)
USING delta
"""
spark.sql(create_tbl_ddl)

# COMMAND ----------

# ソースからデータを読み込む
df = (
    spark.read.format("csv")
    .option("header", "true")
    .option("inferSchema", "False")
    .load(src_file_path__1_1_1)
)

# 監査列として`_datasource`列と`_ingest_timestamp`列を追加
df = (
    df.select("*", "_metadata")
    .withColumn("_datasource", df["_metadata.file_path"])
    .withColumn("_ingest_timestamp", df["_metadata.file_modification_time"])
    .drop("_metadata")
)

# COMMAND ----------

# 処理後の結果を確認
df.display()

# COMMAND ----------

# `product2__bronze`テーブルへ`append`によりデータの書き込みを実施
(
    df.write.format("delta")
    .mode("append")
    .option("mergeSchema", "true")
    .saveAsTable(tgt_table_name__1_1_1)
)

# COMMAND ----------

# データが書き込まれたことを確認
display(spark.table(f"{tgt_table_name__1_1_1}"))

# COMMAND ----------

# MAGIC %md
# MAGIC ### ToDo `pricebook_entry__bronze`のパイプラインを作成してください。

# COMMAND ----------

src_file_path__1_2_1 = f"{volume_dir}/PricebookEntry.csv"
tgt_table_name__1_2_1 = f"{catalog_name}.{schema_name}.pricebook_entry__bronze"

# COMMAND ----------

# ToDo CSV の中身をチェック
data = dbutils.fs.head(src_file_path__1_2_1, 700)
print(data)

# COMMAND ----------

# `pricebook_entry__bronze`テーブルを作成
create_tbl_ddl = f"""
CREATE OR REPLACE TABLE {tgt_table_name__1_2_1}
(
    `Id` STRING,
    `Name` STRING,
    `Pricebook2Id` STRING,
    `Product2Id` STRING,
    `UnitPrice` STRING,
    `IsActive` STRING,
    `UseStandardPrice` STRING,
    `CreatedDate` STRING,
    `CreatedById` STRING,
    `LastModifiedDate` STRING,
    `LastModifiedById` STRING,
    `SystemModstamp` STRING,
    `ProductCode` STRING,
    `IsDeleted` STRING,
    `IsArchived` STRING,
    _datasource STRING,
    _ingest_timestamp timestamp
)
USING delta
"""
spark.sql(create_tbl_ddl)

# COMMAND ----------

# ToDo 書き込み処理を記述してください
# ソースからデータを読み込む
df = (
    spark.read.format("csv")
    .option("header", "true")
    .option("inferSchema", "False")
    .load(src_file_path__1_2_1)
)

# 監査列として`_datasource`列と`_ingest_timestamp`列を追加
df = (
    df.select("*", "_metadata")
    .withColumn("_datasource", df["_metadata.file_path"])
    .withColumn("_ingest_timestamp", df["_metadata.file_modification_time"])
    .drop("_metadata")
)

# COMMAND ----------

# 処理後の結果を確認
df.display()

# COMMAND ----------

# ToDo `pricebook_entry__bronze`テーブルへ書き込みを実施してください。
(
    df.write.format("delta")
    .mode("append")
    .option("mergeSchema", "true")
    .saveAsTable(tgt_table_name__1_2_1)
)

# COMMAND ----------

# データが書き込まれたことを確認
display(spark.table(f"{tgt_table_name__1_2_1}"))

# COMMAND ----------

# MAGIC %md
# MAGIC ## Q2. Silver テーブルのパイプラインを作成してください

# COMMAND ----------

# MAGIC %md
# MAGIC ### 実践例

# COMMAND ----------

src_table_name__2_1_1 = f"{catalog_name}.{schema_name}.product2__bronze"
tgt_table_name__2_1_1 = f"{catalog_name}.{schema_name}.product2__silver"

# COMMAND ----------

# `product2__silver`テーブルを作成
spark.sql(
    f"""
    CREATE OR REPLACE TABLE {tgt_table_name__2_1_1}
    (
        `Id` STRING,
        `Name` STRING,
        `ProductCode` STRING,
        `Description` STRING,
        `IsActive` BOOLEAN,
        `CreatedDate` TIMESTAMP,
        `CreatedById` STRING,
        `LastModifiedDate` TIMESTAMP,
        `LastModifiedById` STRING,
        `SystemModstamp` TIMESTAMP,
        `Family` STRING,
        `ExternalDataSourceId` STRING,
        `ExternalId` STRING,
        `DisplayUrl` STRING,
        `QuantityUnitOfMeasure` STRING,
        `IsDeleted` BOOLEAN,
        `IsArchived` BOOLEAN,
        `LastViewedDate` TIMESTAMP,
        `LastReferencedDate` TIMESTAMP,
        `StockKeepingUnit` STRING,
        _datasource STRING,
        _ingest_timestamp timestamp
    )
    USING delta
    """
)

# COMMAND ----------

# 下記の処理を実行したデータフレーム（df）を作成
## 1. `product2__bronze`テーブルから主キー（`Id`）ごとに`_ingest_timestamp`列の最大日を抽出したサブセットを作成
## 2. 主キー＋`_ingest_timestamp`列の条件で、1のサブセットと`product2__bronzeテーブルを結合
## 3. `product2__bronze`テーブルのデータ型をシルバーテーブルと同一のデータ型に変換
brz_to_slv_sql = f'''
with slv_records (
SELECT
    Id,
    MAX(_ingest_timestamp) AS max_ingest_timestamp
    FROM
        {src_table_name__2_1_1}
    GROUP BY
        id
)
SELECT
    brz.`Id`,
    brz.`Name`,
    brz.`ProductCode`,
    brz.`Description`,
    brz.`IsActive`::BOOLEAN,
    brz.`CreatedDate`::TIMESTAMP,
    brz.`CreatedById`,
    brz.`LastModifiedDate`::TIMESTAMP,
    brz.`LastModifiedById`,
    brz.`SystemModstamp`::TIMESTAMP,
    brz.`Family`,
    brz.`ExternalDataSourceId`,
    brz.`ExternalId`,
    brz.`DisplayUrl`,
    brz.`QuantityUnitOfMeasure`,
    brz.`IsDeleted`::BOOLEAN,
    brz.`IsArchived`::BOOLEAN,
    brz.`LastViewedDate`::TIMESTAMP,
    brz.`LastReferencedDate`::TIMESTAMP,
    brz.`StockKeepingUnit`,
    brz._datasource,
    brz._ingest_timestamp::timestamp
    
    FROM
        {src_table_name__2_1_1} AS brz
    INNER JOIN 
        slv_records AS slv
        ON 
            brz.id =  slv.id
            AND brz._ingest_timestamp =  slv.max_ingest_timestamp
'''
df = spark.sql(brz_to_slv_sql)

# dropDuplicates関数にて、主キーの一意性を保証。連携日ごとの一意性が保証されないことがあるため。
df = df.drop_duplicates(['Id'])

# COMMAND ----------

# 処理後の結果を確認
df.display()

# COMMAND ----------

# 一時ビューから`product2__silver`に対して、MERGE文によりアップサート処理を実施。
## 一時ビューを作成
temp_view_name = f'_tmp_product2__silver'
df.createOrReplaceTempView(temp_view_name)

## Merge処理を実行
returned_df = spark.sql(f'''
MERGE INTO {tgt_table_name__2_1_1} AS tgt
  USING {temp_view_name} AS src
  
  ON tgt.Id = src.Id 

  WHEN MATCHED
  AND tgt._ingest_timestamp < src._ingest_timestamp
    THEN UPDATE SET *
  WHEN NOT MATCHED
    THEN INSERT *
''')
returned_df.display()

# COMMAND ----------

# データが書き込まれたことを確認
display(spark.table(tgt_table_name__2_1_1))

# COMMAND ----------

# MAGIC %md
# MAGIC ### ToDo `pricebook_entry__silver`のパイプラインを作成してください。
# MAGIC
# MAGIC `pricebook_entry__silver`テーブルにおける主キーは`Id`列です。

# COMMAND ----------

src_table_name__2_2_1 = f"{catalog_name}.{schema_name}.pricebook_entry__bronze"
tgt_table_name__2_2_1 = f"{catalog_name}.{schema_name}.pricebook_entry__silver"

# COMMAND ----------

# Silver テーブルを作成
spark.sql(
    f"""
    CREATE OR REPLACE TABLE {tgt_table_name__2_2_1}
    (
        `Id` STRING,
        `Name` STRING,
        `Pricebook2Id` STRING,
        `Product2Id` STRING,
        `UnitPrice` DECIMAL(16, 0),
        `IsActive` BOOLEAN,
        `UseStandardPrice` BOOLEAN,
        `CreatedDate` TIMESTAMP,
        `CreatedById` STRING,
        `LastModifiedDate` TIMESTAMP,
        `LastModifiedById` STRING,
        `SystemModstamp` TIMESTAMP,
        `ProductCode` STRING,
        `IsDeleted` BOOLEAN,
        `IsArchived` BOOLEAN,
        _datasource STRING,
        _ingest_timestamp timestamp
    )
    USING delta
    """
)

# COMMAND ----------

# ToDo 下記の処理を実行したデータフレーム（df）を作成してください。
## 1. `pricebook_entry__bronze`テーブルから主キー（`Id`）ごとに`_ingest_timestamp`列の最大日を抽出したサブセットを作成
## 2. 主キー＋`_ingest_timestamp`列の条件で、1のサブセットと`pricebook_entry__bronze`テーブルを結合
## 3. `pricebook_entry__bronze`テーブルのデータ型をシルバーテーブルと同一のデータ型に変換
brz_to_slv_sql = f'''
with slv_records (
SELECT
    Id,
    MAX(_ingest_timestamp) AS max_ingest_timestamp
    FROM
        {src_table_name__2_2_1}
    GROUP BY
        id
)
SELECT
    brz.`Id`,
    brz.`Name`,
    brz.`Pricebook2Id`,
    brz.`Product2Id`,
    brz.`UnitPrice`::DECIMAL(16, 0),
    brz.`IsActive`::BOOLEAN,
    brz.`UseStandardPrice`::BOOLEAN,
    brz.`CreatedDate`::TIMESTAMP,
    brz.`CreatedById`,
    brz.`LastModifiedDate`::TIMESTAMP,
    brz.`LastModifiedById`,
    brz.`SystemModstamp`::TIMESTAMP,
    brz.`ProductCode`,
    brz.`IsDeleted`::BOOLEAN,
    brz.`IsArchived`::BOOLEAN,
    brz._datasource,
    brz._ingest_timestamp::timestamp
    
    FROM
        {src_table_name__2_2_1} AS brz
    INNER JOIN 
        slv_records AS slv
        ON 
            brz.id =  slv.id
            AND brz._ingest_timestamp =  slv.max_ingest_timestamp
'''
df = spark.sql(brz_to_slv_sql)

# dropDuplicates関数にて、主キーの一意性を保証。連携日ごとの一意性が保証されないことがあるため。
df = df.drop_duplicates(['Id'])

# COMMAND ----------

# 処理後の結果を確認
df.display()

# COMMAND ----------

# ToDo 一時ビューから`pricebook_entry__silver`テーブルに対して、MERGE文によりアップサート処理を実施してください。
## 一時ビューを作成
temp_view_name = f'_tmp_pricebook_entry__silver'
df.createOrReplaceTempView(temp_view_name)


returned_df = spark.sql(f'''
MERGE INTO {tgt_table_name__2_2_1} AS tgt
  USING {temp_view_name} AS src
  
  ON tgt.Id = src.Id 

  WHEN MATCHED
  AND tgt._ingest_timestamp < src._ingest_timestamp
    THEN UPDATE SET *
  WHEN NOT MATCHED
    THEN INSERT *
''')
returned_df.display()

# COMMAND ----------

# データが書き込まれたことを確認
display(spark.table(tgt_table_name__2_1_1))

# COMMAND ----------

# MAGIC %md
# MAGIC ## Q3. Gold Tableのパイプラインを作成してください

# COMMAND ----------

# MAGIC %md
# MAGIC ### 実践例

# COMMAND ----------

src_table_name__3_1_1 = f"{catalog_name}.{schema_name}.product2__silver"
tgt_table_name__3_1_1 = f"{catalog_name}.{schema_name}.product_count_by_family"

# COMMAND ----------

# テーブルが存在する場合に Drop
spark.sql(
    f"""
    DROP TABLE IF EXISTS {tgt_table_name__3_1_1}
    """
)

# COMMAND ----------

# 書き込み想定のデータフレームを作成
sql = f"""
SELECT
  Family,
  COUNT(*) AS product_count
  FROM
    {src_table_name__3_1_1}
  GROUP BY
    ALL
"""
df = spark.sql(sql)

# COMMAND ----------

# 処理後の結果を確認
df.display()

# COMMAND ----------

# `product_count_by_family`テーブルへ書き込み
df.write.mode("overwrite").saveAsTable(tgt_table_name__3_1_1)

# COMMAND ----------

# データが書き込まれたことを確認
display(spark.table(tgt_table_name__3_1_1))

# COMMAND ----------

# MAGIC %md
# MAGIC ### ToDo `d_product`パイプラインを作成してください。
# MAGIC
# MAGIC `Product2`をベースに、`pricebook_entry`にある`UnitPrice`を追加したデータのテーブルを作成してください。
# MAGIC
# MAGIC ```sql
# MAGIC SELECT
# MAGIC   prd.*
# MAGIC     EXCEPT (
# MAGIC       _datasource,
# MAGIC       _ingest_timestamp
# MAGIC     ),
# MAGIC   pbk.UnitPrice
# MAGIC   FROM
# MAGIC     {src_table_name__3_2_1} prd
# MAGIC   INNER JOIN 
# MAGIC     {src_table_name__3_2_2} pbk
# MAGIC   on 
# MAGIC     prd.id = pbk.Product2Id
# MAGIC ```

# COMMAND ----------

src_table_name__3_2_1 = f"{catalog_name}.{schema_name}.product2__silver"
src_table_name__3_2_2 = f"{catalog_name}.{schema_name}.pricebook_entry__silver"
tgt_table_name__3_2_1 = f"{catalog_name}.{schema_name}.d_product"

# COMMAND ----------

# テーブルが存在する場合に Drop
spark.sql(
    f"""
    DROP TABLE IF EXISTS {tgt_table_name__3_2_1}
    """
)

# COMMAND ----------

# ToDo 書き込み想定のデータフレームを作成してください。
sql = f"""
SELECT
  prd.*
    EXCEPT (
      _datasource,
      _ingest_timestamp
    ),
  pbk.UnitPrice
  FROM
    {src_table_name__3_2_1} prd
  INNER JOIN 
    {src_table_name__3_2_2} pbk
  on 
    prd.id = pbk.Product2Id
"""
df = spark.sql(sql)

# COMMAND ----------

# 処理後の結果を確認
df.display()

# COMMAND ----------

# ToDo `d_product`テーブルへ書き込みを実施してください。
df.write.mode("overwrite").saveAsTable(tgt_table_name__3_2_1)

# COMMAND ----------

# データが書き込まれたことを確認
display(spark.table(tgt_table_name__3_2_1))

# COMMAND ----------

# MAGIC %md
# MAGIC ## Challenge1. Databricks Auto Loader によりデータ取り込みを実施してください。
# MAGIC
# MAGIC こちらは Challenge のコンテンツであり、実施は任意です。
# MAGIC
# MAGIC Databricks Auto Loader（自動ローダー）について詳しく知りたい方は、以下のドキュメントをご参照ください。
# MAGIC
# MAGIC > 自動ローダーでは、追加の設定を行わなくても、クラウド ストレージに到着した新しいデータ ファイルが段階的かつ効率的に処理されます。
# MAGIC
# MAGIC 引用元：[自動ローダー - Azure Databricks | Microsoft Learn](https://learn.microsoft.com/ja-jp/azure/databricks/ingestion/cloud-object-storage/auto-loader/)
# MAGIC
# MAGIC 取り込み対象のデータについては、下記のオブジェクトと同等のものとなっております。
# MAGIC
# MAGIC - [Campaign | Salesforce プラットフォームのオブジェクトリファレンス | Salesforce Developers](https://developer.salesforce.com/docs/atlas.ja-jp.object_reference.meta/object_reference/sforce_api_objects_campaign.htm)
# MAGIC - [Account | Salesforce プラットフォームのオブジェクトリファレンス | Salesforce Developers](https://developer.salesforce.com/docs/atlas.ja-jp.object_reference.meta/object_reference/sforce_api_objects_account.htm)
# MAGIC

# COMMAND ----------

# MAGIC %md
# MAGIC ### 実践例

# COMMAND ----------

src_file_path__c1_1_1 = f"{volume_dir}/Campaign.csv"
checkpoint_dir__c1_1_1 = f"{checkpint_volume_dir}/campaign"
tgt_table_name__c1_1_1 = f"{catalog_name}.{schema_name}.campaign__bronze"

schema__c1_1_1 = """
`id` STRING,
`IsDeleted` STRING,
`Name` STRING,
`ParentId` STRING,
`Type` STRING,
`Status` STRING,
`StartDate` STRING,
`EndDate` STRING,
`ExpectedRevenue` STRING,
`BudgetedCost` STRING,
`ActualCost` STRING,
`ExpectedResponse` STRING,
`NumberSent` STRING,
`IsActive` STRING,
`Description` STRING,
`NumberOfLeads` STRING,
`NumberOfConvertedLeads` STRING,
`NumberOfContacts` STRING,
`NumberOfResponses` STRING,
`NumberOfOpportunities` STRING,
`NumberOfWonOpportunities` STRING,
`AmountAllOpportunities` STRING,
`AmountWonOpportunities` STRING,
`OwnerId` STRING,
`CreatedDate` STRING,
`CreatedById` STRING,
`LastModifiedDate` STRING,
`LastModifiedById` STRING,
`SystemModstamp` STRING,
`LastActivityDate` STRING,
`LastViewedDate` STRING,
`LastReferencedDate` STRING,
`CampaignMemberRecordTypeId` STRING
"""

# COMMAND ----------

# CSV の中身をチェック
data = dbutils.fs.head(src_file_path__c1_1_1, 700)
print(data)

# COMMAND ----------

# Bronzeテーブルを作成
create_tbl_ddl = f"""
CREATE OR REPLACE TABLE {tgt_table_name__c1_1_1}
(
{schema__c1_1_1},
_rescued_data STRING,
_datasource STRING,
_ingest_timestamp timestamp

)
USING delta
"""
spark.sql(create_tbl_ddl)

# COMMAND ----------

# Databricks Auto Loader で利用するチェックポイントを初期化
dbutils.fs.rm(checkpoint_dir__c1_1_1, True)

# COMMAND ----------

# ソースからデータを読み込む
df = (
    spark.readStream.format("cloudFiles")
    .option("cloudFiles.format", "csv")
    .option("cloudFiles.schemaLocation", checkpoint_dir__c1_1_1)
    .option("cloudFiles.schemaHints", schema__c1_1_1)
    .option("header", True)
    .load(src_file_path__c1_1_1)
)

# ファイル メタデータ列を追加
df = df.select("*", "_metadata")

# ファイル メタデータ列に基づき監査列として`_datasource`列と`_ingest_timestamp`列を追加
df = (
    df.select("*", "_metadata")
    .withColumn("_datasource", df["_metadata.file_path"])
    .withColumn("_ingest_timestamp", df["_metadata.file_modification_time"])
)

# ファイル メタデータ列を削除
df = df.drop("_metadata")

# COMMAND ----------

# `checkpoint_dir__c1_1_1`変数をチェックポイントとして指定して、書き込み処理を実施。
(
    df.writeStream.trigger(availableNow=True)
    .option("checkpointLocation", checkpoint_dir__c1_1_1)
    .trigger(availableNow=True)
    .toTable(tgt_table_name__c1_1_1)
)

# COMMAND ----------

# データが書き込まれたことを確認
display(spark.table(f"{tgt_table_name__c1_1_1}"))

# COMMAND ----------

# MAGIC %md
# MAGIC ### ToDo `account__bronze`のパイプラインを Databricks Auto Loader にて作成してください。

# COMMAND ----------

src_file_path__c1_2_1 = f"{volume_dir}/Account.csv"
checkpoint_dir__c1_2_1 = f"{checkpint_volume_dir}/account"
tgt_table_name__c1_2_1 = f"{catalog_name}.{schema_name}.account__bronze"

schema__c1_2_1 = """
`id` STRING,
`IsDeleted` STRING, 
`MasterRecordId` STRING, 
`Name` STRING, 
`Type` STRING, 
`ParentId` STRING, 
`BillingStreet` STRING, 
`BillingCity` STRING, 
`BillingState` STRING, 
`BillingPostalCode` STRING, 
`BillingCountry` STRING, 
`BillingLatitude` STRING, 
`BillingLongitude` STRING, 
`BillingGeocodeAccuracy` STRING, 
`ShippingStreet` STRING, 
`ShippingCity` STRING, 
`ShippingState` STRING, 
`ShippingPostalCode` STRING, 
`ShippingCountry` STRING, 
`ShippingLatitude` STRING, 
`ShippingLongitude` STRING, 
`ShippingGeocodeAccuracy` STRING, 
`Phone` STRING, 
`Fax` STRING, 
`AccountNumber` STRING, 
`Website` STRING, 
`PhotoUrl` STRING, 
`Sic` STRING, 
`Industry` STRING, 
`AnnualRevenue` STRING, 
`NumberOfEmployees` STRING, 
`Ownership` STRING, 
`TickerSymbol` STRING, 
`Description` STRING, 
`Rating` STRING, 
`Site` STRING, 
`OwnerId` STRING, 
`CreatedDate` STRING, 
`CreatedById` STRING, 
`LastModifiedDate` STRING, 
`LastModifiedById` STRING, 
`SystemModstamp` STRING, 
`LastActivityDate` STRING, 
`LastViewedDate` STRING, 
`LastReferencedDate` STRING, 
`Jigsaw` STRING, 
`JigsawCompanyId` STRING, 
`CleanStatus` STRING, 
`AccountSource` STRING, 
`DunsNumber` STRING, 
`Tradestyle` STRING, 
`NaicsCode` STRING, 
`NaicsDesc` STRING, 
`YearStarted` STRING, 
`SicDesc` STRING, 
`DandbCompanyId` STRING
"""

# COMMAND ----------

# CSV の中身をチェック
data = dbutils.fs.head(src_file_path__c1_2_1, 1000)
print(data)

# COMMAND ----------

# Bronzeテーブルを作成
create_tbl_ddl = f"""
CREATE OR REPLACE TABLE {tgt_table_name__c1_2_1}
(
{schema__c1_2_1},
_rescued_data STRING,
_datasource STRING,
_ingest_timestamp timestamp

)
USING delta
"""
spark.sql(create_tbl_ddl)

# COMMAND ----------

# Hint コード修正後に想定通りに動作しない場合にはDatabricks Auto Loader で利用するチェックポイントを初期化してください。
# Databricks Auto Loader で利用するチェックポイントを初期化
dbutils.fs.rm(checkpoint_dir__c1_2_1, True)

# COMMAND ----------

# ToDo `checkpoint_dir__c1_2_1`変数を`cloudFiles.schemaLocation`に指定して、ソースからデータの読み込み処理を記述してください。
df = (
    spark.readStream.format("cloudFiles")
    .option("cloudFiles.format", "csv")
    .option("cloudFiles.schemaLocation", checkpoint_dir__c1_2_1)
    .option("cloudFiles.schemaHints", schema__c1_2_1)
    .option("header", True)
    .load(src_file_path__c1_2_1)
)

# COMMAND ----------

# ToDo 監査列として`_datasource`列と`_ingest_timestamp`列を追加（`_metadata`列は追加しない）
# ファイル メタデータ列を追加
df = df.select("*", "_metadata")

# ファイル メタデータ列に基づき監査列として`_datasource`列と`_ingest_timestamp`列を追加
df = (
    df.select("*", "_metadata")
    .withColumn("_datasource", df["_metadata.file_path"])
    .withColumn("_ingest_timestamp", df["_metadata.file_modification_time"])
)

# ファイル メタデータ列を削除
df = df.drop("_metadata")

# COMMAND ----------

# ToDo `checkpoint_dir__c1_2_1`変数をチェックポイントとして指定して、書き込み処理を実施してください。
(
    df.writeStream.trigger(availableNow=True)
    .option("checkpointLocation", checkpoint_dir__c1_2_1)
    .trigger(availableNow=True)
    .toTable(tgt_table_name__c1_2_1)
)

# COMMAND ----------

# データが書き込まれたことを確認
display(spark.table(f"{tgt_table_name__c1_2_1}"))

# COMMAND ----------

# MAGIC %md
# MAGIC ## 事後処理

# COMMAND ----------

# ストリーム処理を停止
for stream in spark.streams.active:
    stream.stop()

# COMMAND ----------

# MAGIC %md
# MAGIC ## End
