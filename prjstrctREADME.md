# Network Traffic Monitor

A Linux-based network traffic monitoring application that displays real-time data flow in the system tray and provides detailed statistics.

## Features

- Real-time network traffic display in the system tray
- Upload and download speed monitoring
- Session-based data usage tracking
- Clean and intuitive user interface
- System tray integration
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
3. Enable/disable autostart from the application menu

### Features
- Click the system tray icon to view the menu
- Monitor current upload/download speeds
- Track total data usage for the session
- View session duration
- Toggle autostart functionality

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