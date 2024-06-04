## Tello Drone Bump Detection (`droneFly`)

Bump Detection in Tello Drones

### Brief Overview of Project Directories:
- `droneFly` - main code where running the drone / collecting data programs are located
  - `main.py` is where the program is run once a suitable drone is connected via Wifi socket
- `data` - csv data of flight data containing state details collected at certain frequency during a flight (default=20) - see History of Development for details on how past files are collected.
- `logs` - console log data of each flight (only started collecting from 2024-05-31)
- `analysis` - miscellaneous scripts for plotting and analysing data (not organised yet)
- `videos` - for certain trials, video recordings were also collected in addition to the flight data
- `sorted_data` - grouped in `gusts`, `bumps` and `control` for this current problem. (Copies of actual data from `data` folder)

[Ignore other directories for now...]