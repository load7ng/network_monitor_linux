#!/bin/bash

# Exit on error
set -e

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "Please run as root (use sudo)"
    exit 1
fi

echo "Uninstalling load7ng's Data Tracker..."

# Remove system-wide files
echo "Removing system files..."
rm -f /usr/local/bin/load7ng-data-tracker
rm -f /usr/share/applications/load7ng-data-tracker.desktop
rm -f /etc/xdg/autostart/load7ng-data-tracker.desktop

# Remove the main installation directory
echo "Removing installation directory..."
rm -rf /opt/load7ng-data-tracker

# Remove autostart entries for all users
echo "Removing autostart entries..."
for USER_HOME in /home/*; do
    if [ -d "$USER_HOME" ]; then
        USER_AUTOSTART="$USER_HOME/.config/autostart/load7ng-data-tracker.desktop"
        if [ -f "$USER_AUTOSTART" ]; then
            rm -f "$USER_AUTOSTART"
        fi
    fi
done

# Remove user config directory
echo "Removing user configuration..."
for USER_HOME in /home/*; do
    if [ -d "$USER_HOME" ]; then
        USER_CONFIG="$USER_HOME/.config/load7ng-data-tracker"
        if [ -d "$USER_CONFIG" ]; then
            rm -rf "$USER_CONFIG"
        fi
    fi
done

echo "Uninstallation complete!" 