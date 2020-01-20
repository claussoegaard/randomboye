# Randomboye
Runs on a Raspberry Pi Zero hooked up to two push buttons and a 2x16 LCD, and prints a random record from a Discogs collection.

All these notes are basically just for myself year(s) from now when

## Run
See `main.py` for details about args and how to run.

## Setup
Haven't found a pipenv/venv/etc. solution that really clicks so not attempting any requirements.txt stuff, so just install whatever dependencies it complains about needing.. `discogs_client` and some of the GPIO-related libraries for sure, don't remember what else. Make sure to install everything globally as the service itself will run as root (even though the launcher script is executed as `pi` user).

You have to enable Remote GPIO in `raspi-config` under "Interfaces".

You have to at least install these libraries: `sudo apt install python3-gpiozero python3-pigpio` and start the pigpiod service:
`sudo systemctl enable pigpiod`
`sudo systemctl start pigpiod`
 
### Setting Up Discogs Collection
Setup an API token.

### Wiring

### Run As Service
To run as a service you'll need to do a few things (this is just the solution I'm doing).

**Create service**

Run `sudo nano /etc/systemd/system/randomboye.service` and paste this content:
```
[Unit]
Description=Random Boye Python Service
After=multi-user.target

[Service]
Type=idle
User=pi
ExecStart=sh /home/pi/dev/randomboye/randomboye_launcher.sh

[Install]
WantedBy=multi-user.target
```
Set permissions: `sudo chmod 744 /etc/systemd/system/randomboye.service`
Refresh systemctl daemon: `sudo systemctl daemon-reload`
Enable the service: `sudo systemctl enable randomboye.service`
Edit the service to add an environment variable with the Discogs API auth token. Run this: `sudo systemctl edit randomboye.service` and edit the override file like so:
```
[Service]
Environment="DISCOGS_TOKEN=bblablablba"
```
Alternatively just hardcode the auth-token into the `-a` arg in the launcher script.
To test/start the service: `sudo systemctl start randomboye.service`. This will start on all subsequent reboots. 

**Troubleshooting Tips**

Sometimes permissions can be finicky when things run as different users and root and whatnot so just some helpful commands in case you're troubleshooting:
`sudo systemctl status randomboye.service`: Run this after `start` to see how the service is doing. It'll tell you which exceptions the script threw, if any.
`sudo systemctl disable randomboye.service` to make it not auto-start on reboot. 
Most likely any issues will be permissions related. 
Remember to run `sudo systemctl stop randomboye.service` before manually starting the service if you're debugging something. Alternatively you can find the python process running by `ps -fA | grep python`, fetch the process ID and do `kill <pid>`.
