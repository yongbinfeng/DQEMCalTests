import ROOT
import os
import sys
from modules.runinfo import GetSelectionRange, GetRunInfo, CheckRunExists

ROOT.gROOT.SetBatch(True)


def select(run):
    fname = f"root/Run{run}_list.root"
    if not os.path.exists(fname):
        print(f"File {fname} does not exist")
        return

    if not CheckRunExists(run):
        print(f"Run {run} does not exist")
        return

    be, hasAtten, hasFilter, _ = GetRunInfo(run)
    xmin, xmax = GetSelectionRange(be*8, hasAtten, hasFilter)

    f = ROOT.TFile(fname)
    t = f.Get("save")
    nentries = t.GetEntries()

    # make plots of sum of ch_lg
    from modules.utils import plotChSum, plotCh2D
    plotChSum(t, run, xmin=0.6*xmin, xmax=xmax *
              1.3, outdir="plots/Selections/ChSum")
    plotCh2D(t, run, xmin=xmin, xmax=xmax, outdir="plots/Selections/Ch2D")

    # create a new file
    fout = ROOT.TFile(f"root_selected/Run{run}_list_selected.root", "RECREATE")
    tout = t.CloneTree(0)

    nevts = 0
    for i in range(nentries):
        t.GetEntry(i)
        if sum(t.ch_lg) > xmin and sum(t.ch_lg) < xmax:
            tout.Fill()
            nevts += 1

    tout.Write()
    fout.Close()
    f.Close()

    print(
        f"Selected {nevts} out of {nentries} events for Run {run}, with cut on min sum ch_lg {xmin} and max {xmax}, efficiency = {nevts/(nentries+1e-3):.2f}")


if __name__ == "__main__":
    from modules.utils import parseRuns
    run_start, run_end = parseRuns()
    for i in range(run_start, run_end+1):
        select(i)
