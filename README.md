# Network Traffic Monitor

A Linux-based network traffic monitoring application that displays real-time data flow in the system tray with session-based tracking.

## Features

- Real-time network traffic monitoring in system tray
- Upload and download speed display
- Session-based data usage tracking
- Automatic session reset on system restart
- Clean and intuitive GTK-based user interface
- System tray integration with detailed statistics
- Autostart capability
- Easy installation and uninstallation

## Requirements

### System Dependencies
```bash
sudo apt-get install python3-venv python3-gi python3-gi-cairo gir1.2-gtk-3.0 gir1.2-appindicator3-0.1
```

### Python Dependencies
- psutil >= 5.9.0
- PyGObject >= 3.42.0
- matplotlib >= 3.7.0
- pandas >= 2.0.0
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
- Install required system dependencies
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
- System tray icon shows current upload/download speeds
- Click the icon to view the menu with:
  - Current transfer rates
  - Session start time
  - Total data transferred in session
  - Session duration
  - Option to reset session
  - Quit option

### Session Handling
- Sessions automatically reset on system restart
- Manual reset available through the menu
- Session data is preserved between application restarts
- 24-hour maximum session duration

### Uninstallation
To remove the application:
```bash
sudo /opt/load7ng-data-tracker/uninstall.sh
```

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
├── uninstall.sh       # Created during installation
└── load7ng-data-tracker.desktop
```

### Running Tests
```bash
python -m pytest tests/
```

## Contributing
Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct and the process for submitting pull requests.

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Author
- load7ng 