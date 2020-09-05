# PREACT
PREACT is a Python framework that simulates the tailoring of data redundancy to the reliability levels of the underlying 
disk layer without compromising target data reliability. Read reference for more details.

## Dependencies
PREACT depends on several Python packages (which also include the packages it uses for anomaly and change-point 
detection: read reference for detail). Use the pip3 package manager to install all required dependencies.
```bash
sudo apt-get install python3 python3-pip
pip3 install numpy scipy pandas statsmodels matplotlib boto3 rrcf ruptures pyarrow tqdm
```

## Usage
There are several mandatory and optional flags for running HeART. The best way to learn about all the flags is to run 
the following command.
```bash
python3 ./heart.py --help
```
In the Backblaze dataset, there are totally 7 makes / models. To run with all of them, you can use the following command.
```bash
python3 ./heart.py --method date -c bb -m ST4000DM000 -m ST8000DM002 -m "HGST HMS5C4040ALE640" -m "HGST HMS5C4040BLE640" -m ST8000NM0055 -m ST12000NM0007 -m "HGST HUH721212ALN604" -c bb --multi_phase
```
Note that running with all makes / models from the Backblaze dataset will require at least 12-ish minutes. A progress bar will show up to show the progress of PREACT.
At the end of each run, the results (including the plots) are collected in the results folder. 

## Configuration
All the configuration settings are in the constants.py file.
