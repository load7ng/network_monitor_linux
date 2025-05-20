#!/usr/bin/env python3
import gi
import os
import sys
import logging
import json
from pathlib import Path
import threading
import speedtest

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_dependencies():
    """Check if all required system dependencies are available"""
    missing_deps = []
    
    # Check for GTK and AppIndicator
    try:
        gi.require_version('Gtk', '3.0')
        gi.require_version('AyatanaAppIndicator3', '0.1')
    except ValueError as e:
        missing_deps.append(str(e))
    
    # Check for required Python packages
    required_packages = {
        'psutil': 'psutil',
        'gi': 'PyGObject',
        'matplotlib': 'matplotlib',
        'pandas': 'pandas',
        'speedtest': 'speedtest-cli'
    }
    
    for module, package in required_packages.items():
        try:
            __import__(module)
        except ImportError:
            missing_deps.append(f"Python package '{package}' is not installed")
    
    if missing_deps:
        error_msg = "Missing dependencies:\n" + "\n".join(missing_deps)
        error_msg += "\n\nPlease run the installation script (install.sh) to install all required dependencies."
        logger.error(error_msg)
        sys.exit(1)

# Check dependencies before proceeding
check_dependencies()

# Configure GTK
gi.require_version('Gtk', '3.0')
gi.require_version('AyatanaAppIndicator3', '0.1')
from gi.repository import Gtk, AyatanaAppIndicator3 as AppIndicator3, GLib
import psutil
import time
from datetime import datetime

# Constants
CONFIG_DIR = os.path.expanduser("~/.config/load7ng-data-tracker")
SESSION_FILE = os.path.join(CONFIG_DIR, "session.json")

class NetworkMonitor:
    def __init__(self):
        logger.info("Initializing NetworkMonitor")
        try:
            # Create config directory if it doesn't exist
            os.makedirs(CONFIG_DIR, exist_ok=True)
            
            # Use a system icon that's guaranteed to exist
            self.indicator = AppIndicator3.Indicator.new(
                "network-monitor",
                "nm-signal-100",  # Using NetworkManager icon which is guaranteed to exist
                AppIndicator3.IndicatorCategory.SYSTEM_SERVICES
            )
            self.indicator.set_status(AppIndicator3.IndicatorStatus.ACTIVE)
            
            # Initialize data storage
            self.load_session()
            self.last_sent = 0
            self.last_received = 0
            
            # Initialize speedtest results
            self.speedtest_results = {
                'download': 0,
                'upload': 0,
                'ping': 0,
                'last_test': None
            }
            self.is_testing = False
            
            # Add a flag to skip the first update
            self.first_update = True
            
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
    
    def load_session(self):
        """Load session data from file or initialize new session"""
        try:
            # Get system boot time with error handling
            try:
                boot_time = datetime.fromtimestamp(psutil.boot_time())
            except Exception as e:
                logger.error(f"Error getting system boot time: {e}")
                boot_time = datetime.now()  # Fallback to current time
            
            if os.path.exists(SESSION_FILE):
                with open(SESSION_FILE, 'r') as f:
                    data = json.load(f)
                    saved_session_start = datetime.fromisoformat(data['session_start'])
                    
                    # If session start is before system boot time or too old (>24h), start a new session
                    if saved_session_start < boot_time or (datetime.now() - saved_session_start).total_seconds() > 86400:
                        logger.info("System reboot detected or session too old, starting new session")
                        self.start_new_session()
                    else:
                        self.session_start = saved_session_start
                        self.session_sent = data['session_sent']
                        self.session_received = data['session_received']
                        logger.info(f"Loaded existing session data from {self.session_start}")
            else:
                self.start_new_session()
                logger.info("Started new session")
        except Exception as e:
            logger.error(f"Error loading session: {e}")
            self.start_new_session()
    
    def start_new_session(self):
        """Initialize a new session with current time"""
        self.session_start = datetime.now()
        self.session_sent = 0
        self.session_received = 0
        self.save_session()
    
    def save_session(self):
        """Save session data to file"""
        try:
            data = {
                'session_start': self.session_start.isoformat(),
                'session_sent': self.session_sent,
                'session_received': self.session_received
            }
            with open(SESSION_FILE, 'w') as f:
                json.dump(data, f)
        except Exception as e:
            logger.error(f"Error saving session: {e}")
        
    def create_menu(self):
        try:
            # Current rate item
            self.rate_item = Gtk.MenuItem(label="Current rate: 0 B/s")
            self.rate_item.show()
            self.menu.append(self.rate_item)
            
            # Session info item (start time)
            self.session_info_item = Gtk.MenuItem(label="Session started: Now")
            self.session_info_item.show()
            self.menu.append(self.session_info_item)
            
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
            
            # Speedtest section
            self.speedtest_item = Gtk.MenuItem(label="Speed Test Results: No Data")
            self.speedtest_item.show()
            self.menu.append(self.speedtest_item)
            
            # Run speedtest button
            self.run_speedtest_item = Gtk.MenuItem(label="Run Speed Test")
            self.run_speedtest_item.connect("activate", self.run_speedtest)
            self.run_speedtest_item.show()
            self.menu.append(self.run_speedtest_item)
            
            # Separator
            separator2 = Gtk.SeparatorMenuItem()
            separator2.show()
            self.menu.append(separator2)
            
            # Reset Session
            reset_item = Gtk.MenuItem(label="Reset Session")
            reset_item.connect("activate", self.reset_session)
            reset_item.show()
            self.menu.append(reset_item)
            
            # Separator
            separator3 = Gtk.SeparatorMenuItem()
            separator3.show()
            self.menu.append(separator3)
            
            # Quit item
            quit_item = Gtk.MenuItem(label="Quit")
            quit_item.connect("activate", self.quit)
            quit_item.show()
            self.menu.append(quit_item)
            logger.info("Menu created successfully")
        except Exception as e:
            logger.error(f"Error creating menu: {e}")
            raise
    
    def reset_session(self, _):
        """Reset the current session"""
        self.start_new_session()
        logger.info("Session reset")
    
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
            
            # Skip the first update to avoid spike
            if self.first_update:
                self.last_sent = current_sent
                self.last_received = current_received
                self.first_update = False
                return True
            
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
            
            # Format session start time
            session_start_str = self.session_start.strftime("%H:%M:%S")
            self.session_info_item.set_label(f"Session started: {session_start_str}")
            
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
            
            # Save session data periodically (every 60 seconds)
            if int(session_duration.total_seconds()) % 60 == 0:
                self.save_session()
            
            return True
        except Exception as e:
            logger.error(f"Error updating stats: {e}")
            return True  # Keep the timer running even if we have an error
    
    def quit(self, _):
        """Save session and quit"""
        logger.info("Quitting application")
        self.save_session()
        Gtk.main_quit()

    def run_speedtest(self, _):
        """Run a speedtest in a separate thread"""
        if self.is_testing:
            logger.info("Speed test already in progress")
            return
        
        self.is_testing = True
        self.run_speedtest_item.set_sensitive(False)
        self.speedtest_item.set_label("Speed Test in progress...")
        
        def speedtest_worker():
            try:
                logger.info("Starting speed test")
                st = speedtest.Speedtest()
                st.get_best_server()
                
                # Test download speed
                download_speed = st.download()
                self.speedtest_results['download'] = download_speed
                
                # Test upload speed
                upload_speed = st.upload()
                self.speedtest_results['upload'] = upload_speed
                
                # Get ping
                self.speedtest_results['ping'] = st.results.ping
                self.speedtest_results['last_test'] = datetime.now()
                
                # Update menu item in main thread
                GLib.idle_add(self.update_speedtest_label)
                logger.info("Speed test completed successfully")
            except Exception as e:
                logger.error(f"Error during speed test: {e}")
                GLib.idle_add(lambda: self.speedtest_item.set_label("Speed Test failed"))
            finally:
                self.is_testing = False
                GLib.idle_add(lambda: self.run_speedtest_item.set_sensitive(True))
        
        # Start speedtest in a separate thread
        thread = threading.Thread(target=speedtest_worker)
        thread.daemon = True
        thread.start()
    
    def update_speedtest_label(self):
        """Update the speedtest menu item with the latest results"""
        if self.speedtest_results['last_test'] is None:
            return
        
        download_speed = self.format_bits_per_second(self.speedtest_results['download'])
        upload_speed = self.format_bits_per_second(self.speedtest_results['upload'])
        ping = self.speedtest_results['ping']
        last_test = self.speedtest_results['last_test'].strftime("%H:%M:%S")
        
        self.speedtest_item.set_label(
            f"Speed Test Results (at {last_test}):\n"
            f"↓ {download_speed} ↑ {upload_speed}\n"
            f"Ping: {ping:.1f} ms"
        )
    
    def format_bits_per_second(self, bits):
        """Format bits per second into human readable format"""
        for unit in ['bps', 'Kbps', 'Mbps', 'Gbps']:
            if bits < 1000:
                return f"{bits:.1f} {unit}"
            bits /= 1000
        return f"{bits:.1f} Tbps"

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