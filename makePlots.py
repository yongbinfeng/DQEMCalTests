from modules.utils import parseRuns, plotWeight, plotChSum, plotCh2D, plotCh1D
from modules.runinfo import IsMuonRun
import ROOT
import os
import sys
ROOT.gROOT.SetBatch(True)


def makePlot(run, doChSum=True, doCh2D=True, doCh1D=False, doWeight=False):
    print("Making plots for run", run)
    if doWeight:
        # only works for regressed files with CNN
        # not on input files
        plotWeight(run)
        return

    fname = f"root/Run{run}_list.root"
    if not os.path.exists(fname):
        print(f"File {fname} does not exist")
        return

    from modules.runinfo import GetEnergy
    energy = GetEnergy(run)
    if energy == None:
        print(f"Run {run} not found in runinfo")
        return

    f = ROOT.TFile(fname)
    t = f.Get("save")

    # make plots of sum of ch_lg
    if doChSum:
        print("plotting sum for run", run, "energy", energy, "GeV")
        plotChSum(t, run)
    if doCh2D:
        print("plotting 2D for run", run, "energy", energy, "GeV")
        plotCh2D(t, run)
    if doCh1D:
        print("plotting 1D for run", run, "energy", energy, "GeV")
        plotCh1D(t, run)


if __name__ == "__main__":
    run_start, run_end = parseRuns()
    for i in range(run_start, run_end):
        makePlot(i, doChSum=True, doCh2D=True, doCh1D=True, doWeight=False)
        # if IsMuonRun(i):
        #    makePlot(i, doChSum=False, doCh2D=False,
        #             doCh1D=True, doWeight=False)
