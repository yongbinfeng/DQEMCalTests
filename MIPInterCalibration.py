# fit different channels using MIP

import ROOT
import os
import numpy as np
from modules.fitFunction import saveResults, runFit, runMIPFit
from modules.runinfo import IsMuonRun, GetTitle, GetMIPFitRange
from modules.utils import plotCh1D, plotChMap, getChannelMap, plotCh2D, parseRuns
from modules.plotStyles import DrawHistos
from collections import OrderedDict

ROOT.gROOT.SetBatch(True)


def RunMuonCalibration(start, end):
    t = ROOT.TChain("save")
    for run in range(start, end+1):
        fname = f"root/Run{run}_list.root"
        if not os.path.exists(fname):
            print(f"File {fname} does not exist")
            continue
        if not IsMuonRun(run):
            print(f"Run {run} is not a muon run")
            continue
        t.Add(fname)

    # use the start as the run number for ploting
    run = start

    nentries = t.GetEntries()
    print(f"Number of entries: {nentries}")

    xmin, xmax, xfitmin, xfitmax = GetMIPFitRange(start)

    histos_hg, _ = plotCh1D(t, run, plotAvg=False, applySel=False,
                            makePlots=False, xmin=xmin, xmax=xmax, xbins=50)
    plotCh2D(t, run, plotAvg=True, applySel=False,
             outdir="plots/MIPCalib/Ch2D")

    means = OrderedDict()
    sigmas = OrderedDict()

    print(f"Fit range: {xmin} {xmax} {xfitmin} {xfitmax}")
    for ch in range(16):
        (mean, mean_err), (sigma, sigma_err) = runMIPFit(histos_hg[ch], f"cal_Run{start}_Run{end}_{ch}",
                                                         xmin=xmin, xmax=xmax, xfitmin=xfitmin, xfitmax=xfitmax, outdir="plots/MIPCalib")
        means[ch] = (mean, mean_err)
        sigmas[ch] = (sigma, sigma_err)

    baseChan = 12
    baseMean = means[baseChan][0]
    baseSigma = sigmas[baseChan][0]
    for ch in range(16):
        means[ch] = (means[ch][0] / baseMean,
                     means[ch][1] / baseMean)
        sigmas[ch] = (sigmas[ch][0] / baseSigma,
                      sigmas[ch][1] / baseSigma)

    h2D_mean = ROOT.TH2D("h2D_mean", "h2D_mean", 4, -0.5, 3.5, 4, -0.5, 3.5)
    h2D_sigma = ROOT.TH2D("h2D_sigma", "h2D_sigma", 4, -0.5, 3.5, 4, -0.5, 3.5)
    hCalib = ROOT.TH1D("hCalib", "hCalib", 16, -0.5, 15.5)

    for ch in range(16):
        x, y = getChannelMap(ch)
        h2D_mean.SetBinContent(x+1, y+1, means[ch][0])
        h2D_mean.SetBinError(x+1, y+1, means[ch][1])
        h2D_sigma.SetBinContent(x+1, y+1, sigmas[ch][0])
        h2D_sigma.SetBinError(x+1, y+1, sigmas[ch][1])

        hCalib.SetBinContent(ch+1, means[ch][0])
        hCalib.SetBinError(ch+1, means[ch][1])

    title = GetTitle(start, end)
    DrawHistos([h2D_sigma], [], -0.5, 3.5, "X", -0.5, 3.5, "Y", f"MIPCalib_Sigma_Run{start}_Run{end}", dology=False, drawoptions="colz,text,ERROR", dologz=False, legendPos=(
        0.15, 0.87, 0.70, 0.97), lheader=title, outdir="plots/MIPCalib", zmin=0.70, zmax=1.20)
    DrawHistos([h2D_mean], [], -0.5, 3.5, "X", -0.5, 3.5, "Y", f"MIPCalib_Mean_Run{start}_Run{end}", dology=False, drawoptions="colz,text,ERROR", dologz=False, legendPos=(
        0.15, 0.87, 0.70, 0.97), lheader=title, outdir="plots/MIPCalib", zmin=0.70, zmax=1.20)

    plotChMap("plots/MIPCalib")

    # save results
    if not os.path.exists("results"):
        os.makedirs("results")
    ofile = ROOT.TFile(
        f"results/MIPCalib_Run{start}_Run{end}.root", "RECREATE")
    h2D_mean.SetDirectory(ofile)
    h2D_mean.Write()
    h2D_sigma.SetDirectory(ofile)
    h2D_sigma.Write()
    hCalib.SetDirectory(ofile)
    hCalib.Write()
    ofile.Close()

    # save results similar to linear regression way
    results = []
    for ch in means.keys():
        results.append(means[ch][0])
    saveResults(results, f"results/MIPCalib_Run{start}_Run{end}.json")


if __name__ == "__main__":
    run_start, run_end = parseRuns()
    RunMuonCalibration(run_start, run_end)
