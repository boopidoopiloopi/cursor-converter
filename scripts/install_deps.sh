#!/usr/bin/env bash
set -e

INSTALL_GTK3_PICKER="$1"

echo "[Step 0] Checking Arch Linux Dependencies..."

if ! command -v yay &> /dev/null; then
    echo "Error: 'yay' (AUR helper) is not installed."
    exit 1
fi

NEEDED_AUR=()
for pkg in win2xcur pyside6; do
    if ! pacman -Q "$pkg" &> /dev/null; then
        NEEDED_AUR+=("$pkg")
    fi
done

if [ ${#NEEDED_AUR[@]} -gt 0 ]; then
    echo "Installing missing AUR packages: ${NEEDED_AUR[*]}..."
    yay -S --needed --noconfirm "${NEEDED_AUR[@]}"
else
    echo "All required AUR packages are present."
fi

PACMAN_DEPS=("bc" "imagemagick" "xorg-xcursorgen" "python-pillow" "gtk3" "git" "python-gobject")

echo "Installing pacman dependencies using Polkit (pkexec)..."
pkexec pacman -S --needed --noconfirm "${PACMAN_DEPS[@]}"

echo "Dependency check complete!"
