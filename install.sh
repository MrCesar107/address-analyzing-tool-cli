#!/bin/bash

# =========================================
# Address Analyzing Terminal Tool - Installer
# By Cesar Augusto Rodriguez Lara
# https://github.com/MrCesar107
# =========================================

SCRIPT_NAME="address_analyzing_tool"
MAIN_SCRIPT="main.py"
PROJECT_DIR="$(pwd)"

# Check for Python3
if ! command -v python3 &>/dev/null;
then
    echo "❌ Python3 is not installed in your system."
    exit 1
fi

# Check if requirements.txt exists
if [ ! -f "$PROJECT_DIR/requirements.txt" ]; then
    echo "❌ requirements.txt not found in the project directory."
    exit 1
fi

# Create virtual environment
VENV_DIR="$PROJECT_DIR/venv"
if [ ! -d "$VENV_DIR" ]; then
    echo "📌 Creating virtual environment..."
    python3 -m venv "$VENV_DIR"
else
    echo "✅ Virtual environment already exists."
fi

# Install dependencies
source "$VENV_DIR/bin/activate"
pip install --upgrade pip
pip install -r "$PROJECT_DIR/requirements.txt"
if [ -f "$PROJECT_DIR/.env" ]; then
    echo "🔑 Loading environment variables from .env file."
fi
deactivate

# Create a wrapper script for global access
WRAPPER_SCRIPT="$(mktemp)"
cat > "$WRAPPER_SCRIPT" << 'EOF'
#!/bin/bash
PROJECT_DIR="/Users/mrcesar107/Documents/address-analyzing-tool-cli"
VENV_PATH="$PROJECT_DIR/venv"
source "$VENV_PATH/bin/activate"
python3 "$PROJECT_DIR/main.py" "$@"
EOF

# Make the temporary script executable
chmod +x "$WRAPPER_SCRIPT"

# Install globally
sudo mv "$WRAPPER_SCRIPT" /usr/local/bin/$SCRIPT_NAME

# Set permissions
sudo chmod +x /usr/local/bin/$SCRIPT_NAME

echo "✅ Installation completed successfully."

# Provide usage instructions
echo "
🔄 You can now use the tool globally by running:"
echo "    address_analyzing_tool --url https://example.com"

echo "
📌 Note: If you encounter any issues, ensure:"
echo "- The virtual environment exists at $PROJECT_DIR/venv."
echo "- The .env file contains the required API keys."