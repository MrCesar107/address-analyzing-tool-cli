# =========================================
# Address Analyzing Terminal Tool
# By Cesar Augusto Rodriguez Lara
# https://github.com/MrCesar107
# =========================================

#!/bin/bash

SCRIPT_NAME="main.py"
VENV_DIR="venv"

if ! command -v python3 &> /dev/null
then
    echo "❌ Python3 is not installed in your system"
    exit 1
fi

if [ ! -d "$VENV_DIR" ]; then
    echo "📌 Creando virtual env..."
    python3 -m venv "$VENV_DIR"
else
    echo "✅ Virtual env detected."
fi

echo "🔄 Activating virtual env..."
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
elif [ -f "venv/Scripts/activate" ]; then
    source venv/Scripts/activate
else
    echo "❌ Error: Virtual env not found. Creating..."
    python3 -m venv venv
    source venv/bin/activate
fi

if [ -z "$VIRTUAL_ENV" ]; then
    echo "❌ Virtual env cannot be activated"
    exit 1
fi

echo "📦 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo "🔑 Granting execution permissions to $SCRIPT_NAME..."
chmod +x "$SCRIPT_NAME"

echo "🚀 Making script executable from any place..."
sudo cp "$SCRIPT_NAME" /usr/local/bin/

SHELL_CONFIG="$HOME/.bashrc"
if [ "$SHELL" = "/usr/bin/zsh" ]; then
    SHELL_CONFIG="$HOME/.zshrc"
elif [ "$SHELL" = "/usr/bin/fish" ]; then
    SHELL_CONFIG="$HOME/.config/fish/config.fish"
fi

echo "alias address_analyzing_tool='source $VENV_DIR/bin/activate && python3 /usr/local/bin/$SCRIPT_NAME'" >> "$SHELL_CONFIG"
source "$SHELL_CONFIG"

echo "✅ Installation completed"
