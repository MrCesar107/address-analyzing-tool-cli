# =========================================
# Address Analyzing Terminal Tool
# By Cesar Augusto Rodriguez Lara
# https://github.com/MrCesar107
# =========================================

#!/bin/bash

SCRIPT_NAME="main.py"

if ! command -v python3 &> /dev/null
then
  echo "❌ Python3 is not installed"
  exit 1
fi

echo "📌 Creating virtual environment"
python3 -m venv venv
source venv/bin/activate

echo "📦 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo "🔑 Granting execution permissions to $SCRIPT_NAME..."
chmod +x $SCRIPT_NAME

echo "🚀 Making the script executable from any place"
sudo mkdir /usr/local/bin/address_analyzing_tool
sudo cp $SCRIPT_NAME /usr/local/bin/address_analyzing_tool/$SCRIPT_NAME

echo "alias address_analyzing_tool='python3 /usr/local/bin/address_analyzing_tool/$SCRIPT_NAME'" >> ~/.bashrc
source ~/.bashrc

echo "✅ Instalation completed."
