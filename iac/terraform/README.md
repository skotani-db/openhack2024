# デプロイ方法

## 前提

- VSCode devcontainer 環境
- サブスクリプション所有者
- - あらかじめリソースグループを作成済みの場合はリソースグループ所有者でOK

## デプロイリソース

### トレーナー用リソースグループ

- databricks workspace
- azure data lake storage gen2
- databricks access connector

### 生徒用リソースグループ

- databricks workspace

## 方法


- .devcontainer に基づいてdevcontainer を立ち上げます。
- environments内の作業ではそれぞれのファイル名にふくまれるアンダースコアを置換してファイルとして機能するように変更します。（git公開の都合で.を_に置き換えています）
- - config.sh 内の内容を設定する
- - - MODE : terrform の apply / plan 設定。必要に応じて"plan" に変更することでterraform planに変更することができます。
- - - SUBSCRIPTION_ID: リソースを作成する
- - - ENV: environments内のフォルダを指定する。devでOK
- - student.tfvars と trainer.tfvars を設定する
- - - metastore_id: trainer
- - - rg_name: 講師用のリソースグループ名
- - - databricks_account_id: [Databrics Account コンソール](https://accounts.azuredatabricks.net/users?account_id=5673373b-a975-4748-8863-c0b9d279bf65)で確認できる DatabrickアカウントID
- 以下のコマンドを実行します。  
実行した際にaz loginが試行された場合は、対象のテナントでログインをしてください。以前のtfstateファイルが残っている場合は削除してから実行してください
```
source ./environments/dev/config.sh
bash ./code/deploy_trainer.sh

```

- - student.tfvars を設定する
- - - metastore_id: trainer リソース設定後にアカウントコンソール内のカタログ管理画面から取得。～.dfs.core.windows.net/{id}となっている
- ./code/student_rg_list.txt 上に生徒用リソースグループ名を記入します。
- 以下のコマンドを実行します。  
実行した際にaz loginが試行された場合は、対象のテナントでログインをしてください。以前のtfstateファイルが残っている場合は削除してから実行してください
```
source ./environments/dev/config.sh
bash ./code/deploy_student.sh

```