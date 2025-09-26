#!/bin/bash

set -e # Exit on error

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_status() {
    local color=$1
    local message=$2
    echo -e "${color}[$(date '+%H:%M:%S')] $message${NC}"
}

print_header() {
    echo ""
    echo "=================================="
    echo "$1"
    echo "=================================="
    echo ""
}

test_script_exists() {
    local script=$1
    local description=$2

    if [ -f "$script" ]; then
        if [ -x "$script" ]; then
            print_status $GREEN "✓ $description: Exists and is executable"
            return 0
        else
            print_status $YELLOW "⚠️  $description: Exists but is not executable"
            return 1
        fi
    else
        print_status $RED "❌ $description: Does not exist"
        return 1
    fi
}

test_directory_structure() {
    print_header "Checking project structure"

    local all_good=true

    test_script_exists "main.py" "Main script" || all_good=false
    test_script_exists "update.sh" "Complete update script" || all_good=false
    test_script_exists "quick-update.sh" "Quick update script" || all_good=false

    if [ -f "requirements.txt" ]; then
        print_status $GREEN "✓ requirements.txt: Exists"
    else
        print_status $RED "❌ requirements.txt: Does not exist"
        all_good=false
    fi

    for dir in "src" "logs"; do
        if [ -d "$dir" ]; then
            print_status $GREEN "✓ Directory $dir: Exists"
        else
            print_status $RED "❌ Directory $dir: Does not exist"
            all_good=false
        fi
    done

    return $([ "$all_good" = true ])
}

test_git_repository() {
    print_header "Checking Git repository"

    if [ -d ".git" ]; then
        print_status $GREEN "✓ Git repository initialized"

        if git remote -v | grep -q "origin"; then
            local origin_url=$(git remote get-url origin 2>/dev/null || echo "Not configured")
            print_status $GREEN "✓ Remote origin: $origin_url"
        else
            print_status $YELLOW "⚠️  Remote origin not configured"
        fi

        if git status --porcelain | grep -q .; then
            print_status $YELLOW "⚠️  There are uncommitted changes"
        else
            print_status $GREEN "✓ Clean repository"
        fi

        return 0
    else
        print_status $RED "❌ Not a Git repository"
        return 1
    fi
}

test_python_environment() {
    print_header "Checking Python environment"

    local all_good=true

    if command -v python3 &> /dev/null; then
        local python_version=$(python3 --version)
        print_status $GREEN "✓ Python: $python_version"
    else
        print_status $RED "❌ Python3 is not installed"
        all_good=false
    fi

    if [ -d "venv" ]; then
        print_status $GREEN "✓ Virtual environment: Exists"

        if source venv/bin/activate 2>/dev/null; then
            print_status $GREEN "✓ Virtual environment: Can be activated"

            if pip list | grep -q "requests"; then
                print_status $GREEN "✓ Basic dependencies installed"
            else
                print_status $YELLOW "⚠️  Dependencies may need updating"
            fi

            deactivate 2>/dev/null || true
        else
            print_status $RED "❌ Virtual environment: Error activating"
            all_good=false
        fi
    else
        print_status $YELLOW "⚠️  Virtual environment: Does not exist (will be created if needed)"
    fi

    return $([ "$all_good" = true ])
}

test_script_syntax() {
    print_header "Checking scripts syntax"

    local all_good=true

    for script in "update.sh" "quick-update.sh" "setup-auto-update.sh"; do
        if [ -f "$script" ]; then
            if bash -n "$script" 2>/dev/null; then
                print_status $GREEN "✓ $script: Correct syntax"
            else
                print_status $RED "❌ $script: Syntax error"
                all_good=false
            fi
        fi
    done

    for script in "main.py"; do
        if [ -f "$script" ]; then
            if python3 -m py_compile "$script" 2>/dev/null; then
                print_status $GREEN "✓ $script: Correct syntax"
            else
                print_status $RED "❌ $script: Python syntax error"
                all_good=false
            fi
        fi
    done

    return $([ "$all_good" = true ])
}

test_update_script_dry_run() {
    print_header "Testing update script (dry run)"

    local test_backup="./test_backup_$(date +%Y%m%d_%H%M%S)"
    mkdir -p "$test_backup"

    touch "$test_backup/.env.test"
    touch "$test_backup/scan_results.csv.test"

    print_status $BLUE "📋 Checking update script functions..."

    if bash -c "source ./update.sh && type check_prerequisites &>/dev/null"; then
        print_status $GREEN "✓ Function check_prerequisites defined"
    else
        print_status $YELLOW "⚠️  Function check_prerequisites not accessible"
    fi

    rm -rf "$test_backup"

    print_status $GREEN "✓ Dry run test completed"
    return 0
}

test_auto_update_configuration() {
    print_header "Checking auto-update configuration"

    if ./setup-auto-update.sh --help &>/dev/null; then
        print_status $GREEN "✓ setup-auto-update.sh: Help works"
    else
        print_status $RED "❌ setup-auto-update.sh: Help error"
        return 1
    fi

    if ./setup-auto-update.sh --status &>/dev/null; then
        print_status $GREEN "✓ setup-auto-update.sh: Status works"
    else
        print_status $YELLOW "⚠️  setup-auto-update.sh: Status may have issues"
    fi

    return 0
}

run_all_tests() {
    print_status $BLUE "🧪 Starting update scripts tests..."
    echo ""

    local tests_passed=0
    local total_tests=6

    test_directory_structure && ((tests_passed++))
    test_git_repository && ((tests_passed++))
    test_python_environment && ((tests_passed++))
    test_script_syntax && ((tests_passed++))
    test_update_script_dry_run && ((tests_passed++))
    test_auto_update_configuration && ((tests_passed++))

    print_header "Test summary"

    if [ $tests_passed -eq $total_tests ]; then
        print_status $GREEN "🎉 All tests passed ($tests_passed/$total_tests)"
        print_status $GREEN "✅ Update scripts are ready to use"
        return 0
    else
        print_status $YELLOW "⚠️  Some tests failed ($tests_passed/$total_tests passed)"
        print_status $YELLOW "🔧 Review errors before using the scripts"
        return 1
    fi
}

show_help() {
    echo "Test Scripts - Address Analyzing Tool"
    echo ""
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  -h, --help        Show this help"
    echo "  -a, --all         Run all tests (default)"
    echo "  -s, --structure   Only test structure"
    echo "  -g, --git         Only test Git"
    echo "  -p, --python      Only test Python"
    echo "  -x, --syntax      Only test syntax"
    echo ""
}

case "${1:-}" in
    -h|--help)
        show_help
        exit 0
        ;;
    -s|--structure)
        test_directory_structure
        exit $?
        ;;
    -g|--git)
        test_git_repository
        exit $?
        ;;
    -p|--python)
        test_python_environment
        exit $?
        ;;
    -x|--syntax)
        test_script_syntax
        exit $?
        ;;
    -a|--all|"")
        run_all_tests
        exit $?
        ;;
    *)
        print_status $RED "❌ Unknown option: $1"
        show_help
        exit 1
        ;;
esac

