# CronEditor

Linux上のcronジョブをWebブラウザ経由で簡単に管理・編集できるGUIアプリケーションです。

## 機能

- 既存cronジョブの一覧表示（有効/無効両方）
- cronジョブの実行時間の編集（分、時、日、月、曜日）
- 複雑なcron式のサポート（*/5、1-30、mon-fri、sat,sunなど）
- ハイブリッドUI：シンプルなプルダウン⇔高度なテキスト入力の自動切替
- cronジョブの有効/無効切り替え
- インライン編集（保存・キャンセル）
- 開発者パネル（生crontab出力の確認）
- レスポンシブデザイン（PC・タブレット対応）

## 必要要件

- Python 3.8以上
- Linux環境
- crontabへの適切な権限
- 任意のユーザー（pi、ubuntu、その他何でも対応）

## インストール

### uv を使用する場合（推奨）

```bash
# uvのインストール（まだの場合）
curl -LsSf https://astral.sh/uv/install.sh | sh

# プロジェクトの設定
uv sync

# アプリケーションの起動
uv run python app.py
```

### venv を使用する場合

```bash
# 自動インストール（推奨）
./install.sh

# または手動インストール
python3 -m venv .venv
source .venv/bin/activate
pip install flask
python app.py
```

## 設定

`config.ini` ファイルでポート番号等を変更できます：

```ini
[server]
port = 5000
host = 0.0.0.0
debug = false
```

## systemdサービスとして実行

`./install.sh` を実行すると自動的にsystemdサービスが設定され、起動されます。

```bash
# サービスの開始
sudo systemctl start croneditor

# サービスの停止
sudo systemctl stop croneditor

# サービスの再起動
sudo systemctl restart croneditor

# 状態確認
sudo systemctl status croneditor

# 自動起動の有効化/無効化
sudo systemctl enable croneditor
sudo systemctl disable croneditor
```

## 使用方法

1. Webブラウザで `http://localhost:5000` にアクセス
2. 既存のcronジョブが一覧表示されます（有効/無効両方）
3. 「編集」ボタンをクリックして時間設定を変更
4. **UI自動切替**: 複雑なcron式は高度なテキスト入力、シンプルな値はプルダウンで表示
5. 「高度な設定」ボタンで手動でUI切替も可能
6. 「保存」ボタンで変更を確定、「キャンセル」ボタンで取り消し
7. チェックボックスでcronジョブの有効/無効を切り替え
8. 🛠️「Developer Panel」で生のcrontab出力を確認可能

## 制約事項

- 新規cronジョブの作成はできません
- cronジョブの削除はできません
- コマンドの編集はできません
- 既存cronジョブの時間設定のみ編集可能です

## cron式の例

このアプリケーションは以下のような複雑なcron式をサポートします：

- `*/5` - 5分毎
- `0-23/2` - 2時間毎
- `1-30` - 1日から30日まで
- `mon-fri` - 月曜日から金曜日まで
- `sat,sun` - 土曜日と日曜日
- `1,15,30` - 1日、15日、30日

## トラブルシューティング

### cronジョブが表示されない
- `crontab -l` でcronジョブが存在することを確認
- アプリケーション実行ユーザーにcrontabへの適切な権限があることを確認
- 🛠️「Developer Panel」でcrontabの生出力を確認

### systemdサービスでcronジョブが表示されない
- `sudo systemctl status croneditor` でサービス状態を確認
- `sudo journalctl -u croneditor` でログを確認
- PATH環境変数にcrontabコマンドのパスが含まれているか確認

### サービスが開始しない
- `sudo systemctl status croneditor` でエラーログを確認
- Python仮想環境のパスが正しく設定されていることを確認
- `./install.sh` を再実行してサービスファイルを更新