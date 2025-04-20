# Worker Monitor

A computer vision-based system to track employee activity using YOLO object detection. Designed for environments with fixed cameras and designated workstation zones.

## Overview

This Python script identifies whether a person is:

- **WORKING**: Inside a predefined workstation rectangle.  
- **IDLE**: Outside the workstation area.

Useful for automating productivity monitoring in workplaces with fixed desks or stations.

## Files

- `main.py` — Main Python script that runs the worker monitoring logic.  
- *(Optional)* systemd service file — For running the script as a background service on Linux.

## Installation

```bash
# Install dependencies
pip install -r requirements.txt
```

## Running the Script

```bash
python main.py
```

Make sure your YOLO model weights and camera/video source are properly set up inside `main.py`.

## Running as a Linux Service (Optional)

Create a service file at:

```bash
sudo nano /etc/systemd/system/worker-monitor.service
```

Paste this into the file:

```ini
[Unit]
Description=Worker Monitor Service
After=network.target

[Service]
Type=simple
User=youruser
WorkingDirectory=/path/to/worker_monitor
ExecStart=/usr/bin/python3 /path/to/your/project/main.py
Restart=always
RestartSec=5
Environment=PYTHONUNBUFFERED=1

[Install]
WantedBy=multi-user.target
```

Enable and start the service:

```bash
sudo systemctl daemon-reload
sudo systemctl enable worker-monitor
sudo systemctl start worker-monitor
```

View logs in real time:

```bash
journalctl -u worker-monitor -f
```
