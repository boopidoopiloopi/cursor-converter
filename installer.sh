#!/usr/bin/env bash

# Get full absolute path of this script
SCRIPT_PATH="$(readlink -f "$0")"

# 1. If not running inside the new spawned terminal window, launch a new terminal
if [ "$1" != "--child" ]; then
    if command -v gnome-terminal &> /dev/null; then
        gnome-terminal -- bash "$SCRIPT_PATH" --child
    elif command -v konsole &> /dev/null; then
        konsole -e bash "$SCRIPT_PATH" --child
    elif command -v xfce4-terminal &> /dev/null; then
        xfce4-terminal -e "bash \"$SCRIPT_PATH\" --child"
    elif command -v kitty &> /dev/null; then
        kitty bash "$SCRIPT_PATH" --child
    elif command -v alacritty &> /dev/null; then
        alacritty -e bash "$SCRIPT_PATH" --child
    elif command -v xterm &> /dev/null; then
        xterm -e bash "$SCRIPT_PATH" --child
    elif command -v x-terminal-emulator &> /dev/null; then
        x-terminal-emulator -e bash "$SCRIPT_PATH" --child
    else
        echo "No supported external terminal emulator found. Running in current shell..."
        bash "$SCRIPT_PATH" --child
    fi
    exit 0
fi

# ==============================================================================
# --- Code below runs inside the newly opened terminal window ---
# ==============================================================================

REPO_URL="https://github.com/boopidoopiloopi/cursor-converter.git"
TARGET_DIR="BoopiCursorConverter"

echo "=========================================="
echo "          1. Cloning Repository           "
echo "=========================================="

if [ -d "$TARGET_DIR" ]; then
    echo "Directory '$TARGET_DIR' already exists. Skipping clone."
else
    git clone "$REPO_URL" "$TARGET_DIR"
fi

# Make main.py executable inside the cloned directory if it exists
if [ -f "./$TARGET_DIR/main.py" ]; then
    chmod u+x "./$TARGET_DIR/main.py"
    echo "Set executable permission on ./$TARGET_DIR/main.py"
else
    echo "Warning: ./$TARGET_DIR/main.py not found."
fi

echo ""
echo "=========================================="
echo "        2. Checking Dependencies          "
echo "=========================================="

MISSING_DEPS=0

# Check Git
if command -v git &> /dev/null; then
    echo "[OK] git"
else
    echo "[MISSING] git"
    MISSING_DEPS=1
fi

# Check Python 3
if ! command -v python3 &> /dev/null; then
    echo "[MISSING] python3 (Required for python-pillow and python-gobject)"
    MISSING_DEPS=1
else
    # Check Python Pillow
    if python3 -c "import PIL" &> /dev/null; then
        echo "[OK] python-pillow (Pillow)"
    else
        echo "[MISSING] python-pillow"
        MISSING_DEPS=1
    fi

    # Check PyGObject & GTK3 integration
    if python3 -c "import gi; gi.require_version('Gtk', '3.0'); from gi.repository import Gtk" &> /dev/null; then
        echo "[OK] gtk3 & python-gobject"
    else
        echo "[MISSING] gtk3 and/or python-gobject"
        MISSING_DEPS=1
    fi
fi

echo ""
echo "------------------------------------------"
if [ $MISSING_DEPS -eq 0 ]; then
    echo "SUCCESS: All dependencies are satisfied!"
else
    echo "WARNING: Some dependencies are missing."
    echo "Please install them using your Linux package manager."
fi
echo "------------------------------------------"
echo ""

# Wait for user input before closing
read -p "Press [Enter] to exit..."
