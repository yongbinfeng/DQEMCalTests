# DQEMCalTests

Steps:
- make ROOT [makeROOT.py](makeROOT.py)
- make selections for electrons for regression [makeSelections.py](makeSelections.py)
- run linear regression or CNN regression [linearRegression.py](linearRegression.py) or [CNNRegression.py](CNNRegression.py)
- apply regression [applyRegression.py](applyRegression.py)
- run fits to get resolution and response [runSignalFits.py](runSignalFits.py)
- run analysis to plot resolution and response [plotResol.py](plotResol.py)

Side script:
- make plots for 1D and 2D energy deposits per channel, regressed per-channel cofficients [makePlots.py](makePlots.py)