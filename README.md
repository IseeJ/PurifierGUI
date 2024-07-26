# TempGUI
GUI for temperature and humidity monitoring in LAr purifier (for Temperature logger and EZO Atlas sensors)

*Updated on 7/18/24: Use the **GUIfinal.py** with **TabWindow.py***

*Updated on 7/22/24: Converting gauge pressure to absolute pressure, Configure default unit to be psi and plot the conversion to Torr, calibrate the low point psi*

On the PC:
1. click on the taskbar 'Search'
2. Open Anaconda Navigator
3. Open Jupyter notebook from Anaconda Navigator
4. Open powershell from Anaconda Navigator
5. Type in the command to get into the directory where the python code is

```
cd .\Desktop\TempGUI\GUIfinal\
```
6. Run the python code for GUI
   
```
python .\GUIfinal.py
```
![Fig1](https://github.com/IseeJ/TempGUI/blob/main/images/Screenshot1.png?raw=true)
![Fig2](https://github.com/IseeJ/TempGUI/blob/main/images/Screenshot7.png?raw=true)

# Required Packages
already installed, if error messages pop up, pip install again
```
pip install pyqt5
pip install pyqt5-tools
pip install pyqtgraph
pip install pyserial
```
## Connecting Serial Communications and Logging data ##

1. Press 'Refresh port' to get most recent port names in the drop down box

2. Choose Baudrate (default for Temp = 38400, Hum = 9600, Pressure = 9600)

3. Choose logging interval (default is 2 seconds)

4. Press 'Start/Stop' to start plotting

To log data:

5. Choose 'File Directory' for both Temp, Hum

6. Press 'Log All' to start logging data as csv files


To ensure the data is being recorded properly, both logging and start/stop button must be green as shown in screenshot below

![Fig3](https://github.com/IseeJ/TempGUI/blob/main/images/Screenshot3.png?raw=true)




## Additional Information for debugging ##

### Atlas EZO sensors ###
connections from sensor → Board

White: RX → TX-O

Green: TX → RX-I

Black: GND → GND

Red: VCC → 3.3V

Blue: Auto → N/C


### 1. Pressure Logger ###
[EZO-PRS™ Embedded Pressure Sensor](https://atlas-scientific.com/product/pressure-sensor/)

psi (0 – 74.000) Default, atm (0 – 5.03), bar (0 – 5.102), kPa (0 – 510.212)

Only read gauge pressure (relative to atmospheric pressure)

Conversion: $P_{abs} = P_{gauge} + P_{atm}$

$P_{atm}$ = 14.969 psi = 1 atm = 1.01325 bar = 101.325 kPa

conversion to bar then to Torr

```
Line 224: Pressure_bar = float(Pressure_psi)*0.06894757 #convert psi to bar
Line 225: self.latest_reading = (Pressure_bar+self.ATM_P_bar)*750.061683 #convert to Torr
```

Showing pressure in 3 units. plot in Torr:
![Fig4](https://github.com/IseeJ/TempGUI/blob/main/images/Screenshot4.png?raw=true)


- Writing commands: self.ser.write(b'[command]\r\n')

- Commands:
    - check unit: U,?
    - set unit: U,psi U,atm U,bar U,kPa
    - Low point calibration in psi: Cal,0 (before cal: reads 855 Torr at atm, after cal: reads 760 Torr at atm) *7/23/24 edit: reset calibration (use the Hornet gauge as ref which reads 871 Torr)*
    - Restore calibration to factory setting: Cal,clear
      


### 2. Humidity Logger ###
[EZO-PRS™ Embedded Pressure Sensor](https://atlas-scientific.com/probes/humidity-probe/)

0 – 100% RH

- Commands:
    - Enable All 3 readings:
        - O,HUM,1
        - O,T,1
        - O,Dew,1
    - Check of all readings are enabled: O,? --> ?,O,HUM,T,Dew of all anabled



### 3. Temperature Logger ###
#### notes on connection ####
Power on the device before plugging in otherwise serial port won't be recognized.

#### hexadecimal decoding ####
Output: 37 Hex bits for 8 channels
Max temp is 1800, use this to determine when the temperature decoding needed to be swithed to using Two's complement

Read: 01 16 7b 28 48 4c 45 48 54 43 34 30 39 35 68 71 **e3 00 2b 01 00 00 00 00 00 00 00 00 00 00 00 00** c6 29 7d 7e 04

where the first 16 bits and last 4 bits are the same in all T readings, the middle 16 bits represents temperature readings for the 8 channels (2 bits or 4 digits per channel), Temperature is recorded in 4 digits Hexadecimal number read backward (Little endian system: stores the least-significant byte at the smallest address) For example, the conversion between the reading in channel T2 would be, 2b 01 --> 012b --> 299 --> 29.9 degrees Celsius

- - - -
### Water vapor concentration ###

#### RH to AH ####
Absolute Humidity is calcualted using the measured Relative Humidity and Temperature from the EZO-Hum sensor, using the formula:
$AH = 2.16 \cdot \frac{RH\cdot6.11 e^{\left ( \frac{17.27 \cdot T}{T+273.15-35.86} \right )}}{T+273.15}$

when RH is Relative Humidity in % and T is Temperature in degree Celsius

#### AH to ppm ####
...
*I haven't figured out the conversion yet, but to retrieve the AH, temperature, and Pressure value you can obtain data from model (humidity and pressure data are stored in separated models)
```
HUM_time, RH_val,TMP_val,AH_val,DEW_val = self.humidity_model.getData()
Press_time, Press_raw, Press_torr = self.pressure_model.getData()
```

- - - -
### Code structure ###

There are 3 worker threads: 
- Temperature (T1-T8 thermocouples): write commands, read and emits time and 8 temperatures in tuples
- Humidity (RH, Output Temperature, Dew point): emit time and 4 values where Absolute humidity is calculated from RH and Temperature
- Pressure (pressure): emit time and pressure value in psi (raw reading) and torr (calculated)

There are 3 models to store, handle corresponding data emitted

Worker threads handle serial communications, emits data to connected pyqtSlot through self.worker.result.connect(self.updatefunction)

The update function store data in the model and plots them out
  
