
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
