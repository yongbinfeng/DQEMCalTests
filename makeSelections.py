import ROOT
import os
import sys

ROOT.gROOT.SetBatch(True)


def select(run):
    fname = f"root/Run{run}_list.root"
    if not os.path.exists(fname):
        print(f"File {fname} does not exist")
        return
    f = ROOT.TFile(fname)
    t = f.Get("save")
    nentries = t.GetEntries()

    # make plots of sum of ch_lg
    from modules.utils import plotChSum, plotCh2D
    plotChSum(t, run)
    plotCh2D(t, run)

    # create a new file
    fout = ROOT.TFile(f"root_selected/Run{run}_list_selected.root", "RECREATE")
    tout = t.CloneTree(0)

    nevts = 0
    for i in range(nentries):
        t.GetEntry(i)
        if sum(t.ch_lg) > 2000 and sum(t.ch_lg) < 4000:
            tout.Fill()
            nevts += 1

    tout.Write()
    fout.Close()
    f.Close()

    print(
        f"Selected {nevts} out of {nentries} events for Run {run}, efficiency = {nevts/(nentries+1e-3):.2f}")


if __name__ == "__main__":
    for i in range(330, 430):
        select(i)
