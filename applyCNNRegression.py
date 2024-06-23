import numpy as np
import ROOT
import os
from modules.CNNModel import loadCNNModel
from modules.fitFunction import fitFunction
from modules.utils import getChannelMap


model = loadCNNModel("results/best_model.keras")


def Evaluate(run):
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

    predictions, weights = model.predict(chans)
    print("weight shape: ", weights.shape)
    print("weights ", weights)
    print("avg weights: ", np.mean(weights, axis=0))
    print("prediction avg", np.mean(predictions))
    predictions = predictions.astype(np.float64)

    chans = chans.reshape(nentries, 16)
    predictions_unc = fitFunction(chans, np.ones(17))

    selection = (predictions_unc > 300.0)
    weights_sel = weights[selection]
    weights_avg = np.mean(weights_sel, axis=0)
    print("weights_avg: ", weights_avg)

    print("predictions after trainng: ", predictions)
    mu, std = np.mean(predictions), np.std(predictions)
    print(f"mu = {mu}, std = {std}, relative std = {std/mu}")
    print("predictions with linear sum: ", predictions_unc)
    mu_unc, std_unc = np.mean(predictions_unc), np.std(predictions_unc)
    print(f"mu = {mu_unc}, std = {std_unc}, relative std = {std_unc/mu_unc}")

    ofile = ROOT.TFile(f"regressed/Run{run}_list.root", "RECREATE")

    hweights = ROOT.TH2F("hweights", "Weights", 4, -0.5, 3.5, 4, -0.5, 3.5)
    for i in range(4):
        for j in range(4):
            hweights.Fill(i, j, weights_avg[i][j])
    hweights.Write()

    hcal = ROOT.TH1F("hcal", "Calibrated Energy", 4000, 0, 8000)
    hcal.FillN(nentries, predictions, np.ones(nentries))
    hcal.Write()

    hcal_unc = ROOT.TH1F("hcal_unc", "Uncalibrated Energy", 4000, 0, 8000)
    hcal_unc.FillN(nentries, predictions_unc, np.ones(nentries))
    hcal_unc.Write()

    ofile.Close()


if __name__ == "__main__":
    from modules.utils import parseRuns
    run_start, run_end = parseRuns()
    for i in range(run_start, run_end):
        Evaluate(i)
