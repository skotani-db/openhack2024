# Databricks notebook source
# MAGIC %md
# MAGIC ## 概要
# MAGIC
# MAGIC 本ノートブックは AI/BI コンテスト の Dashboard で使用するデータセットの定義を出力します。

# COMMAND ----------

# MAGIC %md
# MAGIC ## 事前準備

# COMMAND ----------

# MAGIC %run ./00_config

# COMMAND ----------

# 本ノートブックで利用するスキーマ
schema_name = f"03_data_analysis_by_gen_ai_for_{user_name}"
print(f"schema_name: `{schema_name}`")

# COMMAND ----------

# MAGIC %md
# MAGIC ## データセット作成コードの生成
# MAGIC AI/BIダッシュボードで使用する以下のデータセットのクエリを生成するセクションです
# MAGIC - ケース
# MAGIC - 問い合わせ
# MAGIC - クレーム
# MAGIC - 未クローズ
# MAGIC - 未クローズかつ優先度高い
# MAGIC - ケースのレビュー
# MAGIC
# MAGIC
# MAGIC なお、ケースのレビューは以下のCTASを用いて作成します
# MAGIC - ケースのレビューテーブル作成

# COMMAND ----------

print("-- ケース")
case = """select * from {catalog_name}.{schema_name}.case
"""
print(case)


print("-- 問い合わせ")
query = """select * from {catalog_name}.{schema_name}.case
where type = "問い合わせ"
"""
print(query)


print("-- クレーム")
claim = """SELECT * FROM {catalog_name}.{schema_name}.case
WHERE Type = 'クレーム';
"""
print(claim)


print("-- 未クローズ")
not_closed = """SELECT * FROM {catalog_name}.{schema_name}.case
WHERE IsClosed = false;
"""
print(not_closed)


print("-- 未クローズかつ優先度高い")
not_closed_high_priority = """SELECT * FROM {catalog_name}.{schema_name}.case
WHERE IsClosed = false and Priority = "高";
"""
print(not_closed_high_priority)


print("-- ケースのレビューテーブル作成")
review_ctas = """CREATE TABLE {catalog_name}.{schema_name}.case_classified AS 
SELECT *, ai_classify(
    Description,
    ARRAY(
      "ソフトウェアのバグ",
      "ハードウェアの動作不良",
      "ハードウェアの破損",
      "ネットワークの動作不良",
      "その他"
    )
  ) AS predict
FROMt eam_master.`03_data_analysis_by_gen_ai_for_ktn`
.`case`
LIMIT 100;
"""
print(review_ctas)


print("-- ケースのレビュー")
review = """SELECT * FROM {catalog_name}.{schema_name}.case_classified"""
print(review)

# COMMAND ----------

# MAGIC %md
# MAGIC ## ダッシュボード作成例
# MAGIC https://databricks.zoom.us/rec/share/A1JysmKQa7CSqkUp91-wyjNx8OoebMWXeKVWif7PzMoANsCRaF64HqzghhHUz-My.eMYNwpuoppwUbwJk
# MAGIC
# MAGIC Passcode: 1bmp3g%N
