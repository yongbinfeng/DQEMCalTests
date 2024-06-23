# fit 16D data to 1D data with ROOT

import ROOT
import os
import numpy as np
from scipy.optimize import minimize
from scipy.stats import norm
from modules.fitFunction import fitFunction, saveResults

ROOT.gROOT.SetBatch(True)

t = ROOT.TChain("save")
for run in range(513, 514):
    fname = f"root_selected/Run{run}_list_selected.root"
    if not os.path.exists(fname):
        print(f"File {fname} does not exist")
        continue
    t.Add(fname)

# run = 357
# fname = f"root_selected/Run{run}_list_selected.root"
# f = ROOT.TFile(fname)
# t = f.Get("save")
nentries = t.GetEntries()
print(f"Number of entries: {nentries}")

chans = np.zeros((nentries, 16))
energys = np.zeros(nentries)

for i in range(nentries):
    t.GetEntry(i)
    for j in range(16):
        chans[i][j] = t.ch_lg[j]


def runLinearRegression(chans, target):
    nentries = chans.shape[0]
    energys = np.ones(nentries) * target

    def objective(params):
        predictions = fitFunction(chans, params)
        return np.sum(np.abs(predictions - energys))

    initial_guess = np.ones(17)
    b = [(0, None) for i in range(16)] + [(-100, 100)]
    result = minimize(objective, initial_guess, bounds=b)

    return result


def selectEvents(chans, scales):
    predictions = fitFunction(chans, scales)
    mu, std = norm.fit(predictions)
    print(f"mu = {mu}, sigma = {std}")
    selection = ((predictions > mu - 2.0*std) & (predictions < mu + 3.0*std))
    return selection, mu


target = 3100.0 * 0.3
chans_reg = chans.copy()
for i in range(20):
    print("Iteration ", i+1)
    result = runLinearRegression(chans_reg, target)
    selection, _ = selectEvents(chans_reg, result.x)
    chans_reg = chans_reg[selection]
    print("Number of selected events: ", chans_reg.shape[0])

predictions = fitFunction(chans, result.x)
mu, std = norm.fit(predictions)
print(f"mu = {mu}, std = {std}")

predictions_unc = fitFunction(chans, np.ones(17))
mu_unc, std_unc = norm.fit(predictions_unc)
print(f"mu_unc = {mu_unc}, std_unc = {std_unc}")

predictions_reg = fitFunction(chans_reg, result.x)
mu_reg, std_reg = norm.fit(predictions_reg)
print(f"mu_reg = {mu_reg}, std_reg = {std_reg}")

print(result.x)

# run the predictions
ofile = ROOT.TFile(
    f"root_selected/Run_list_selected_calibrated.root", "RECREATE")
hcal = ROOT.TH1F("hcal", "Calibrated Energy", 200, target-1000, target+1000)
hcal.FillN(nentries, predictions, np.ones(nentries))
hcal.Write()
hcal_unc = ROOT.TH1F("hcal_unc", "Uncalibrated Energy",
                     200, target-1000, target+1000)
hcal_unc.FillN(nentries, predictions_unc, np.ones(nentries))
hcal_unc.Write()
hcal_reg = ROOT.TH1F("hcal_reg", "Calibrated Energy (Reg)",
                     200, target-1000, target+1000)
hcal_reg.FillN(chans_reg.shape[0], predictions_reg,
               np.ones(chans_reg.shape[0]))
hcal_reg.Write()
ofile.Close()

# save the result to a json file

saveResults(result.x.tolist(), "results/results_withattu.json")
