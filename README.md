# DQEMCalTests

Steps:
- make ROOT [makeROOT.py](makeROOT.py)
- make selections for electrons for regression [makeSelections.py](makeSelections.py)
- run linear regression or CNN regression [linearRegression.py](linearRegression.py) or [CNNRegression.py](CNNRegression.py)
- apply regression [applyRegression.py](applyRegression.py)
- run fits to get resolution and response [runSignalFits.py](runSignalFits.py)
- run analysis to plot resolution and response [plotResol.py](plotResol.py)

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
python applyCorrection.py -f results/MIPCalib_Run521_Run526.json --start 493 --end 544
# runs with neutral density filter
python applyCorrection.py -f results/MIPCalib_Run614_Run618.json --start 563 --end 612
# runs without attenuator or neutral density filter
python applyCorrection.py -f results/MIPCalib_Run655_Run655.json --start 642 --end 654
```

Side script:
- make plots for 1D and 2D energy deposits per channel, regressed per-channel coefficients [makePlots.py](makePlots.py)