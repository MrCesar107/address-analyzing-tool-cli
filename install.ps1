if (-Not (Get-Command python3 -ErrorAction SilentlyContinue)) {
    Write-Host "❌ Python3 is not installed."
    exit 1
}

$scriptPath = (Get-Location).Path + "\main.py"

Write-Host "📌 Creating virtual environment..."
python3 -m venv venv
venv\Scripts\Activate

Write-Host "📦 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

Write-Host "🚀 Config global alias..."
$profilePath = "$HOME\Documents\WindowsPowerShell\profile.ps1"

if (!(Test-Path $profilePath)) {
    New-Item -ItemType File -Path $profilePath -Force
}

Add-Content -Path $profilePath -Value "`nSet-Alias address_analyzing_tool `"$scriptPath`" -Scope Global"

Write-Host "✅ Installation completed"

. $profilePath