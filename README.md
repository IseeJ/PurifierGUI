# TempGUI
GUI for temperature and humidity monitoring in LAr purifier (for Omega logger and EZO Atlas sensors)

Updated on 7/18/24: Use the **GUIfinal.py in MostRecentEdit branch**

On the PC:

Open powershell from Anaconda navigator

```
$cd .\Desktop\TempGUI\GUIfinal\
$python .\GUIfinal.py
```

** Connecting Serial Communications and Logging data**

1. Press 'Refresh port' to get most recent port names in the drop down box

2. Choose Baudrate (default for Temp = 38400, Hum = 9600, Pressure = 9600)

3. Choose logging interval (default is 2 seconds)

4. Press 'Start/Stop' to start plotting

To log data:

5. Choose 'File Directory' for both Temp, Hum

6. Press 'Log Both' to start logging data as csv files

*for Pressure logging, since the reading is still off, the logging is separated, it has to be configured in its tab.


To ensure the data is being recorded properly, both start logging and start/stop button must be green as shown in screenshot below

![Fig1](https://github.com/IseeJ/TempGUI/blob/MostRecentEdit/GUI.png?raw=true)
