# PREACT
The main results of PREACT are evaluated using a Python framework that simulates the tailoring of data redundancy to the reliability levels of the underlying 
disk layer without compromising target data reliability. Read reference for more details.

## System Requirements
- Any Ubuntu distribution >= 16.04 with access to internet to install packages using `apt-get`.

## Dependencies
PREACT depends on several Python packages (which also include the packages it uses for anomaly and change-point 
detection: read reference for detail). Use the pip3 package manager to install all required dependencies.
```bash
sudo apt-get install python3 python3-pip
pip3 install numpy scipy pandas statsmodels matplotlib boto3 rrcf ruptures pyarrow tqdm dataclasses
```

## Usage
There are several mandatory and optional flags for running PREACT. The best way to learn about all the flags is to run 
the following command.
```bash
python3 ./preact.py --help
```
In the Backblaze dataset, there are totally 7 makes / models. To run with all of them, you can use the following command.
```bash
python3 ./preact.py --method date -c bb -m ST4000DM000 -m ST8000DM002 -m "HGST HMS5C4040ALE640" -m "HGST HMS5C4040BLE640" -m ST8000NM0055 -m ST12000NM0007 -m "HGST HUH721212ALN604" --multi_phase
```
Note that running with all makes / models from the Backblaze dataset will require at least 12-ish minutes. A progress bar will show up to show the progress of PREACT.
At the end of each run, the results (including the plots) are collected in the results folder.


## Confirming results reproducibility
The above simulation produces all graphs that are in Fig. 12 of the submitted draft. The `./results/plots/transition_overload_with_reconstruction.pdf` file should match Fig. 12a. The `./results/plots/rgroups.pdf` should match Fig. 12b. and the rest of the figures in `./results/plots/` should match Fig. 12c--Fig 12i. Even though this graph is in the appendix, it is essentially the performance of PREACT on an entire storage cluster with over 100,000 disks. The other clusters shown in Fig. 1, 5, 6, 10, and 11 belong to Google and the data used for those results in confidential. In case of any confusion, please contact saukad@cs.cmu.edu.


## Configuration
All the configuration settings are in the constants.py file, and do not need to be changed for running this experiment.
