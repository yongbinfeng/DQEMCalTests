# fit 16D data to 1D data with ROOT

import ROOT
import os
import numpy as np
from scipy.optimize import minimize
from scipy.stats import norm
from modules.fitFunction import fitFunction, saveResults
from modules.runinfo import GetSelectionRange, GetRunInfo, CheckRunExists, GetRegressionGoal, GetTitle
from modules.utils import plotCh1D, plotChMap, getChannelMap, plotCh2D, parseRuns
from modules.plotStyles import DrawHistos

ROOT.gROOT.SetBatch(True)


def ReadInputs(run_start, run_end):
    t = ROOT.TChain("save")
    for run in range(run_start, run_end):
        fname = f"root_selected/Run{run}_list_selected.root"
        if not os.path.exists(fname):
            print(f"File {fname} does not exist")
            continue

        if not CheckRunExists(run):
            print(f"Run {run} does not exist")
            continue

        t.Add(fname)

    nentries = t.GetEntries()
    print(f"Number of entries: {nentries}")

    chans = np.zeros((nentries, 16))

    for i in range(nentries):
        t.GetEntry(i)
        for j in range(16):
            chans[i][j] = t.ch_lg[j]

    return chans


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


def RunLinearRegression(run_start, run_end):
    chans = ReadInputs(run_start, run_end)
    target = GetRegressionGoal(run_start)
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

    # without regression
    predictions_unc = fitFunction(chans, np.ones(17))
    mu_unc, std_unc = norm.fit(predictions_unc)
    print(f"mu_unc = {mu_unc}, std_unc = {std_unc}")

    baseChan = 12
    result.x = result.x / result.x[baseChan]

    # with regression
    predictions_reg = fitFunction(chans_reg, result.x)
    mu_reg, std_reg = norm.fit(predictions_reg)
    print(f"mu_reg = {mu_reg}, std_reg = {std_reg}")

    print(result.x)

    nentries = chans.shape[0]

    # run the predictions
    ofile = ROOT.TFile(
        f"root_selected/Run_list_selected_calibrated_Run{run_start}_{run_end}.root", "RECREATE")
    hcal = ROOT.TH1F("hcal", "Calibrated Energy",
                     200, target-1000, target+1000)
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

    h2D_mean = ROOT.TH2D("h2D_mean", "h2D_mean", 4, -0.5, 3.5, 4, -0.5, 3.5)

    for ch in range(16):
        x, y = getChannelMap(ch)
        h2D_mean.SetBinContent(x+1, y+1, result.x[ch])
        h2D_mean.SetBinError(x+1, y+1, 0)

    title = GetTitle(run_start, run_end)
    DrawHistos([h2D_mean], [], -0.5, 3.5, "X", -0.5, 3.5, "Y", f"LinearRegression_Mean_Run{run_start}_Run{run_end}", dology=False, drawoptions="colz,text,ERROR", dologz=False, legendPos=(
        0.15, 0.87, 0.70, 0.97), lheader=title, outdir="plots/LinearRegression", zmin=0.70, zmax=1.20)

    plotChMap("plots/LinearRegression")

    # save the result to a json file
    saveResults(result.x.tolist(),
                f"results/LinearRegression_Run{run_start}_Run{run_end}.json")


if __name__ == "__main__":
    run_start, run_end = parseRuns()
    RunLinearRegression(run_start, run_end)
