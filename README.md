# DQEMCalTests

## Installation on MIT's `sqtestbench`

First install miniconda and create an environment in which to install the latest version of ROOT and python3. Installation instructions can be found [here](https://docs.anaconda.com/miniconda/#quick-command-line-install) but are given below:
```
mkdir -p ~/miniconda3
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O ~/miniconda3/miniconda.sh
bash ~/miniconda3/miniconda.sh -b -u -p ~/miniconda3
rm -rf ~/miniconda3/miniconda.sh
```
After installing, initialize the newly-installed Miniconda for either bash or zsh shell:
```
~/miniconda3/bin/conda init bash
~/miniconda3/bin/conda init zsh
```

Now install [ROOT](https://root.cern/install/#conda) inside the miniconda environment:
```
conda config --set channel_priority strict
conda create -c conda-forge --name <my-environment> root
conda activate <my-environment>
```

You are now ready to run the DarkQuest EMCal test scripts below. 

## Running analyses

Steps:
- make ROOT [makeROOT.py](makeROOT.py)
- make selections for electrons for regression [makeSelections.py](makeSelections.py)
- run linear regression or CNN regression [linearRegression.py](linearRegression.py) or [CNNRegression.py](CNNRegression.py)

- If doing linear regression
```
# runs with attenuator
python makeSelections.py --start 496 --end 507
python linearRegression.py --start 496 --end 507
```

- run MIP inter-channel calibrations [MIPInterCalibration.py](MIPInterCalibration.py)
```
# runs with attenuator
python MIPInterCalibration.py --start 521 --end 526
# runs with neutral density filter
python MIPInterCalibration.py --start 614 --end 618
# runs without attenuator or neutral density filter
python MIPInterCalibration.py --start 655 --end 655
```
- apply MIP inter-channel calibrations [applyCorrection.py](applyCorrection.py)
```
# runs with attenuator
python applyCorrection.py -m results/MIPCalib_Run521_Run526.json --start 493 --end 544
# runs with neutral density filter
python applyCorrection.py -m results/MIPCalib_Run614_Run618.json --start 563 --end 612
# runs without attenuator or neutral density filter
python applyCorrection.py -m results/MIPCalib_Run655_Run655.json --start 642 --end 654
```

- run the signal fit to extract the energy resolution and response [runSignalFits.py](runSignalFits.py)
```
# runs with attenuator
python runSignalFits.py --start 493 --end 544
# runs with neutral density filter
python runSignalFits.py --start 563 --end 612
# runs without attenuator or neutral density filter
python runSignalFits.py --start 642 --end 654
```

- plot the energy resolution and response [plotResol.py](plotResol.py)
```
python plotResol.py
```

Side script:
- make plots for 1D and 2D energy deposits per channel, regressed per-channel coefficients [makePlots.py](makePlots.py)
