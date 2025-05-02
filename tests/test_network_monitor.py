import unittest
from unittest.mock import patch, MagicMock
import sys
import os
from datetime import datetime, timedelta

# Add the src directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from app import NetworkMonitor

class TestNetworkMonitor(unittest.TestCase):
    @patch('gi.repository.AppIndicator3')
    @patch('gi.repository.Gtk')
    def setUp(self, mock_gtk, mock_indicator):
        self.monitor = NetworkMonitor()
    
    def test_format_bytes(self):
        test_cases = [
            (0, "0.0 B"),
            (1023, "1023.0 B"),
            (1024, "1.0 KB"),
            (1024*1024, "1.0 MB"),
            (1024*1024*1024, "1.0 GB"),
        ]
        for input_bytes, expected in test_cases:
            with self.subTest(input_bytes=input_bytes):
                self.assertEqual(self.monitor.format_bytes(input_bytes), expected)
    
    def test_format_bytes_short(self):
        test_cases = [
            (0, "0B"),
            (1023, "1023B"),
            (1024, "1K"),
            (1024*1024, "1M"),
            (1024*1024*1024, "1G"),
        ]
        for input_bytes, expected in test_cases:
            with self.subTest(input_bytes=input_bytes):
                self.assertEqual(self.monitor.format_bytes_short(input_bytes), expected)
    
    @patch('psutil.net_io_counters')
    def test_update_stats(self, mock_net_io):
        # Mock network IO counters
        mock_net_io.return_value = MagicMock(
            bytes_sent=1024*10,
            bytes_recv=1024*20
        )
        
        # Set initial values
        self.monitor.last_sent = 1024*5
        self.monitor.last_received = 1024*10
        
        # Call update_stats
        self.monitor.update_stats()
        
        # Check if values were updated correctly
        self.assertEqual(self.monitor.session_sent, 1024*5)  # 10K - 5K
        self.assertEqual(self.monitor.session_received, 1024*10)  # 20K - 10K

if __name__ == '__main__':
    unittest.main() 