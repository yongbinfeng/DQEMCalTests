import ROOT
import os
import sys

ROOT.gROOT.SetBatch(True)


def makePlot(run):
    fname = f"root/Run{run}_list.root"
    if not os.path.exists(fname):
        print(f"File {fname} does not exist")
        return

    from modules.utils import getEnergy
    energy = getEnergy(run)
    if energy == -1:
        print(f"Run {run} not found in runinfo")
        return

    f = ROOT.TFile(fname)
    t = f.Get("save")

    # make plots of sum of ch_lg
    from modules.utils import plotChSum, plotCh2D
    plotChSum(t, run)
    plotCh2D(t, run)


if __name__ == "__main__":
    from modules.utils import parseRuns
    run_start, run_end = parseRuns()
    for i in range(run_start, run_end):
        makePlot(i)
