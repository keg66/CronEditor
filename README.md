# CronEditor

Raspberry Pi上のcronジョブをWebブラウザ経由で簡単に管理・編集できるGUIアプリケーションです。

## 機能

- 既存cronジョブの一覧表示
- cronジョブの実行時間の編集（分、時、日、月、曜日）
- cronジョブの有効/無効切り替え
- インライン編集（保存・キャンセル）
- レスポンシブデザイン（PC・タブレット対応）

## 必要要件

- Python 3.8以上
- Linux環境（Raspberry Pi推奨）
- crontabへの適切な権限

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
# 自動インストール
./install.sh

# または手動インストール
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
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

```bash
# サービスの開始
sudo systemctl start croneditor

# サービスの停止
sudo systemctl stop croneditor

# サービスの再起動
sudo systemctl restart croneditor

# 状態確認
sudo systemctl status croneditor
```

## 使用方法

1. Webブラウザで `http://localhost:5000` にアクセス
2. 既存のcronジョブが一覧表示されます
3. 「編集」ボタンをクリックして時間設定を変更
4. 「保存」ボタンで変更を確定、「キャンセル」ボタンで取り消し
5. チェックボックスでcronジョブの有効/無効を切り替え

## 制約事項

- 新規cronジョブの作成はできません
- cronジョブの削除はできません
- コマンドの編集はできません
- 既存cronジョブの時間設定のみ編集可能です

## トラブルシューティング

### cronジョブが表示されない
- `crontab -l` でcronジョブが存在することを確認
- アプリケーション実行ユーザーにcrontabへの適切な権限があることを確認

### サービスが開始しない
- `sudo systemctl status croneditor` でエラーログを確認
- Python仮想環境のパスが正しく設定されていることを確認