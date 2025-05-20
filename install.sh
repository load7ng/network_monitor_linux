#!/bin/bash

# Exit on error
set -e

echo "Installing load7ng's Data Tracker..."

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check if a package is installed
package_installed() {
    dpkg -l "$1" | grep -q "^ii" 2>/dev/null
}

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "Please run as root (use sudo)"
    exit 1
fi

# Get the username of the user who invoked sudo
SUDO_USER="${SUDO_USER:-$USER}"
SUDO_HOME=$(getent passwd "$SUDO_USER" | cut -d: -f6)

# Get the script's directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# Check and install system dependencies
echo "Checking system dependencies..."
SYSTEM_DEPS=(
    "python3-venv"
    "python3-gi"
    "python3-gi-cairo"
    "gir1.2-gtk-3.0"
    "gir1.2-appindicator3-0.1"
    "python3-pip"
)

# Update package list
apt-get update

# Install missing dependencies
for dep in "${SYSTEM_DEPS[@]}"; do
    if ! package_installed "$dep"; then
        echo "Installing $dep..."
        apt-get install -y "$dep"
    else
        echo "$dep is already installed"
    fi
done

# Create installation directory
INSTALL_DIR="/opt/load7ng-data-tracker"
mkdir -p "$INSTALL_DIR"

# Create virtual environment
echo "Setting up Python environment..."
python3 -m venv "$INSTALL_DIR/venv"
source "$INSTALL_DIR/venv/bin/activate"

# Upgrade pip
python3 -m pip install --upgrade pip

# Install Python dependencies
echo "Installing Python dependencies..."
pip install -r "$SCRIPT_DIR/requirements.txt"

# Copy application files
echo "Installing application files..."
cp -r "$SCRIPT_DIR/src" "$INSTALL_DIR/"
chmod +x "$INSTALL_DIR/src/app.py"

# Create launcher script
LAUNCHER="/usr/local/bin/load7ng-data-tracker"
cat > "$LAUNCHER" << 'EOF'
#!/bin/bash
source /opt/load7ng-data-tracker/venv/bin/activate
exec /opt/load7ng-data-tracker/src/app.py "$@"
EOF
chmod +x "$LAUNCHER"

# Install desktop entry
cp "$SCRIPT_DIR/load7ng-data-tracker.desktop" /usr/share/applications/

# Create symbolic link for GTK bindings
ln -sf /usr/lib/python3/dist-packages/gi "$INSTALL_DIR/venv/lib/python3*/site-packages/"

# Add system-wide autostart entry
echo "Setting up system-wide autostart..."
mkdir -p /etc/xdg/autostart
cp "$SCRIPT_DIR/load7ng-data-tracker.desktop" /etc/xdg/autostart/

# Set up autostart for the installing user
echo "Setting up user autostart..."
USER_AUTOSTART_DIR="$SUDO_HOME/.config/autostart"
mkdir -p "$USER_AUTOSTART_DIR"
cp "$SCRIPT_DIR/load7ng-data-tracker.desktop" "$USER_AUTOSTART_DIR/"
chown -R "$SUDO_USER:$SUDO_USER" "$USER_AUTOSTART_DIR"

# Create uninstall script
cat > "$INSTALL_DIR/uninstall.sh" << 'EOF'
#!/bin/bash
if [ "$EUID" -ne 0 ]; then
    echo "Please run as root (use sudo)"
    exit 1
fi

echo "Uninstalling load7ng's Data Tracker..."

# Remove system-wide files
rm -f /usr/local/bin/load7ng-data-tracker
rm -f /usr/share/applications/load7ng-data-tracker.desktop
rm -f /etc/xdg/autostart/load7ng-data-tracker.desktop
rm -rf /opt/load7ng-data-tracker

# Remove autostart entries for all users
for USER_HOME in /home/*; do
    if [ -d "$USER_HOME" ]; then
        USER_AUTOSTART="$USER_HOME/.config/autostart/load7ng-data-tracker.desktop"
        if [ -f "$USER_AUTOSTART" ]; then
            rm -f "$USER_AUTOSTART"
        fi
    fi
done

echo "Uninstallation complete!"
EOF
chmod +x "$INSTALL_DIR/uninstall.sh"

echo "Installation complete!"
echo "The application has been installed and autostart is enabled by default."
echo "You can toggle autostart from the application menu."
echo "To start the application now, run: load7ng-data-tracker"
echo "To uninstall, run: sudo /opt/load7ng-data-tracker/uninstall.sh" 