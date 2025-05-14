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
    
    def test_format_bits_per_second(self):
        test_cases = [
            (0, "0.0 bps"),
            (999, "999.0 bps"),
            (1000, "1.0 Kbps"),
            (1000*1000, "1.0 Mbps"),
            (1000*1000*1000, "1.0 Gbps"),
        ]
        for input_bits, expected in test_cases:
            with self.subTest(input_bits=input_bits):
                self.assertEqual(self.monitor.format_bits_per_second(input_bits), expected)
    
    @patch('speedtest.Speedtest')
    def test_speedtest_functionality(self, mock_speedtest):
        # Mock speedtest instance
        mock_st = MagicMock()
        mock_st.download.return_value = 50_000_000  # 50 Mbps
        mock_st.upload.return_value = 20_000_000    # 20 Mbps
        mock_st.results.ping = 15.5                 # 15.5 ms
        mock_speedtest.return_value = mock_st
        
        # Verify initial state
        self.assertFalse(self.monitor.is_testing)
        self.assertIsNone(self.monitor.speedtest_results['last_test'])
        
        # Run speedtest
        self.monitor.run_speedtest(None)
        
        # Verify speedtest was initiated
        self.assertTrue(self.monitor.is_testing)
        
        # Mock the completion of speedtest
        mock_st.get_best_server.assert_called_once()
        mock_st.download.assert_called_once()
        mock_st.upload.assert_called_once()
    
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