#!/usr/bin/env bash

# Resolve the absolute path to this script immediately
SCRIPT_PATH="$(readlink -f "$0")"

# 1. If not running inside the new spawned terminal window, launch a new terminal
if [ "$1" != "--child" ]; then
    # Create a unique lockfile to track when the child window finishes
    LOCK_FILE="/tmp/boopi_installer_$$.lock"
    touch "$LOCK_FILE"

    # Launch terminal emulator with the lockfile path passed as parameter 3
    if [ -n "$TERMINAL" ] && command -v "$TERMINAL" &> /dev/null; then
        "$TERMINAL" -e bash "$SCRIPT_PATH" --child "$SCRIPT_PATH" "$LOCK_FILE"
    elif command -v foot &> /dev/null; then
        foot bash "$SCRIPT_PATH" --child "$SCRIPT_PATH" "$LOCK_FILE"
    elif command -v kitty &> /dev/null; then
        kitty bash "$SCRIPT_PATH" --child "$SCRIPT_PATH" "$LOCK_FILE"
    elif command -v alacritty &> /dev/null; then
        alacritty -e bash "$SCRIPT_PATH" --child "$SCRIPT_PATH" "$LOCK_FILE"
    elif command -v gnome-terminal &> /dev/null; then
        gnome-terminal -- bash "$SCRIPT_PATH" --child "$SCRIPT_PATH" "$LOCK_FILE"
    elif command -v konsole &> /dev/null; then
        konsole -e bash "$SCRIPT_PATH" --child "$SCRIPT_PATH" "$LOCK_FILE"
    elif command -v xfce4-terminal &> /dev/null; then
        xfce4-terminal -e "bash \"$SCRIPT_PATH\" --child \"$SCRIPT_PATH\" \"$LOCK_FILE\""
    elif command -v xterm &> /dev/null; then
        xterm -e bash "$SCRIPT_PATH" --child "$SCRIPT_PATH" "$LOCK_FILE"
    elif command -v x-terminal-emulator &> /dev/null; then
        x-terminal-emulator -e bash "$SCRIPT_PATH" --child "$SCRIPT_PATH" "$LOCK_FILE"
    else
        echo "No supported external terminal emulator found. Running in current shell..."
        bash "$SCRIPT_PATH" --child "$SCRIPT_PATH" "$LOCK_FILE"
    fi

    # BLOCK HERE: Pause the original terminal until the lock file disappears
    while [ -f "$LOCK_FILE" ]; do
        sleep 0.2
    done

    # ==============================================================================
    # --- Parent Process Resumes Here (Strictly in the ORIGINAL terminal) ---
    # ==============================================================================
    echo ""
    echo "Всем приветы чизеты!"
    echo "Скрипт короче скачал ГОЛЫЙ (воу) репозиторий, и сделал так чтобы можно было запускать main.py"
    echo ""

    # Launch main.py in background from original terminal
    if [ -f "./BoopiCursorConverter/main.py" ]; then
        ./BoopiCursorConverter/main.py >/dev/null 2>&1 &
        disown 2>/dev/null || true
    fi

    echo "Ну все, чтобы запустить, входишь в папку BoopiCursorConverter и запускаешь main.py"
    echo "Удачи!"
    echo ""

    exit 0
fi

# Store parameters passed from parent
TARGET_SCRIPT_FILE="$2"
LOCK_FILE="$3"

# Capture directory where script lives BEFORE doing anything else
SCRIPT_DIR="$(cd "$(dirname "$TARGET_SCRIPT_FILE")" && pwd)"

# Cleanup lock file automatically when this child terminal closes or crashes
trap 'rm -f "$LOCK_FILE"' EXIT

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

# Resolve absolute path to the main.py script
MAIN_PY_PATH="$SCRIPT_DIR/$TARGET_DIR/main.py"

# Make main.py executable inside the cloned directory if it exists
if [ -f "$MAIN_PY_PATH" ]; then
    chmod u+x "$MAIN_PY_PATH"
    echo "Set executable permission on $MAIN_PY_PATH"
else
    echo "Warning: $MAIN_PY_PATH not found."
fi

echo ""
echo "=========================================="
echo "         2. Checking Dependencies         "
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

echo "=========================================="
echo "     3. Creating .desktop Launcher        "
echo "=========================================="

DESKTOP_DIR="$HOME/.local/share/applications"
DESKTOP_FILE="$DESKTOP_DIR/BoopiCursorConverter.desktop"

mkdir -p "$DESKTOP_DIR"

cat <<EOF > "$DESKTOP_FILE"
[Desktop Entry]
Version=67.69
Type=Application
Name=Boopi Cursor Converter
Comment=Cheese Cheese Cheese (сыр то есть)
Exec=python3 "$MAIN_PY_PATH"
Path=$SCRIPT_DIR/$TARGET_DIR
Terminal=false
Categories=Utility;Development;
EOF

chmod +x "$DESKTOP_FILE"
echo "[OK] Created launcher at $DESKTOP_FILE"

# Refresh desktop application database if utility exists
if command -v update-desktop-database &> /dev/null; then
    update-desktop-database "$DESKTOP_DIR" &> /dev/null
fi

echo ""

# Wait for user input before closing child window
read -p "Press [Enter] to exit..."
