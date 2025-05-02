#!/usr/bin/env python3
import gi
import os
import sys
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configure GTK
gi.require_version('Gtk', '3.0')
gi.require_version('AppIndicator3', '0.1')
from gi.repository import Gtk, AppIndicator3, GLib
import psutil
import time
from datetime import datetime

class NetworkMonitor:
    def __init__(self):
        logger.info("Initializing NetworkMonitor")
        try:
            # Use a system icon that's guaranteed to exist
            self.indicator = AppIndicator3.Indicator.new(
                "network-monitor",
                "nm-signal-100",  # Using NetworkManager icon which is guaranteed to exist
                AppIndicator3.IndicatorCategory.SYSTEM_SERVICES
            )
            self.indicator.set_status(AppIndicator3.IndicatorStatus.ACTIVE)
            
            # Initialize data storage
            self.session_start = datetime.now()
            self.session_sent = 0
            self.session_received = 0
            self.last_sent = 0
            self.last_received = 0
            
            # Create menu
            self.menu = Gtk.Menu()
            self.create_menu()
            self.indicator.set_menu(self.menu)
            
            # Update every second
            GLib.timeout_add_seconds(1, self.update_stats)
            logger.info("NetworkMonitor initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing NetworkMonitor: {e}")
            sys.exit(1)
        
    def create_menu(self):
        try:
            # Current rate item
            self.rate_item = Gtk.MenuItem(label="Current rate: 0 B/s")
            self.rate_item.show()
            self.menu.append(self.rate_item)
            
            # Session stats item
            self.session_item = Gtk.MenuItem(label="Session total: 0 B")
            self.session_item.show()
            self.menu.append(self.session_item)
            
            # Session time item
            self.time_item = Gtk.MenuItem(label="Session time: 0:00:00")
            self.time_item.show()
            self.menu.append(self.time_item)
            
            # Separator
            separator = Gtk.SeparatorMenuItem()
            separator.show()
            self.menu.append(separator)
            
            # Quit item
            quit_item = Gtk.MenuItem(label="Quit")
            quit_item.connect("activate", self.quit)
            quit_item.show()
            self.menu.append(quit_item)
            logger.info("Menu created successfully")
        except Exception as e:
            logger.error(f"Error creating menu: {e}")
            raise
    
    def format_bytes(self, bytes):
        try:
            for unit in ['B', 'KB', 'MB', 'GB']:
                if bytes < 1024:
                    return f"{bytes:.1f} {unit}"
                bytes /= 1024
            return f"{bytes:.1f} TB"
        except Exception as e:
            logger.error(f"Error formatting bytes: {e}")
            return "0 B"
    
    def format_bytes_short(self, bytes):
        """Format bytes in a shorter format for the indicator label"""
        try:
            for unit in ['B', 'K', 'M', 'G']:
                if bytes < 1024:
                    return f"{bytes:.0f}{unit}"
                bytes /= 1024
            return f"{bytes:.0f}T"
        except Exception as e:
            logger.error(f"Error formatting bytes short: {e}")
            return "0B"
    
    def update_stats(self):
        try:
            net_io = psutil.net_io_counters()
            current_sent = net_io.bytes_sent
            current_received = net_io.bytes_recv
            
            # Calculate rates
            sent_rate = current_sent - self.last_sent
            received_rate = current_received - self.last_received
            total_rate = sent_rate + received_rate
            
            # Update session totals
            self.session_sent += sent_rate
            self.session_received += received_rate
            
            # Update indicator label with current rates
            label = f"↑{self.format_bytes_short(sent_rate)}/s ↓{self.format_bytes_short(received_rate)}/s"
            self.indicator.set_label(label, "")
            
            # Update menu items
            self.rate_item.set_label(
                f"Current rate: ↑{self.format_bytes(sent_rate)}/s ↓{self.format_bytes(received_rate)}/s"
            )
            self.session_item.set_label(
                f"Session total: ↑{self.format_bytes(self.session_sent)} ↓{self.format_bytes(self.session_received)}"
            )
            
            # Update session time
            session_duration = datetime.now() - self.session_start
            hours, remainder = divmod(int(session_duration.total_seconds()), 3600)
            minutes, seconds = divmod(remainder, 60)
            self.time_item.set_label(f"Session time: {hours}:{minutes:02d}:{seconds:02d}")
            
            # Store current values for next update
            self.last_sent = current_sent
            self.last_received = current_received
            
            return True
        except Exception as e:
            logger.error(f"Error updating stats: {e}")
            return True  # Keep the timer running even if we have an error
    
    def quit(self, _):
        logger.info("Quitting application")
        Gtk.main_quit()

def main():
    try:
        logger.info("Starting NetworkMonitor")
        app = NetworkMonitor()
        Gtk.main()
    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt")
        Gtk.main_quit()
    except Exception as e:
        logger.error(f"Unhandled error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()