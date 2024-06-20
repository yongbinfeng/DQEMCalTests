# fit 16D data to 1D data with ROOT

import ROOT
import numpy as np
from sklearn.linear_model import LinearRegression
from scipy.optimize import minimize
import json

run = 357
fname = f"root_selected/Run{run}_list_selected.root"
f = ROOT.TFile(fname)
t = f.Get("save")
nentries = t.GetEntries()

chans = np.zeros((nentries, 16))
energys = np.zeros(nentries)

for i in range(nentries):
    t.GetEntry(i)
    for j in range(16):
        chans[i][j] = t.ch_lg[j]
        
    energys[i] = ROOT.gRandom.Gaus(3100, 3100*0.000002)
    
def objective(params):
    predictions = np.dot(chans, params[:-1]) + params[-1]
    return np.sum((predictions - energys)**2)

initial_guess = np.ones(17)
# bounds
b = [(0, None) for i in range(16)] + [(-100, 100)]

result = minimize(objective, initial_guess, bounds=b)

print(result.x)

# run the predictions
predictions = np.dot(chans, result.x[:-1]) + result.x[-1]
ofile = ROOT.TFile(f"root_selected/Run{run}_list_selected_calibrated.root", "RECREATE")
hcal = ROOT.TH1F("hcal", "Calibrated Energy", 200, 2500, 4000)
hcal.FillN(nentries, predictions, np.ones(nentries))
hcal.Write()
ofile.Close()

# save the result to a json file
with open("calibration.json", "w") as outfile:
    json.dump(result.x.tolist(), outfile)