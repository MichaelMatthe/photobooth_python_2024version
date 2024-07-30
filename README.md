# Photobooth Python 2024 Version

## Requirements

Tested on Ubuntu 24.04 with Python 3.12.3.

Install gphoto2

```
sudo apt install gphoto2
```

Clone project.

Create Python virtual environment.

```
sudo apt install python3-venv
cd photobooth_python_2024version
python3 -m venv venv
```

Activate virtual environment and install required packages:

```
source venv/bin/activate
pip install -r requirements.txt
```

Install PyQt5 requirements:

```
sudo apt install libxcb-xinerama0
sudo apt install libxkbcommon-x11-0
```
s
## Hardware:

Connect camera and printer, set the correct printer as the default printer. (Settings > Printers > ... "Use Printer by Default")

## Start application

```
python3 main.py
```