#!/bin/bash

# CronEditor インストールスクリプト

echo "CronEditor をインストールします..."

# 現在のディレクトリを取得
INSTALL_DIR=$(pwd)

# Python仮想環境の作成
echo "Python仮想環境を作成しています..."
python3 -m venv .venv
source .venv/bin/activate

# 依存関係のインストール
echo "依存関係をインストールしています..."
pip install --upgrade pip
pip install -e .

# systemdサービスファイルのコピー（実際のパスに置き換え）
echo "systemdサービスを設定しています..."
sudo sed "s|/home/pi/CronEditor|${INSTALL_DIR}|g" croneditor.service > /tmp/croneditor.service
sudo mv /tmp/croneditor.service /etc/systemd/system/

# systemdサービスの有効化
sudo systemctl daemon-reload
sudo systemctl enable croneditor
sudo systemctl start croneditor

echo "インストールが完了しました！"
echo "サービス状態: "
sudo systemctl status croneditor --no-pager
echo ""
echo "Webブラウザで http://localhost:5000 にアクセスしてください"
echo ""
echo "サービスの管理コマンド:"
echo "  開始: sudo systemctl start croneditor"
echo "  停止: sudo systemctl stop croneditor"
echo "  再起動: sudo systemctl restart croneditor"
echo "  状態確認: sudo systemctl status croneditor"