# phuey
A python Phillips Hue animation framework. Create and run pre-built animations, and easily script them into other routines.

## Install
```console
git clone git@github.com:politeauthority/phuey.git
cd phuey
pip3 install -r requirements.txt
python3 setup.py build
sudo python3 setup.py install
```
Then setup the config in `~/.phuey/config.json` with your bridge IP and light ids, if you don't know the light ids you want to use yet you can run `phuey --list-lights`
```json
{
    "bridge_ip": "192.168.50.220",
    "light_ids": [23, 26, 22, 11, 25, 24, 12]
}
```
