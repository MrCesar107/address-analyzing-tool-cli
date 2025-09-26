#!/bin/bash

set -e # Exit on error

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

REPO_URL="https://github.com/MrCesar107/address-analyzing-tool-cli.git"
BACKUP_DIR="./backup_$(date +%Y%m%d_%H%M%S)"
LOG_FILE="./logs/update_$(date +%Y%m%d_%H%M%S).log"

log() {
    local message="$1"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo "[$timestamp] $message" | tee -a "$LOG_FILE"
}

print_status() {
    local color=$1
    local message=$2
    echo -e "${color}[$(date '+%H:%M:%S')] $message${NC}"
    log "$message"
}

create_backup() {
    print_status $YELLOW "Creating backup of critical files..."

    mkdir -p "$BACKUP_DIR"

    if [ -f ".env" ]; then
        cp ".env" "$BACKUP_DIR/.env.backup"
        print_status $GREEN "✓ .env backup created"
    fi

    if [ -f "scan_results.csv" ]; then
        cp "scan_results.csv" "$BACKUP_DIR/scan_results.csv.backup"
        print_status $GREEN "✓ scan_results.csv backup created"
    fi

    if [ -d "logs" ]; then
        cp -r "logs" "$BACKUP_DIR/logs_backup"
        print_status $GREEN "✓ logs backup created"
    fi
}

restore_backup() {
    print_status $YELLOW "Restoring critical files from backup..."

    if [ -f "$BACKUP_DIR/.env.backup" ]; then
        cp "$BACKUP_DIR/.env.backup" ".env"
        print_status $GREEN "✓ .env restored"
    fi

    if [ -f "$BACKUP_DIR/scan_results.csv.backup" ]; then
        cp "$BACKUP_DIR/scan_results.csv.backup" "scan_results.csv"
        print_status $GREEN "✓ scan_results.csv restored"
    fi

    if [ -d "$BACKUP_DIR/logs_backup" ]; then
        cp -r "$BACKUP_DIR/logs_backup/"* "logs/" 2>/dev/null || true
        print_status $GREEN "✓ logs restored"
    fi
}

cleanup_backup() {
    if [ -d "$BACKUP_DIR" ]; then
        rm -rf "$BACKUP_DIR"
        print_status $GREEN "✓ Temporary backup cleaned"
    fi
}

rollback() {
    print_status $RED "❌ Error detected. Starting rollback..."

    restore_backup

    git reset --hard HEAD~1 2>/dev/null || true

    print_status $RED "❌ Rollback completed. Check logs for more details."
    exit 1
}

check_prerequisites() {
    print_status $BLUE "Checking prerequisites..."

    if [ ! -d ".git" ]; then
        print_status $RED "❌ Git repository not found. Run from project directory."
        exit 1
    fi

    if ! command -v git &> /dev/null; then
        print_status $RED "❌ Git is not installed"
        exit 1
    fi

    if ! command -v python3 &> /dev/null; then
        print_status $RED "❌ Python3 is not installed"
        exit 1
    fi

    print_status $GREEN "✓ Prerequisites verified"
}

update_code() {
    print_status $BLUE "Updating code from GitHub..."

    CURRENT_COMMIT=$(git rev-parse HEAD)
    log "Current commit: $CURRENT_COMMIT"

    if ! git diff-index --quiet HEAD --; then
        git stash push -m "Auto-stash before update $(date)"
        print_status $YELLOW "⚠️  Local changes saved in stash"
    fi

    git fetch origin main
    git pull origin main

    print_status $GREEN "✓ Code updated from GitHub"
}

update_dependencies() {
    print_status $BLUE "Checking and updating dependencies..."

    if [ -d "venv" ]; then
        source venv/bin/activate
        print_status $GREEN "✓ Virtual environment activated"
    else
        print_status $YELLOW "⚠️  Virtual environment not found. Using system Python"
    fi

    python3 -m pip install --upgrade pip

    if [ -f "requirements.txt" ]; then
        pip install -r requirements.txt --upgrade
        print_status $GREEN "✓ Dependencies updated"
    else
        print_status $YELLOW "⚠️  requirements.txt not found"
    fi
}

verify_installation() {
    print_status $BLUE "Verifying installation..."

    if [ -f "main.py" ]; then
        python3 -m py_compile main.py
        print_status $GREEN "✓ main.py compiles correctly"
    else
        print_status $RED "❌ main.py not found"
        return 1
    fi

    python3 -c "
import sys
sys.path.insert(0, '.')
try:
    from src.scanners.hybrid_analysis import HybridAnalysisScanner
    from src.scanners.recorded_future import RecordedFutureScanner
    from src.config.settings import settings
    print('✓ Critical imports verified')
except ImportError as e:
    print(f'❌ Import error: {e}')
    sys.exit(1)
" || return 1

    print_status $GREEN "✓ Installation verified correctly"
}

main() {
    print_status $BLUE "🚀 Starting Address Analyzing Tool update..."

    mkdir -p logs

    trap rollback ERR

    check_prerequisites
    create_backup
    update_code
    update_dependencies
    restore_backup
    verify_installation

    cleanup_backup

    print_status $GREEN "🎉 Update completed successfully!"
    print_status $BLUE "📝 Log saved in: $LOG_FILE"

    if command -v git &> /dev/null; then
        NEW_COMMIT=$(git rev-parse HEAD)
        print_status $BLUE "📌 Current commit: $NEW_COMMIT"
        print_status $BLUE "📝 Latest changes:"
        git log --oneline -5
    fi
}

show_help() {
    echo "Address Analyzing Tool - Update Script"
    echo ""
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  -h, --help     Show this help"
    echo "  -f, --force    Force update (overwrites local changes)"
    echo "  -b, --backup   Only create backup without updating"
    echo ""
    echo "Examples:"
    echo "  $0                    # Normal update"
    echo "  $0 --force           # Force update"
    echo "  $0 --backup          # Backup only"
}

FORCE_UPDATE=false
BACKUP_ONLY=false

while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            show_help
            exit 0
            ;;
        -f|--force)
            FORCE_UPDATE=true
            shift
            ;;
        -b|--backup)
            BACKUP_ONLY=true
            shift
            ;;
        *)
            print_status $RED "❌ Unknown option: $1"
            show_help
            exit 1
            ;;
    esac
done

if [ "$BACKUP_ONLY" = true ]; then
    print_status $BLUE "🔄 Creating backup only..."
    mkdir -p logs
    create_backup
    print_status $GREEN "✓ Backup created in: $BACKUP_DIR"
else
    main
fi

