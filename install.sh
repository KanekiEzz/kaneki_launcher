#!/usr/bin/env bash
# Installs Kaneki Launcher as a real app (app menu + dock) for the current user.
# Usage:  ./install.sh            -> install
#         ./install.sh --uninstall -> remove

set -euo pipefail

APP_ID="kaneki"
INSTALL_DIR="$HOME/.local/share/kaneki-launcher"
ICON_DIR="$HOME/.local/share/icons/hicolor/256x256/apps"
DESKTOP_DIR="$HOME/.local/share/applications"
DESKTOP_FILE="$DESKTOP_DIR/$APP_ID.desktop"
SRC_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

refresh_caches() {
    update-desktop-database "$DESKTOP_DIR" 2>/dev/null || true
    gtk-update-icon-cache -f -t "$HOME/.local/share/icons/hicolor" 2>/dev/null || true
}

if [[ "${1:-}" == "--uninstall" ]]; then
    rm -rf "$INSTALL_DIR"
    rm -f "$DESKTOP_FILE" "$ICON_DIR/$APP_ID.png"
    refresh_caches
    echo "Kaneki Launcher removed."
    exit 0
fi

# tkinter check
if ! python3 -c "import tkinter" 2>/dev/null; then
    echo "tkinter is missing. Install it first:"
    echo "  sudo apt install python3-tk"
    exit 1
fi

mkdir -p "$INSTALL_DIR/icons" "$ICON_DIR" "$DESKTOP_DIR"

# Copy app files
install -m 755 "$SRC_DIR/kaneki_launcher.py" "$INSTALL_DIR/kaneki_launcher.py"
install -m 644 "$SRC_DIR/kaneki.png"         "$INSTALL_DIR/kaneki.png"
install -m 644 "$SRC_DIR/background.png"         "$INSTALL_DIR/background.png"
cp -f "$SRC_DIR"/icons/*.png "$INSTALL_DIR/icons/"
install -m 644 "$SRC_DIR/kaneki.png"         "$ICON_DIR/$APP_ID.png"

# Write the .desktop entry with absolute paths
cat > "$DESKTOP_FILE" <<EOF
[Desktop Entry]
Type=Application
Version=1.0
Name=Kaneki
GenericName=Application Launcher
Comment=My applications launcher
Exec=python3 $INSTALL_DIR/kaneki_launcher.py
Icon=$ICON_DIR/$APP_ID.png
Terminal=false
Categories=Utility;
StartupWMClass=Kaneki
EOF
chmod 644 "$DESKTOP_FILE"

refresh_caches

echo "Done. Search for 'Kaneki' in your app menu."
echo "Then right-click its icon in the dock -> Add to Favorites / Pin to Dock."
