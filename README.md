# Network Traffic Monitor

A Linux-based network traffic monitoring application that displays real-time data flow in the system tray with session-based tracking and network speed testing capabilities.

## Features

- Real-time network traffic monitoring in system tray
- Upload and download speed display
- Session-based data usage tracking
- Integrated network speed testing
  - Download and upload speed measurements
  - Latency (ping) testing
  - Background testing without UI freezing
- Automatic session reset on system restart
- Clean and intuitive GTK-based user interface
- System tray integration with detailed statistics
- Autostart capability
- Easy installation and uninstallation
- **Initial spike fix:** Counters now start cleanly after launch, avoiding a false high value on first start

## Requirements

### System Dependencies
The install script will handle all dependencies automatically. If you need to install manually, use:
```bash
sudo apt-get install build-essential python3-dev pkg-config libcairo2-dev libgirepository1.0-dev libglib2.0-dev gir1.2-gtk-3.0 python3-gi python3-gi-cairo gir1.2-ayatanaappindicator3-0.1 python3-venv python3-pip
```

### Python Dependencies (installed automatically by the script)
- psutil >= 5.9.0
- matplotlib >= 3.7.0
- pandas >= 2.0.0
- speedtest-cli >= 2.1.3
- pytest >= 7.3.1 (for testing)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/load7ng/network-monitor.git
cd network-monitor
```

2. Run the installation script:
```bash
sudo ./install.sh
```

The installer will:
- Install all required system dependencies
- Set up a Python virtual environment
- Install Python packages
- Create necessary desktop entries
- Configure autostart
- Set up proper permissions

## Usage

### Starting the Application
After installation, you can:
1. Run from the application menu: Search for "load7ng's Data Tracker"
2. Run from terminal: `load7ng-data-tracker`
3. The application will start automatically on system boot (can be disabled)

### Features
- System tray icon shows current upload/download speeds (see note below for label visibility)
- Click the icon to view the menu with:
  - Current transfer rates
  - Session start time
  - Total data transferred in session
  - Session duration
  - Network speed test functionality
    - Run speed tests on demand
    - View latest speed test results (download/upload speeds and ping)
    - Tests run in background without affecting application responsiveness
  - Option to reset session
  - Quit option

### Network Speed Testing
The application includes an integrated speed testing feature:
- Access via the system tray menu
- Click "Run Speed Test" to initiate a test
- Tests measure:
  - Download speed
  - Upload speed
  - Network latency (ping)
- Results are displayed in human-readable format
- Testing runs in the background without freezing the UI
- Previous test results remain visible until a new test is run
- Test results include timestamp for reference

### Session Handling
- Sessions automatically reset on system restart
- Manual reset available through the menu
- Session data is preserved between application restarts
- 24-hour maximum session duration

### Uninstallation
To remove the application, you can use either of these commands:
```bash
sudo /opt/load7ng-data-tracker/uninstall.sh
# or (from the repo root)
sudo ./uninstall.sh
```

## AppIndicator Label Visibility (Important Note)
- **On GNOME (default for Ubuntu/Kali):** Only the icon is shown in the top bar; the real-time label is hidden by the desktop environment. This is a GNOME limitation.
- **On XFCE, MATE, or some other desktops:** The label (showing real-time data) is visible next to the icon.
- The app always updates the label, but whether it is visible depends on your desktop environment.
- For full label visibility, consider using XFCE or MATE.

## Troubleshooting
- If you see a spike in the counter at first launch, update to the latest version (this is now fixed).
- If the install script fails, ensure you are running it with `sudo` and your system is up to date.
- If the tray icon appears but no label is visible, see the note above about desktop environment limitations.
- For any missing dependencies, rerun the install script or check the list above.

## Development

### Setting up Development Environment
1. Create a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

### Project Structure
```
network_monitor/
├── src/
│   └── app.py          # Main application code
├── tests/
│   └── test_network_monitor.py
├── data/               # For future data storage
├── requirements.txt    # Python dependencies
├── install.sh         # Installation script
├── uninstall.sh       # Standalone uninstall script
└── load7ng-data-tracker.desktop
```

### Running Tests
```bash
python -m pytest tests/
```

## Contributing
Please read (CONTRIBUTING.md) for details on our code of conduct and the process for submitting pull requests.

## License
This project is licensed under the MIT License - see the (LICENSE) file for details.

## Author
- load7ng 