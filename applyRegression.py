import numpy as np
import ROOT
import os
from modules.CNNModel import loadCNNModel
from modules.fitFunction import fitFunction, loadResults
from modules.utils import getChannelMap
from modules.runinfo import runinfo, GetFitRange


def applyCNNRegression(model, chans, run, verbose=False, applyCutForWeightPlots=True):
    predictions, weights = model.predict(chans)
    predictions = predictions.astype(np.float64)

    raw = np.sum(chans, axis=(1, 2, 3))

    selection = np.ones(len(raw), dtype=bool)
    if applyCutForWeightPlots:
        try:
            be, atten = runinfo[run]
            try:
                _, _, fitmin, fitmax = GetFitRange(be * 8.0, atten)
                selection = (raw > fitmin) & (raw < fitmax)
            except KeyError:
                print(
                    f"Run {run} with {be*8.0} GeV and attenuation {atten} not found in FitRange")
        except KeyError:
            print(f"Run {run} not found in runinfo")

    weights_sel = weights[selection]
    weights_avg = np.mean(weights_sel, axis=0)
    weights_std = np.std(weights_sel, axis=0)

    if verbose:
        print("weights_avg: ", weights_avg)
        print("weights_std: ", weights_std)

        print("predictions after trainng: ", predictions)
        mu, std = np.mean(predictions), np.std(predictions)
        print(f"mu = {mu}, std = {std}, relative std = {std/mu}")

    return predictions, weights_avg, weights_std


def applyLinearRegression(chans, scales, verbose=False):
    predictions = fitFunction(chans, scales)
    if verbose:
        mu, std = np.mean(predictions), np.std(predictions)
        print(f"mu = {mu}, std = {std}, relative std = {std/mu}")
    return predictions


def Evaluate(run, model=None, scales=None, verbose=False):
    fname = f"root/Run{run}_list.root"
    if not os.path.exists(fname):
        print(f"File {fname} does not exist")
        return

    print("Evaluating Run ", run)
    f = ROOT.TFile(fname)
    t = f.Get("save")
    nentries = t.GetEntries()
    print(f"Number of entries: {nentries}")

    if nentries == 0:
        f.Close()
        print("No entries in the file ", fname)
        return

    chans = np.zeros((nentries, 4, 4, 1), dtype=np.float32)

    for i in range(nentries):
        t.GetEntry(i)
        for j in range(16):
            x, y = getChannelMap(j)
            chans[i][x][y][0] = t.ch_lg[j]

    ofile = ROOT.TFile(f"regressed/Run{run}_list.root", "RECREATE")

    if model:
        print("Applying CNN Regression")
        predictions, weights_avg, weights_std = applyCNNRegression(
            model, chans, run, verbose)

        hweights = ROOT.TH2F("hweights", "Weights", 4, -0.5, 3.5, 4, -0.5, 3.5)
        for i in range(4):
            for j in range(4):
                hweights.SetBinContent(i+1, j+1, weights_avg[i][j])
                hweights.SetBinError(i+1, j+1, weights_std[i][j])
        hweights.Write()

        hcal = ROOT.TH1F("hcal", "Calibrated Energy with CNN", 4000, 0, 8000)
        hcal.FillN(nentries, predictions, np.ones(nentries))
        hcal.Write()

    chans = chans.reshape(nentries, 16)
    if type(scales) is np.ndarray:
        print("Applying Linear Regression")
        predictions_linear = applyLinearRegression(chans, scales, verbose)

        hcal_linear = ROOT.TH1F(
            "hcal_linear", "Calibrated Energy with Linear Regression", 4000, 0, 8000)
        hcal_linear.FillN(nentries, predictions_linear, np.ones(nentries))
        hcal_linear.Write()

    print("Simple sum (uncalibrated) of all channels")
    predictions_unc = fitFunction(chans, np.ones(17))
    hcal_unc = ROOT.TH1F("hcal_unc", "Uncalibrated Energy", 4000, 0, 8000)
    hcal_unc.FillN(nentries, predictions_unc, np.ones(nentries))
    hcal_unc.Write()

    ofile.Close()


if __name__ == "__main__":
    model = loadCNNModel("results/best_model.keras")

    scales = loadResults("results/results_withattu.json")
    scales = np.array(scales)

    from modules.utils import parseRuns
    run_start, run_end = parseRuns()
    for i in range(run_start, run_end):
        Evaluate(i, model, scales)
