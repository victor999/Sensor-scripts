# Sensor-scripts

Scripts for scanning BLE sensors on Raspberry Pi and write data to different systems

Bluetooth Sensors can be bought at https://www.tindie.com/products/11856/

Currently supported

- mySQL DB

- thinspeak.com

- AT&T m2x

- io.adafruit

<br>
<br>

sudo apt-get install python-pip libglib2.0-dev git apache2 mysql-server

sudo pip install bluepy


<br>
<br>
- Thingspeak

<br>
<br>
sudo pip install thingspeak

Create file /home/pi/thing.sp with following content
<br>
<br>
MAC ADDRESS

CHANNEL_ID

WRITE_API

<br>
<br>
- mySQL

<br>
<br>
sudo pip install MySQL-python

Create file /home/pi/my.cnf with following content
<br>
<br>
[client]

host = localhost

user = db_user

database = your_db

password = YourPassword

<br>
<br>
- AT&T m2x

<br>
<br>
sudo pip install m2x

Create a file /home/pi/mx.2 wit the following content
<br>
<br>
mac_address

m2x_key

m2x_device_id

stream1_id

stream2_id

<br>
<br>
- Adafruit

<br>
<br>
sudo pip install adafruit-io

Create file /home/pi/ada.fr with following content
<br>
<br>
MAC_ADDRESS

AIO_KEY
