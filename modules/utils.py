# collection for all the functions that are used in the main script
import sys
import os
from collections import OrderedDict
from .runinfo import runinfo, GetFitRange, GetEnergy, GetTitle
from .plotStyles import DrawHistos
import ROOT


def plotChSum(t, run, xmin=0, xmax=8000, outdir="plots/ChSum"):
    h = ROOT.TH1F(f"h_Run{run}ChSum", "h", 500, xmin, xmax)
    t.Draw(f"Sum$(ch_lg)>>h_Run{run}ChSum")

    vmax = h.GetMaximum()
    outname = f"Run{run}_sum_ch_lg"

    title = GetTitle(run)

    DrawHistos([h], [], xmin, xmax, "Energy [ADC]", 0.1, vmax * 1e2,
               "Counts", outname, dology=True, outdir=outdir, lheader=title, legendPos=(0.25, 0.85, 0.80, 0.90))


def getChannelMap(chan):
    chanMap = {
        15: (0, 0),
        14: (1, 0),
        13: (0, 1),
        12: (1, 1),
        11: (2, 0),
        10: (3, 0),
        9: (2, 1),
        8: (3, 1),
        7: (0, 2),
        6: (1, 2),
        5: (0, 3),
        4: (1, 3),
        3: (2, 2),
        2: (3, 2),
        1: (2, 3),
        0: (3, 3)
    }
    return chanMap[chan]


def plotChMap(outdir="plots/ChMap"):
    """
    plot the channel map
    """
    h2D = ROOT.TH2F("h_Chs", "h", 4, -0.5, 3.5, 4, -0.5, 3.5)
    for ch in range(16):
        x, y = getChannelMap(ch)
        h2D.Fill(x, y, ch)

    DrawHistos([h2D], [], -0.5, 3.5, "X", -0.5, 3.5, "Y",
               "ChMap", dology=False, drawoptions="text", dologz=False, legendPos=(0.30, 0.87, 0.70, 0.97), lheader="Channel Map", outdir=outdir, zmin=0.0, zmax=15.0, textformat=".0f")


def plotCh2D(t, run, plotAvg=True, applySel=True, outdir="plots/Ch2D", xmin=None, xmax=None):
    # use RDF such that the loop is only needed once
    rdf = ROOT.RDataFrame(t)

    energy = GetEnergy(run)

    if applySel:
        _, atte, hasfilter, _ = runinfo[run]
        _, _, fitmin, fitmax = GetFitRange(energy, atte, hasfilter)
        if xmin is not None:
            fitmin = xmin
        if xmax is not None:
            fitmax = xmax
        # fitmin and fitmax are basically the electron dominated region
        rdf = rdf.Define("ADCSum", "Sum(ch_lg)").Filter(
            f"ADCSum > {fitmin}").Filter(f'ADCSum < {fitmax}')

    nEvents = rdf.Count().GetValue()

    histos = OrderedDict()
    for ch in range(16):
        x, y = getChannelMap(ch)
        rdf = rdf.Define(f"x_{ch}", str(x)).Define(f"y_{ch}", str(
            y)).Define(f"count_{run}_{ch}", f"ch_lg[{ch}]")

        histos[ch] = rdf.Histo2D(
            (f"h_Chs_{run}_{ch}", "h", 4, -0.5, 3.5, 4, -0.5, 3.5), f"x_{ch}", f"y_{ch}", f"count_{run}_{ch}")

    h2D = ROOT.TH2F(f"h_Chs_{run}", "h", 4, -0.5, 3.5, 4, -0.5, 3.5)
    for ch in range(16):
        h2D.Add(histos[ch].GetValue())

    if plotAvg:
        h2D.Scale(1.0 / (nEvents+0.001))

    title = GetTitle(run)

    DrawHistos([h2D], [], -0.5, 3.5, "X", -0.5, 3.5, "Y",
               f"Run{run}_ch_lg_2D", dology=False, drawoptions="colz,text", dologz=True, legendPos=(0.15, 0.87, 0.80, 0.97), lheader=title, outdir=outdir, zmin=1.0, zmax=2e3)


def plotCh1D(t, run, plotAvg=True, applySel=False, makePlots=True, xmin=0, xmax=1000, xbins=100):
    rdf = ROOT.RDataFrame(t)

    energy = GetEnergy(run)

    if applySel:
        _, atte, hasfilter, _ = runinfo[run]
        _, _, fitmin, fitmax = GetFitRange(energy, atte, hasfilter)
        rdf = rdf.Define("ADCSum", "Sum(ch_lg)").Filter(
            f"ADCSum > {fitmin}").Filter(f'ADCSum < {fitmax}')

    nEvents = rdf.Count().GetValue()

    histos_hg = OrderedDict()
    histos_lg = OrderedDict()
    for ch in range(16):
        rdf = rdf.Define(f"ch_hg_{ch}", f"ch_hg[{ch}]").Define(
            f"ch_lg_{ch}", f"ch_lg[{ch}]")
        histos_hg[ch] = rdf.Histo1D(
            (f"h_Chs_hg_{run}_{ch}", "h", xbins, xmin, xmax), f"ch_hg_{ch}")
        histos_lg[ch] = rdf.Histo1D(
            (f"h_Chs_lg_{run}_{ch}", "h", xbins, xmin, xmax), f"ch_lg_{ch}")

    if plotAvg:
        for ch in range(16):
            histos_hg[ch].Scale(1.0 / (nEvents+0.001))
            histos_lg[ch].Scale(1.0 / (nEvents+0.001))

    if makePlots:
        # make the actual plots
        title = GetTitle(run)

        ltitle = ROOT.TLatex(0.20, 0.95, title)
        ltitle.SetNDC()
        ltitle.SetTextFont(42)
        ltitle.SetTextSize(0.04)

        mycolors = [15 + i*5 for i in range(16)]

        DrawHistos([histos_hg[ch].GetValue() for ch in range(16)], [f"Ch {ch}" for ch in range(16)], xmin, xmax, "High Gain ADC", 1e-6, 1e3, "Counts",
                   f"Run{run}_ch_hg_1D", dology=True, outdir="plots/Ch1D/hg", legendPos=(0.35, 0.70, 0.90, 0.90), mycolors=mycolors, extraToDraws=[ltitle], legendNCols=4, addOverflow=True)
        DrawHistos([histos_lg[ch].GetValue() for ch in range(16)], [f"Ch {ch}" for ch in range(16)], xmin, xmax, "Low Gain ADC", 1e-6, 1e3, "Counts",
                   f"Run{run}_ch_lg_1D", dology=True, outdir="plots/Ch1D/lg", legendPos=(0.35, 0.70, 0.90, 0.90), mycolors=mycolors, extraToDraws=[ltitle], legendNCols=4, addOverflow=True)

    for ch in range(16):
        histos_hg[ch] = histos_hg[ch].GetValue()
        histos_hg[ch].SetDirectory(0)
        histos_lg[ch] = histos_lg[ch].GetValue()
        histos_lg[ch].SetDirectory(0)

    return histos_hg, histos_lg


def plotWeight(run):
    """
    plot the weights from the regression.
    works only for regressed files with CNN
    """
    fname = f"regressed/Run{run}_list.root"
    if not os.path.exists(fname):
        print(f"File {fname} does not exist")
        return
    f = ROOT.TFile(fname)
    h2D = f.Get("hweights")
    title = GetTitle(run)
    DrawHistos([h2D], [], -0.5, 3.5, "X", -0.5, 3.5, "Y", f"Run{run}_weights", dology=False, drawoptions="colz,text,ERROR", dologz=False, legendPos=(
        0.25, 0.87, 0.70, 0.97), lheader=title, outdir="plots/Weights", zmin=0.70, zmax=1.10)


def parseRuns():
    import argparse
    parser = argparse.ArgumentParser(description="Make ROOT files")
    parser.add_argument("-s", "--start", type=int,
                        default=369, help="Run number to start")
    parser.add_argument("-e", "--end", type=int,
                        default=695, help="Run number to end")
    args, unknown = parser.parse_known_args()
    run_start, run_end = args.start, args.end
    print(f"Selecting runs from {run_start} to {run_end}")
    return run_start, run_end
