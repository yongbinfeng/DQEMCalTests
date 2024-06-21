from modules.fitFunction import fitFunction, loadResults
import numpy as np
import ROOT
import os

scales = loadResults("results.json")
scales = np.array(scales)
print(scales)


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

    chans = np.zeros((nentries, 16))

    for i in range(nentries):
        t.GetEntry(i)
        for j in range(16):
            chans[i][j] = t.ch_lg[j]

    predictions = fitFunction(chans, scales)
    predictions_unc = fitFunction(chans, np.ones(17))

    ofile = ROOT.TFile(f"regressed/Run{run}_list.root", "RECREATE")
    hcal = ROOT.TH1F("hcal", "Calibrated Energy", 600, 0, 14000)
    hcal.FillN(nentries, predictions, np.ones(nentries))
    hcal.Write()

    hcal_unc = ROOT.TH1F("hcal_unc", "Uncalibrated Energy", 600, 0, 14000)
    hcal_unc.FillN(nentries, predictions_unc, np.ones(nentries))
    hcal_unc.Write()

    ofile.Close()


for i in range(500, 510):
    Evaluate(i)
